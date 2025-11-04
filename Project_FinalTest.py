#import required modules
from machine import Pin, PWM, ADC, UART
import time

#LEDs for feedback
led_ok = Pin(16, Pin.OUT)
led_error = Pin(17, Pin.OUT)
#button to make the program more user friendly (press to start)
sw5 = Pin(22, Pin.IN, Pin.PULL_DOWN)

#Button to start
button = Pin(22, Pin.IN, Pin.PULL_DOWN)

# PWM setup
pwm_pin = Pin(15)
pwm = PWM(pwm_pin)
pwm.freq(1000)  # 1 kHz

#ADC setup (connected to other Pico's PWM through RC filter)
adc = ADC(26)

#UART setup for communication
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))

#give the user some instrucitons and an explanation of what the program does
print("""
This program will measure an compare the expected and actual PWM signals of 2 Picos as a percentage.
To indicate things are going well, LED 1 will turn on.
To indicate an error, LED 2 will turn on.      
      """)

#set the duty cycle to whatever the user would like it to be (between 0 and 65536)
duty_cycle = int(input("If you would like to procede, give me a duity cycle (any number between 0 and 65536): "))

#make sure the number that was given was between 0 and 65536
if duty_cycle >= 0 and duty_cycle <= 65536:
    #if it is, continue
    print("press the sw5button to continue")
else:
    #if it is not, then notify the user and ask them to try again
    print("I said a number between 0 and 65536, try again")

#a loop that will always be ture so that the user can continuously recieve data wihtout restarting the program
while True: 
    if sw5.value():
        #convert the first picos duty cycle to a percentage 
        pwm.duty_u16(duty_cycle)
        my_percent = (duty_cycle / 65535) * 100
        print(f"My PWM Sent: {my_percent:.1f}%")

        #send the first picos own guessed duty cycle as a percentage
        uart.write(f"{duty_cycle}\n")

        #turn on the ok LED to show that the message was recieved and everythign is going well
        led_ok.value(1)

        #Check if the second pico has sent a duty cycle value
        if uart.any():
            #if it did, read the data it received
            data = uart.readline()

            #turn on the ok LED to show that the message was recieved and everythign is going well
            led_ok.value(1)

            try:
                #convert the data recieved into somehting the user can easily understand
                actual_duty = int(data.decode().strip())

                # Measure PWM from other Pico and turn the guessed and actual measured PWM values into percentages
                adc_value = adc.read_u16()
                guessed_duty = int((adc_value / 65535) * 65535)
                guessed_percent = (guessed_duty / 65535) * 100
                actual_percent = (actual_duty / 65535) * 100
                #find the accuracy of the picos PWM signal by finding the difference between the acutal and guessed percent
                difference = abs(guessed_percent - actual_percent)

                #turn on the ok LED to show that the message was recieved and everythign is going well
                led_ok.value(1)

            except:
                #if there is an error, notify the user using the terminal and LEDs
                print("An error has occured while decoding received duty")
                led_error.toggle()
            
            #print the results
            print(f"Other PWM Sent: {actual_percent:.1f}% | ADC: {guessed_percent:.1f}% | Difference: {difference:.1f}%")
        
        else:
            #notify user if there is no reply to read
            print("Error: there has been an issue reading the ADC signal")
            led_error.toggle()
        
        #give the picos a time buffer to send and recive singals so that they do not get overwhelmed
        time.sleep(1)