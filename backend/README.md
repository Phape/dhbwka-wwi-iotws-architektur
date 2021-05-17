Serverseitiger Softwarestack
=============================

Dieses Verzeichnis enthält die Quellcodes und Softwarekomponenten für die Serverseite.
Auch hier wird Docker genutzt, um alle Komponenten in Containern zu verpacken und
zu deployen.

 * `mqttserver`: Zentraler MQTT-Server zum Datenaustausch mit den IoT-Devices
 * `mariadb`: MariaDB (ehemals MySQL) Datenbank zur dauerhaften Sicherung der Sensorwerte
 * `receiver`: Python-Programm zum Emfpang der Sensordaten und Ablage in der Datenbank
 * `webadmin`: Webbasierte Admin-Oberfläche zur Einsicht der Sensordaten und Steuerung der Devices

**Der Serverteil ist derzeit in Arbeit und fehlt deshalb noch.**