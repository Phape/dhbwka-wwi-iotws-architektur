# Benoetigte Module werden importiert und eingerichtet
import RPi.GPIO as GPIO
import time
   
GPIO.setmode(GPIO.BCM)
   
# Hier werden die Ausgangs-Pin deklariert, an dem die LEDs angeschlossen sind.
LED_ROT = 24
LED_GRUEN = 23
GPIO.setup(LED_ROT, GPIO.OUT, initial= GPIO.LOW)
GPIO.setup(LED_GRUEN, GPIO.OUT, initial= GPIO.LOW)
   
print "LED-Test [druecken Sie STRG+C, um den Test zu beenden]"
# Hauptprogrammschleife
try:
        while True:
            #print("LED ROT 3 Sekunden an")
            GPIO.output(LED_ROT,GPIO.HIGH) #LED rot wird eingeschaltet
            #GPIO.output(LED_GRUEN,GPIO.LOW) #LED grün wird ausgeschaltet
            time.sleep(1) # Wartemodus fuer 2 Sekunden
            #print("LED GRUEN 3 Sekunden an") 
            GPIO.output(LED_ROT,GPIO.LOW) #LED rot wird ausgeschaltet
            #GPIO.output(LED_GRUEN,GPIO.HIGH) #LED grün wird eingeschaltet
            time.sleep(2) #Wartemodus fuer weitere zwei Sekunden, in denen die LED Dann ausgeschaltet ist
   
# Aufraeumarbeiten nachdem das Programm beendet wurde
except KeyboardInterrupt:
        GPIO.cleanup()