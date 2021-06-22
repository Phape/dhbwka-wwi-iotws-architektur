#! /bin/env python

import redis
import configparser, logging, pprint, os, random, sys, time, cv2, platform
import numpy as np

REDIS_KEY_MEASUREMENT_INTERVAL = "measurement:interval"
REDIS_KEY_MOVEMENT_DETECTED  = "measurement:enabled"
REDIS_KEY_MEASUREMENT_VALUES   = "measurement:values"
#TODO: Confidence in Redis hinterlegen
#REDIS_KEY_MEASUREMENT_CONFIDENCE = "measurement:confidence"

class CameraDevice():
    
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        ret, frame = self.cap.read()
        if not ret:
            print('Failed to open default camera. Exiting...')
            sys.exit()
        self.cap.set(3, 640)
        self.cap.set(4, 480)

    def rotate(self, frame):
        flip = True
        if flip:
            (h, w) = frame.shape[:2]
            center = (w/2, h/2)
            M = cv2.getRotationMatrix2D(center, 180, 1.0)
            frame = cv2.warpAffine(frame, M, (w, h))
        return frame

    def get_latest_frame(self):
        ret, frame = self.cap.read()
        return self.rotate(frame)

    def save_jpeg_frame(self):
        encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), 90)
        frame = self.get_latest_frame()
        cv2.imwrite('current.jpg', frame, encode_param)

class CaffeModelLoader:	
    @staticmethod
    def load(proto, model):
    	net = cv2.dnn.readNetFromCaffe(proto, model)
    	return net
 
class FrameProcessor:	
    def __init__(self, size, scale, mean):
    	self.size = size
    	self.scale = scale
    	self.mean = mean
        
    def get_blob(self, frame):
        img = frame
        (h, w, c) = frame.shape
        if w>h :
            dx = int((w-h)/2)
            img = frame[0:h, dx:dx+h]
        
        resized = cv2.resize(img, (self.size, self.size), cv2.INTER_AREA)
        blob = cv2.dnn.blobFromImage(resized, self.scale, (self.size, self.size), self.mean)
        return blob

class SSD:	

    def __init__(self, frame_proc, ssd_net):
        self.proc = frame_proc
        self.net = ssd_net
    
    def detect(self, frame):
        blob = self.proc.get_blob(frame)
        self.net.setInput(blob)
        detections = self.net.forward()
    	# detected object count
        k = detections.shape[2]
        obj_data = []
        for i in np.arange(0, k):
            obj = detections[0, 0, i, :]
            obj_data.append(obj)
        
        return obj_data
 
    def get_object(self, frame, data):
        confidence = int(data[2]*100.0)
        (h, w, c) = frame.shape
        r_x = int(data[3]*h)
        r_y = int(data[4]*h)
        r_w = int((data[5]-data[3])*h)
        r_h = int((data[6]-data[4])*h)
        
        if w>h :
            dx = int((w-h)/2)
            r_x = r_x+dx
        
        obj_rect = (r_x, r_y, r_w, r_h)
    	
        return (confidence, obj_rect)
    	
    def get_objects(self, frame, obj_data, class_num, min_confidence):
        objects = []
        for (i, data) in enumerate(obj_data):
            obj_class = int(data[1])
            obj_confidence = data[2]
            if obj_class==class_num and obj_confidence>=min_confidence :
                obj = self.get_object(frame, data)
                objects.append(obj)
        return objects

class App:
    """
    Python-Skript zur Erkennung von Personen und Ablage
    dieser in einer Redis-Datenbank. Das Skript liest die Konfigurationsdatei `app.conf`
    ein, um herauszufinden, was es tun soll. Die Messwerte werden als Stream in der
    Datenbank abgelegt. Zusätzlich können durch entsprechende Einträge in der Datenbank
    die Messung aus der Ferne unterbrochen sowie das Messintervall überschrieben werden.
    """

    def __init__(self, configfile,camera_device):
        """
        Konstruktor. Liest die Konfigurationsdatei ein und stellt eine Verbindung
        zur Redis-Datenbank her.
        """

        self.camera_device = camera_device

        # Logger konfigurieren
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.INFO)
    
        formatter = logging.Formatter("[%(asctime)s] %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        self._pp = pprint.PrettyPrinter(indent=4)

        # Konfigurationsdatei einlesen
        self._logger.info("Lese Konfigurationsdatei app.conf")
        self._config = configparser.ConfigParser(interpolation=None)
        self._config.read(configfile)

        # Verbindung zur Redis-Datenbank herstellen
        redis_config = {
            "host": os.getenv("REDIS_HOST") or self._config["redis"]["host"],
            "port": os.getenv("REDIS_PORT") or self._config["redis"]["port"],
            "db":   os.getenv("REDIS_DB")   or self._config["redis"]["db"],
        }

        redis_config["port"] = int(redis_config["port"])
        redis_config["db"]   = int(redis_config["db"])

        self._logger.info("Stelle Verbindung zu Redis her: host=%(host)s, port=%(port)s, db=%(db)s" % redis_config)
        self._redis = redis.Redis(decode_responses=True, **redis_config)

        # Voreingestelltes Messintervall
        self._interval_seconds = float(os.getenv("INTERVAL_SECONDS") or self._config["measurement"]["interval_seconds"])

        # Objecterkennungsmodell Laden
        proto_file = r"./mobilenet.prototxt"
        model_file = r"./mobilenet.caffemodel"
        self.ssd_net = CaffeModelLoader.load(proto_file, model_file)
        self._logger.info("Caffe model geladen: "+model_file)


    def main(self):
        """
        Hauptverarbeitung des Skripts. Startet eine Endlosschleife zur Messung der
        Daten und Speicherung in der Redis-Datenbank.
        """
        try:
            while True:
                if self._is_movement_detected():
                    measurement = self._perform_measurement()
                    self._save_measurement(measurement)

                interval_seconds = self._read_measurement_interval()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            pass
        
    def _is_movement_detected(self):
        last_measurements = self._redis.xrevrange(name=REDIS_KEY_MEASUREMENT_VALUES, min="-", max="+", count=5)

        VALUES_INDEX = 1
        for entry in last_measurements:
            if "movement" in entry[VALUES_INDEX]:
                movement_detected = int(entry[VALUES_INDEX]["movement"])
                if movement_detected > 0 :
                    return True
        return False

    def _read_measurement_interval(self):
        """
        Liest den Eintrag REDIS_KEY_MEASUREMENT_INTERVAL in Redis mit der Anzahl Sekunden
        zwischen zwei Messungen. Fehlt der Eintrag, wird der in self._interval_seconds
        hinterlegte, zuletzt bekannte Werte verwendet.
        """
        interval_seconds = self._redis.get(REDIS_KEY_MEASUREMENT_INTERVAL)

        if interval_seconds == None:
            return self._interval_seconds

        interval_seconds = float(interval_seconds)

        if not interval_seconds == self._interval_seconds:
            self._interval_seconds = interval_seconds
            self._logger.info("Neues Messintervall: %s Sekunde(n)" % interval_seconds)
        
        return interval_seconds

    def _perform_measurement(self):
        """
        Misst einen neuen Sensorwert und gibt ihn zurück. Diese Methode muss am
        besten so angepasst werden, dass alle Sensoren ausgelesen und das Ergebnis
        als Dictionary zurückgegeben wird. Das Dictionariy wird dann in der Methode
        `save_measurement()` unverändert in Redis gespeichert.
        """
        self._logger.info("Starte neue Messung")

        proc_frame_size = 300

        # frame processor for MobileNet
        ssd_proc = FrameProcessor(proc_frame_size, 1.0/127.5, 127.5)
        person_class = 15
 
        ssd = SSD(ssd_proc, self.ssd_net)
 
        #Bild der PiCamera auslesen
        camera_device.save_jpeg_frame()
        image = cv2.imread("./current.jpg")
        
        #Durchführung der Objekterkennung
        obj_data = ssd.detect(image)
        persons = ssd.get_objects(image, obj_data, person_class, 0.85)
        self._logger.info("Person count on the image: "+str(len(persons)))

        #Erkannter Mensch führt zum Abspeichern des Bildes in
        if len(persons) != 0:
            timestr = time.strftime("%c", time.localtime())
            img_name = "/data/" + timestr + ".jpg"
            encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), 90)
            cv2.imwrite(img_name, image, encode_param)

        return {
            "persons": len(persons)
        }


    def _save_measurement(self, measurement):
        """
        Speichert das Ergebnis einer Messung in der Redis-Datenbank, indem dem
        Stream REDIS_KEY_MEASUREMENT_VALUES ein neuer Eintrag hinzugefügt wird.
        Die Messwerte müssen hierfür als Dictionary übergeben werden.
        """
        self._logger.info("Speichere Messwerte: %s" % self._pp.pformat(measurement))
        self._redis.xadd(REDIS_KEY_MEASUREMENT_VALUES, measurement)

def checkDeviceReadiness():
    if not os.path.exists('/dev/video0') and platform.system() == 'Linux':
        print('Video device is not ready')
        print('Trying to load bcm2835-v4l2 driver...')
        os.system('bash -c "modprobe bcm2835-v4l2"')
        time.sleep(1)
        sys.exit()
    else:
        print('Video device is ready')

if __name__ == "__main__":
    configfile = "app.conf"
    checkDeviceReadiness()

    if len(sys.argv) > 1:
        configfile = sys.argv[1]
    camera_device = CameraDevice()
    app = App(configfile, camera_device)
    app.main()