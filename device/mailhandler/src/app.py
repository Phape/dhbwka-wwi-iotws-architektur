import smtplib, ssl
from socket import gaierror
import os, sys, logging, configparser, time, datetime
import redis

REDIS_ALERT_ENABLED = "alert:enabled"
REDIS_LAST_MAIL_ALERT_TIME = "alert:last"
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

        # Mailserver konfigurieren
        self._mail_server_config = {
            "port": os.getenv("MAIL_PORT") or self._config["mail_server"]["port"],
            "host": os.getenv("MAIL_SMTP_SERVER")
            or self._config["mail_server"]["host"],
            "from_addr": os.getenv("MAIL_FROM")
            or self._config["mail_server"]["from_addr"],
            "to_addrs": os.getenv("MAIL_TO") or self._config["mail_server"]["to_addrs"],
            "user": os.getenv("MAIL_USER") or self._config["mail_server"]["user"],
            "password": os.getenv("MAIL_PWD")
            or self._config["mail_server"]["password"],
        }

        self._mail_server_config["port"] = int(self._mail_server_config["port"])

        self._logger.info(
            "Mail Server Konfiguration: host=%(host)s, port=%(port)s, from_addr=%(from_addr)s, to_addrs=%(to_addrs)s, user=%(user)s, password=**not_shown**"
            % self._mail_server_config
        )

    def main(self):
        try:
            while True:
                alert_enabled = self._is_alert_enabled()

                if self._redis.get(REDIS_LAST_MAIL_ALERT_TIME) is None:
                    self._logger.info("Keine letze Alarm-Mail-Zeit gefunden. Benachrichtige Nutzer per Mail.")
                    self._send_mail() # Parametrisieren, Hier Mail schicken, dass Alarmanlage in Betrieb ist
                    self._redis.set(REDIS_LAST_MAIL_ALERT_TIME, time.time())

                last_alert_time = float(self._redis.get(REDIS_LAST_MAIL_ALERT_TIME))
                self._logger.info("Letzte Alarmierung per Mail: " + datetime.datetime.utcfromtimestamp(last_alert_time).isoformat())

                if alert_enabled and time.time() - last_alert_time > 3600: # alarm cooldown: 1h
                    self._logger.info("Alarm ist " + alert_enabled + ", Mail wird versendet.")
                    self._send_mail()
                    self._redis.set(REDIS_LAST_MAIL_ALERT_TIME, time.time())
                else: 
                    time.sleep(10)
        except KeyboardInterrupt:
            pass


    def _is_alert_enabled(self):
        """Prüft, ob der Alarm ausgelöst ist

        Returns:
            bool: Wahr, wenn der Alarm ausgelöst ist
        """
        if self._redis.get(REDIS_ALERT_ENABLED) == "1":
            return True
        else:
            return False


    def _send_mail(self):
        message = """\
        Subject: Hallo
        Diese Nachricht wurde mit Python gesendet."""

        try:
            # context = ssl.create_default_context()
            with smtplib.SMTP(
                self._mail_server_config["host"], self._mail_server_config["port"]
            ) as server:
                # server.starttls(context=context)
                server.login(
                    self._mail_server_config["user"],
                    self._mail_server_config["password"],
                )
                server.sendmail(
                    self._mail_server_config["from_addr"],
                    self._mail_server_config["to_addrs"],
                    message,
                )

            self._logger.info("Gesendet")

        except (gaierror, ConnectionRefusedError):
            self._logger.warn(
                "Verbindung zum Server fehlgeschlagen. Sind alle Verbindungseinstellungen korrekt?"
            )
        except smtplib.SMTPServerDisconnected:
            self._logger.warn(
                "Verbindung zum Server fehlgeschlagen. Falscher Nutzer/Passwort?"
            )
        except smtplib.SMTPException as e:
            self._logger.warn("SMTP Error: " + str(e))


if __name__ == "__main__":
    configfile = "app.conf"

    if len(sys.argv) > 1:
        configfile = sys.argv[1]

    app = App(configfile)
    app.main()
