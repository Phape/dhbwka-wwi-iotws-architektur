# Aktoren

## Beschreibung

Dieses Programm kümmert sich um die Ansteuerung der Aktoren (wie Buzzer und LED).

## Auslösen der Aktoren

Die Aktoren werden eingeschaltet, wenn ein Alarm ausgelöst wurde.
`REDIS_ALERT_SYSTEM_ACTIVE` und `REDIS_ALERT_ENABLED` müssen hierzu aktiv sein.

## Umgebungsvariablen

Folgende Umgebungsvariablen sollten in der `docker-compose.yml` gesetzt werden:

* `REDIS_HOST`: Hostname des lokalen Redis-Servers
* `REDIS_PORT`: Portnummer des lokalen Redis-Servers
* `REDIS_DB`: Datenbanknummer des lokalen Redis-Servers
