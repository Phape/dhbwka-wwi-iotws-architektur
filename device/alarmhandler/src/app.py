import os, sys, logging, configparser, time
import redis

REDIS_ALERT_SYSTEM_ACTIVE = "system:active"
REDIS_ALERT_ENABLED = "alert:enabled"
REDIS_KEY_MEASUREMENT_VALUES   = "measurement:values"

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
        self._redis.set(REDIS_ALERT_SYSTEM_ACTIVE, "1") # For debugging
        system_active = self._is_alert_system_active()
        print("alert system active von Redis: " + self._redis.get(REDIS_ALERT_SYSTEM_ACTIVE) + " variable: " + str(system_active))

        try:
            while True:
                if system_active:
                    self._system_active_cycle()
                else:
                    self._logger.info("System ist inaktiv. Zum aktivieren " + REDIS_ALERT_SYSTEM_ACTIVE + " auf 1 setzen.")

                time.sleep(10)

        except KeyboardInterrupt:
            pass

    
    def _system_active_cycle(self):
        # self._redis.set(REDIS_ALERT_ENABLED, "0") # For debugging
        alert_enabled = self._is_alert_enabled()
        print("alert enabled von Redis: " + self._redis.get(REDIS_ALERT_ENABLED) + " variable: " + str(alert_enabled))

        if alert_enabled:
            self._logger.info("Alarm ist an. Um ihn zu deaktivieren setze " + REDIS_ALERT_ENABLED + " auf 0.")
        elif not alert_enabled:
            if self._is_alert():
                self._logger.info("Alarm wurde ausgelöst.")
                self._redis.set(REDIS_ALERT_ENABLED, "1")
            else:
                self._logger.info("Alles ist sicher. Es wurde kein Alarm ausgelöst.")
                self._redis.set(REDIS_ALERT_ENABLED, "0")

        else:
            self._logger.info("Problem bei Alarmierungslogik aufgetreten.")


    def _is_alert(self):
        """Entscheidet, ob ein Alarm ausgelöst werden soll.

        Returns:
            bool: Wahr, wenn ein Alarm ausgelöst werden soll
        """
        enable_alert = False

        # Hier Logik, die entscheidet, ob ein Alarm ausgelöst wird, bspw. Sensor 1 = 1 and Sensor 2 = 1
        self._logger.info("Prüfe, ob ein Alarm ausgelöst wird...")
        if self._is_camera_recognized_person() and self._is_movement_detected():
            self._logger.info("Kamera hat Person(en) erkannt und Bewegung wurde erkannt. Alarm wird aktiviert.")
            enable_alert = True

        return enable_alert


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

    def _is_camera_recognized_person(self):
        last_measurements = self._redis.xrevrange(name=REDIS_KEY_MEASUREMENT_VALUES, min="-", max="+", count=5)

        VALUES_INDEX = 1
        for entry in last_measurements:
            if "persons" in entry[VALUES_INDEX]:
                numer_of_persons = int(entry[VALUES_INDEX]["persons"])
                return True if numer_of_persons > 0 else False

    def _is_movement_detected(self):
        last_measurements = self._redis.xrevrange(name=REDIS_KEY_MEASUREMENT_VALUES, min="-", max="+", count=5)

        VALUES_INDEX = 1
        for entry in last_measurements:
            if "movement" in entry[VALUES_INDEX]:
                movement_detected = int(entry[VALUES_INDEX]["movement"])
                return True if movement_detected > 0
        return False
    
if __name__ == "__main__":
    configfile = "app.conf"

    if len(sys.argv) > 1:
        configfile = sys.argv[1]

    app = App(configfile)
    app.main()
