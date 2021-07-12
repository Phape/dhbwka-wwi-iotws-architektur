# Erkennung von Menschen mit Hilfe einer Kamera

## Beschreibung

Dieses Programm kümmert sich um die Ansteuerung der Kamera
zur periodischen Erkennung von Menschen im Kamerafeld. Gemäß der Aufgabenteilung der
verschiedenen deviceseitigen Programme, werden die Messwerte hier nicht
weiterverarbeitet, sondern einfach in einen Redis Stream geschrieben. Das
Auslesen und Verarbeiten der Streamdaten erfolgt durch die anderen Programme.

## Umgebungsvariablen

Folgende Umgebungsvariablen sollten in der `docker-compose.yml` gesetzt werden:

* `REDIS_HOST`: Hostname des lokalen Redis-Servers
* `REDIS_PORT`: Portnummer des lokalen Redis-Servers
* `REDIS_DB`: Datenbanknummer des lokalen Redis-Servers

Folgende Umgebungsvariablen können in der Balena Cloud überschrieben werden:

* `INTERVAL_SECONDS`: Abstand in Sekunden zwischen zwei Messungen

Siehe hierzu auch die Kommentare in der Datei `app.conf`.

## Laufzeitkonfiguration

Folgende Keys in Redis beeinflussen das Laufzeitverhalten dieses Programms.
Sie können von anderen Programmen geschrieben werden, um Einfluss auf die
Messungen zu nehmen:

* `system:enabled`: 1 = System eingeschaltet, 0 = System ausgeschaltet
* `measurement:interval`: Abstand zwischen zwei Messungen in Sekunden
* `measurement:confidence`: Benötigtes Erkennungsvertrauen für die Erkennung eines Menschen
