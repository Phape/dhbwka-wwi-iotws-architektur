import os, sys, logging, configparser, time
import redis
import RPi.GPIO as GPIO

LED_ROT = 24
LED_GRUEN = 23
Buzzer_PIN = 25 

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_ROT, GPIO.OUT, initial= GPIO.LOW)
GPIO.setup(LED_GRUEN, GPIO.OUT, initial= GPIO.LOW)
GPIO.setup(Buzzer_PIN, GPIO.OUT, initial= GPIO.LOW)

REDIS_ALERT_SYSTEM_ACTIVE = "system:active" # Für grüne LED
REDIS_ALERT_ENABLED = "alert:enabled" # Für rote LED + Lautsprecher
# REDIS_KEY_MEASUREMENT_VALUES   = "measurement:values"

class App:
    def __init__(self, configfile):
        """
        Konstruktor. Liest die Konfigurationsdatei ein und stellt eine Verbindung
        zur Redis-Datenbank her.
        """
        # Logger konfigurieren
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.INFO)

        formatter = logging.Formatter("[%(asctime)s] %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)


        # Konfigurationsdatei einlesen
        self._logger.info("Lese Konfigurationsdatei app.conf")
        self._config = configparser.ConfigParser(interpolation=None)
        self._config.read(configfile)

        # Verbindung zur Redis-Datenbank herstellen
        redis_config = {
            "host": os.getenv("REDIS_HOST") or self._config["redis"]["host"],
            "port": os.getenv("REDIS_PORT") or self._config["redis"]["port"],
            "db": os.getenv("REDIS_DB") or self._config["redis"]["db"],
        }

        redis_config["port"] = int(redis_config["port"])
        redis_config["db"] = int(redis_config["db"])

        self._logger.info(
            "Stelle Verbindung zu Redis her: host=%(host)s, port=%(port)s, db=%(db)s"
            % redis_config
        )
        self._redis = redis.Redis(decode_responses=True, **redis_config)

    def main(self):
        system_active = self._is_alert_system_active()
        #print("alert system active von Redis: " + self._redis.get(REDIS_ALERT_SYSTEM_ACTIVE) + " variable: " + str(system_active))

        try:
            while True:
                if self._is_alert_system_active():
                    if self._is_alert_enabled():
                        # LED soll rot leuchten
                         GPIO.output(LED_GRUEN,GPIO.LOW) #LED gruen wird ausgeschaltet
                         GPIO.output(LED_ROT,GPIO.HIGH) #LED rot wird eingeschaltet
                         GPIO.output(Buzzer_PIN,GPIO.HIGH) #Buzzer geht an
                         self._logger.info("Alarm aktiviert LED leuchtet rot")
                    else:
                        # LED soll grün leuchten
                         GPIO.output(Buzzer_PIN,GPIO.LOW) #Buzzer geht aus
                         GPIO.output(LED_ROT,GPIO.LOW) #LED rot wird ausgeschaltet
                         GPIO.output(LED_GRUEN,GPIO.HIGH) #LED gruen wird eingeschaltet
                         self._logger.info("Alarmsystem aktiviert LED leuchtet gruen ")
                else:
                    GPIO.output(LED_GRUEN,GPIO.LOW) #LED gruen wird ausgeschaltet
                time.sleep(10)
                

        except KeyboardInterrupt:
            pass


    def _is_alert_enabled(self):
        """Prüft, ob der Alarm bereits ausgelöst ist.

        Returns:
            bool: Wahr, wenn der Alarm bereits aktiv ist
        """
        if self._redis.get(REDIS_ALERT_ENABLED) == "1":
            return True
        else:
            return False


    def _is_alert_system_active(self):
        """Prüft, ob das Alarmsystem scharfgestellt ist.

        Returns:
            bool: Wahr, wenn das Alarmsystem aktiviert ist.
        """
        if self._redis.get(REDIS_ALERT_SYSTEM_ACTIVE) == "1":
            return True
        else:
            return False


if __name__ == "__main__":
    configfile = "app.conf"

    if len(sys.argv) > 1:
        configfile = sys.argv[1]

    app = App(configfile)
    app.main()
