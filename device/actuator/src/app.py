import os, sys, logging, configparser, time
import redis

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
        print("alert system active von Redis: " + self._redis.get(REDIS_ALERT_SYSTEM_ACTIVE) + " variable: " + str(system_active))

        try:
            while True:
                if self._is_alert_system_active():
                    if self._is_alert_enabled():
                        # LED soll rot blinken
                        pass
                    else:
                        # LED soll grün leuchten
                        pass
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
