import os, sys, logging, configparser, time
import redis

REDIS_ALERT_SYSTEM_ACTIVE = "system:active"
REDIS_ALERT_ENABLED = "alert:enabled"

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
        system_active = self._redis.get(REDIS_ALERT_SYSTEM_ACTIVE) != 0
        if system_active is None:
            system_active = True
            self._redis.set(REDIS_ALERT_SYSTEM_ACTIVE, "1")

        try:
            while system_active:
                alert_enabled = self._redis.get(REDIS_ALERT_ENABLED) != "0"

                if alert_enabled:
                    self._logger.info("Alarm ist an. Um ihn zu deaktivieren schalte das Alarmsystem ab.")

                elif not alert_enabled:
                    if self.is_alert():
                        self._logger.info("Alarm wurde ausgelöst.")
                        self._redis.set(REDIS_ALERT_ENABLED, "1")
                    else:
                        self._logger.info("Alles ist sicher. Es wurde kein Alarm ausgelöst.")

                else:
                    self._logger.info("Problem bei Alarmierungslogik aufgetreten.")

                time.sleep(10)

        except KeyboardInterrupt:
            pass


    def is_alert(self):
        enable_alert = False
        # Hier Logik, die entscheidet, ob ein Alarm ausgelöst wird, bspw. Sensor 1 = 1 and Sensor 2 = 1
        self._logger.info("Prüfe, ob ein Alarm ausgelöst wird...")

        return enable_alert



if __name__ == "__main__":
    configfile = "app.conf"

    if len(sys.argv) > 1:
        configfile = sys.argv[1]

    app = App(configfile)
    app.main()
