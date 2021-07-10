# Serverseitiger Softwarestack

Dieses Verzeichnis enthält die Quellcodes und Softwarekomponenten für die Serverseite ("Backend").
Auch hier wird Docker genutzt, um alle Komponenten in Containern zu verpacken und
zu deployen.

## Docker-Services

Siehe auch [docker-compose](docker-compose.yml)

* `mosquitto`: Zentraler MQTT-Server zum Datenaustausch mit den IoT-Devices
* `db`: MariaDB (ehemals MySQL) Datenbank zur dauerhaften Sicherung der Sensorwerte
* `adminer`: Python-Programm zum Emfpang der Sensordaten und Ablage in der Datenbank
* `mqtt2mysql`: Programm zum Empfangen der Sensordaten (MQTT) und Ablage in der Datenbank (MariaDB, MySQL)
* `grafana`: Webbasiertes Dashboard für die Visualisierung der Daten aus der Datenbank
