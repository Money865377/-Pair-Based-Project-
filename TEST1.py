#Set up SPI serial communication between two Picos (use SoftSPI).
#Test sending and receiving simple test messages (like numbers or short text).
#Add LED blink on receiving a message.
#Display received message to user through serial terminal.

#import libraries
from machine import UART, Pin, PWM, ADC
import time

#define the locatoin of the LED 
led1 = Pin(16, Pin.OUT)

#set up uart signal location
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1)

# --- Setup PWM Output ---
pwm_pin = Pin(15)              # PWM output pin (connect to RC filter input)
pwm = PWM(pwm_pin)
pwm.freq(1000)                 # Set PWM frequency to 1 kHz

# --- Setup ADC Input ---
adc = ADC(Pin(26))             # ADC0 reads from GP26

#set up a statement that will always be true
x = 1

#while the statemetn is true, run this loop
while x == 1:
    
    #send a message to the reciving pico
    for duty in range(0, 65536, 8192):  # Step through duty cycles
        pwm.duty_u16(duty)              # Set PWM duty cycle
        time.sleep(0.5)                 # Allow filter to settle
        adc_value = adc.read_u16()      # Read analog voltage
        duty_percent = (duty / 65535) * 100
        uart.write(f"{duty_percent:6.1f}%          {adc_value}")
        time.sleep(0.5)

    pwm.deinit()
    print("\nTest complete. Verify that ADC readings increase as duty cycle increases.")
    
    uart.write("insert signal value here")

    #if there is a response, read it, if not, notify user
    if uart.any(): 

        #print the 2 first bytes of the message that was sent
        print(uart.read(2))
        #make it sleep so it doesnt overwhelm the pico
        time.sleep(2)
    else:
        print("error1")

#temporary until i get the code
while True:
    signal = 0 
    recieved_signal = ["53"]
    #somethign to set appare the recieving and transmitting signals
    recieved_signal.insert(0, "a")

    #find out weather the signal has been pressed yet or not and if it is recieving or tansmitting
    if signal >= 0 and recieved_signal[0] == "a":
        print("message recieved")
        led1.value(1)
        print(recieved_signal[1])
    else:
        print("error2")
        led1.value(0)