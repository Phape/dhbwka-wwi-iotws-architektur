# Benoetigte Module werden importiert und eingerichtet
import RPi.GPIO as GPIO
import time
  
GPIO.setmode(GPIO.BCM)
  
# Hier wird der Eingangs-Pin deklariert, an dem der Sensor angeschlossen ist.
Buzzer_PIN = 25 
GPIO.setup(Buzzer_PIN, GPIO.OUT, initial= GPIO.LOW)
  
print "Buzzer-Test [druecken Sie STRG+C, um den Test zu beenden]"
 
# Hauptprogrammschleife
try:
        while True:
        #print("Buzzer 4 Sekunden an")
        GPIO.output(Buzzer_PIN,GPIO.HIGH) #Buzzer wird eingeschaltet
        time.sleep(4) #Wartemodus für 4 Sekunden
        #print("Buzzer 2 Sekunden aus") 
        GPIO.output(Buzzer_PIN,GPIO.LOW) #Buzzer wird ausgeschaltet
        time.sleep(2) #Wartemodus für weitere zwei Sekunden, in denen die LED Dann ausgeschaltet ist
  
# Aufraeumarbeiten nachdem das Programm beendet wurde
except KeyboardInterrupt:
        GPIO.cleanup()