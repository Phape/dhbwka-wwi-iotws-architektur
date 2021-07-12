# Mailversand

## Beschreibung

Dieses Programm sendet eine E-Mail, wenn ein Alarm ausgelöst wurde.
Falls der Alarm durch die Kamera ausgelöst wurde, wird ein Bild angehängt.

## Auslösen des Mailversands

Die Versand wird ausgelöst, wenn ein Alarm ausgelöst wurde.
`REDIS_ALERT_SYSTEM_ACTIVE` und `REDIS_ALERT_ENABLED` müssen hierzu aktiv sein.
Des weiteren gibt es einen Cooldown, der den Versand von E-Mails auf 1 pro Stunde begrenzt.
Der Timestamp des letzten Mailversands wird in Redis gespeichert. Siehe Variable im Code: `REDIS_LAST_MAIL_ALERT_TIME`

## Umgebungsvariablen

Folgende Umgebungsvariablen sollten in der `docker-compose.yml` gesetzt werden:

* `REDIS_HOST`: Hostname des lokalen Redis-Servers
* `REDIS_PORT`: Portnummer des lokalen Redis-Servers
* `REDIS_DB`: Datenbanknummer des lokalen Redis-Servers
* `MAIL_PORT`: Port des Mailservers (Bspw. 587 für Starttls)
* `MAIL_SMTP_SERVER`: Hostadresse des SMTP-Servers
* `MAIL_FROM`: E-Mail-Adresse des Absenders
* `MAIL_TO`: E-Mail-Adresse des Empfängers
* `MAIL_USER`: Benutzername des Absenders
* `MAIL_PWD`: Passwort des Absenders

Diese Variablen lassen sich in der Balena-Cloud überschreiben.
