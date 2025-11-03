#import libraries
from machine import UART, Pin, PWM, ADC
import time

#define the locations of the LEDS and PIN 
led1 = Pin(16, Pin.OUT)
led2 = Pin(17, Pin.OUT)
sw5 = Pin(22, Pin.IN, Pin.PULL_DOWN)

#set up uart signal location
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1)

# PWM output pin (connect to RC filter input)
pwm_pin = Pin(15)              
pwm = PWM(pwm_pin)

# Set PWM frequency to 1 kHz
pwm.freq(1000)                 

#Setup ADC Input
adc = ADC(26)             

#give the user some instrucitons and an explanation of what the program does
print("""
This program will measure an compare the expected and actual PWM signals of 2 Picos.
To indicate things are going well, LED 1 will turn on.
To indicate an error, LED 2 will turn on.      

If you would like to procede, press the sw5 button.
      """)

#while the statemetn is true, run this loop
while True:
    if sw5.value():
        #send a message to the reciving pico
        for duty in range(0, 65536, 8192):  # Step through duty cycles
            pwm.duty_u16(duty)              # Set PWM duty cycle
            time.sleep(0.5)                 # Allow filter to settle

            #find out weather the signal has been recieved sucsessfully
            try:
                #Read analog voltage
                adc_value = adc.read_u16()
                print("message recieved")
                #if the message is recieved, blink the LED
                led1.value(1)
            except: 
                #if the message is not recieved, notify user
                print("Error: there is no signal being read")
                led1.value(0)
            
            #find the duty cycle percentage
            duty_percent = (duty / 65535) * 100

            #print the results to the user
            message = f"{duty_percent:.1f},{adc_value}\n"
            uart.write(message)

            #sleep for 0.5 seconds to give the devices time to send and recieve signals smoothly
            time.sleep(0.5)   

        pwm.deinit()
        print("\nTest complete. Verify that ADC readings increase as duty cycle increases.")

        #if there is a response, read it, if not, notify user
        if uart.any(): 
            #Read one line of text
            data = uart.readline() 
            if data:
                #Blink LED to show message received
                led1.toggle()       
                try:
                    #decode the recieved information to ensure the user can read and understand it
                    duty_str, adc_str = data.decode().strip().split(',')
                    #change the type of the infromation from the duty cycle to float
                    duty = float(duty_str)
                    #change the type of the infromation from the duty cycle to integer
                    adc = int(adc_str)
                    #print the recieved duty cycle
                    print(f"Received -> Duty Cycle: {duty:.1f}% | ADC: {adc}")
                except:
                    #notify user if there is an issue decoding the signal from the pico
                    print("Error parsing:", data)
            else:
                #Blink LED and notify the users that the signal has not been recieved
                print("Error: there is no signal being read")
                led2.toggle()
            #allow the picos 0.2 seconds to recive data so that they do not get overwhelmed
            time.sleep(0.2)
        else:
            #notify user if there is no reply to read

            print("Error: there has been an issue reading the ADC signal")
