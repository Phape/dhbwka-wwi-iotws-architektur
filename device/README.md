# Deviceseitiger Softwarestack

Dieses Verzeichnis enthält die Quellcodes und Softwarekomponenten für die IoT-Devices.
Jede Komponente besitzt ihren eigenen Docker-Container, so dass sie mit dem Balena CLI
bzw. der Balena Cloud auf die Devices verteilt werden kann.

Die IoT-Devices umfassen folgende Komponenten:

* `redis`: Zentraler Redis-Server
* `sensor`: Python-Programm zum Auslesen der Sensordaten und Ablage in Redis
* `startstopbutton`: Python-Programm zur Simulation eines Türschlosses (System aktivieren, deaktivieren, Alarm deaktivieren)
* `mqtthandler`: Python-Programm zum Versand der Sensordaten via MQTT
* `grafana`: Lokales Grafana-Dashboard zur Überwachung der Devices
* `actuator`: Ansteuern der Aktoren (LED + Buzzer)
* `alarmhandler`: Bestimmt, wann ein Alarm ausgelöst wird
* `camera`: Personenerkennung mittels Kamera + ML
* `mailhlandler`: Versenden von E-Mails bei Alarm
* `zigbee2mqtt`: Zigbee-Geräte über MQTT ansteuern

Hauptbestandteil ist hier der Redis-Server, der als strukturierter in-memory
Key-Value-Store sowohl für die lokale Zwischenspeicherung der Sensordaten als
auch die Kommunikation der Teilprogramme untereinander sorgt. Der Server ist
so konfiguriert, dass bei einem Stromausfall maximal die Daten der letzten
Sekunde verloren gehen können.

Die Sensordaten werden dabei via MQTT an das Backend sowie weitere, interessierte
Empfänger verschickt. Dabei ist sichergestellt, dass bei einem Teilausfall des
Systems keine Sensordaten verloren gehen, sondern der Sendevorgang automatisch
nachgeholt wird. Ebenso erlauben die Devices eine einfache Fernsteuerung durch
JSON-kodierte Kommandos via MQTT.
