import picamera
import time

# picam = picamera.PiCamera()
# picam.start_preview()
# time.sleep(10)
# picam.stop_preview()
# picam.close()

import gpiozero  # The GPIO library for Raspberry Pi
import time  # Enables Python to manage timing
 
led = gpiozero.LED(17) # Reference GPIO17
 
while True:
  led.on() # Turn the LED on
  time.sleep(1)
  led.off() # Turn the LED off
  time.sleep(1)  # Pause for 1 second