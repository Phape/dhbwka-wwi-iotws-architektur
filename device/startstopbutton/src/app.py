#! /bin/env python

import redis, RPi.GPIO as GPIO
import configparser, logging, os, time, sys

REDIS_ALERT_SYSTEM_ACTIVE = "system:active"
REDIS_ALERT_ENABLED = "alert:enabled"

class App:
    """
    Hilfsprogramm, das einen am Raspberry Pi angeschlossenen Button überwacht, mit
    dem die periodischen Messungen ausgesetzt werden können. Hierfür wird einfach
    bei jedem Druck auf den Button ein Wert in der Redis-Datenbank getoggelt.
    """
    pin_clk = 0
    pin_dt = 0
    pin_button = 0
    PIN_CLK_LETZTER = 0
    PIN_CLK_AKTUELL = 0

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
            "db":   os.getenv("REDIS_DB")   or self._config["redis"]["db"],
        }

        redis_config["port"] = int(redis_config["port"])
        redis_config["db"]   = int(redis_config["db"])

        self._logger.info("Stelle Verbindung zu Redis her: host=%(host)s, port=%(port)s, db=%(db)s" % redis_config)
        self._redis = redis.Redis(decode_responses=True, **redis_config)

        self.pin_clk       = os.getenv("BUTTON_CLK")           or self._config["button"]["PIN_CLK"]
        self.pin_dt        = os.getenv("BUTTON_DT")           or self._config["button"]["PIN_DT"]
        self.pin_button    = os.getenv("BUTTON_PIN")           or self._config["button"]["BUTTON_PIN"]

        #bounce_millis = int(bounce_millis)
        self.pin_clk = int(self.pin_clk)
        self.pin_dt = int(self.pin_dt)
        self.pin_button = int(self.pin_button)

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.pin_clk, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.pin_dt, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.pin_button, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        # Initiales Auslesen des Pin_CLK
        self.PIN_CLK_LETZTER = GPIO.input(self.pin_clk)

    def main(self):
        """
        Hauptverarbeitung des Skripts. Initialisiert den GPIO und startet eine
        Endlosschleife, um das Programm am Laufen zu halten.
        """

        GPIO.add_event_detect(self.pin_clk, GPIO.BOTH, callback=self._change_system_state, bouncetime=50)
        GPIO.add_event_detect(self.pin_button, GPIO.FALLING, callback=self._deactivate_alert, bouncetime=50)
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            pass
        finally:
            self._logger.info("Räume GPIO auf")
            GPIO.cleanup()
    
    
    def _change_system_state(self, null):

        PIN_CLK_AKTUELL = GPIO.input(self.pin_clk)
        
        if PIN_CLK_AKTUELL != self.PIN_CLK_LETZTER:

            if GPIO.input(self.pin_dt) != PIN_CLK_AKTUELL:
                Richtung = True
            else:
                Richtung = False
            
            if Richtung:
                self._logger.info("Alarmsystem deaktiviert")
                self._redis.set(REDIS_ALERT_SYSTEM_ACTIVE, "0")
            else:
                self._logger.info("Alarmsystem aktiviert")
                self._redis.set(REDIS_ALERT_SYSTEM_ACTIVE, "1")

            
    def _deactivate_alert(self, null):
        if self._is_alert_enabled():
            self._logger.info("Alarm deaktiviert!")
            self._redis.set(REDIS_ALERT_ENABLED, "0")
        else:
            self._logger.info("Alarm bereits deaktiviert!")
   

    def _is_alert_enabled(self):
        """Prüft, ob der Alarm bereits ausgelöst ist.
        Returns:
            bool: Wahr, wenn der Alarm bereits aktiv ist
        """
        if self._redis.get(REDIS_ALERT_ENABLED) == "1":
            return True
        else:
            return False
    

if __name__ == "__main__":
    configfile = "app.conf"

    if len(sys.argv) > 1:
        configfile = sys.argv[1]

    app = App(configfile)
    app.main()
