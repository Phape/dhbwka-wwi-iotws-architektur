# Alarmhandler

## Beschreibung

Dieses Programm entscheidet anhand verschiedener Sensordaten, ob ein Alarm ausgelöst werden soll.
Beispielsweise wird ein Alarm ausgelöst, wenn die Lichtschranke durchbrochen wurde oder wenn die Kamera
Personen erkannt hat.
Ist eine der Bedingungen erfüllt, wird die Redis-Variable `REDIS_ALERT_ENABLED` auf 1 gesetzt.
Alle Services, die etwas ausfürhen, was an einen Alarm geknüpft ist, richten sich nach dem Wert dieser
Variable. (Bspw. Aktoren und Mailversand)

## Umgebungsvariablen

Folgende Umgebungsvariablen sollten in der `docker-compose.yml` gesetzt werden:

* `REDIS_HOST`: Hostname des lokalen Redis-Servers
* `REDIS_PORT`: Portnummer des lokalen Redis-Servers
* `REDIS_DB`: Datenbanknummer des lokalen Redis-Servers
