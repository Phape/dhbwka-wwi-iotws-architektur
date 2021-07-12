# Start/Stop-Button

## Beschreibung

Dieses Programm dient der Simulation eines Türschlsses mithilfe eines Drehschalters,
der Drehung im und gegen den Uhrzeigersinn erkennt, sowie einen Druck auf den Drehknopf.

* Bei Druck auf den Drehknopf wird ein aktiver Alarm deaktiviert.
* Bei Drehung gegen den Uhrzeigersinn (Abschließen) wird das System aktiviert (`REDIS_ALERT_SYSTEM_ACTIVE`)
* Brei Drehung im Uhrzeigersinn (Aufschließen) wird das System deaktiviert

## Umgebungsvariablen

Folgende Umgebungsvariablen sollten in der `docker-compose.yml` gesetzt werden:

* `REDIS_HOST`: Hostname des lokalen Redis-Servers
* `REDIS_PORT`: Portnummer des lokalen Redis-Servers
* `REDIS_DB`: Datenbanknummer des lokalen Redis-Servers
* `BUTTON_PIN_CLK`: GPIO-Pin des Drehschalters (Uhrzeigersinn)
* `BUTTON_PIN_DT`: GPIO-Pin des Drehschalters (gegen Uhrzeigersinn)

Siehe hierzu auch die Kommentare in der Datei `app.conf`.
