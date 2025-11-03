from machine import Pin, PWM, ADC, UART
import time
import random

# LEDs for feedback
led_ok = Pin(16, Pin.OUT)
led_error = Pin(17, Pin.OUT)

# Button to start
button = Pin(22, Pin.IN, Pin.PULL_DOWN)

# PWM setup
pwm_pin = Pin(15)
pwm = PWM(pwm_pin)
pwm.freq(1000)  # 1 kHz

# ADC setup (connected to other Pico's PWM through RC filter)
adc = ADC(26)

# UART setup for communication
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))

#give the user some instrucitons and an explanation of what the program does
print("""
This program will measure and compare the expected and actual PWM signals of 2 Picos.
To indicate things are going well, the --- light will turn on.
To indicate an error, the --- light will turn on.      

If you would like to procede, press the sw5 button.
      """)


# Wait for receiver's guess
time.sleep(0.5)
    
while True: 
    # Generate random PWM duty 
    my_duty = random.randint(0, 65535)
    pwm.duty_u16(my_duty)
    my_percent = (my_duty / 65535) * 100
    print(f"My PWM Sent: {my_percent:.1f}%")

    # Send own duty cycle to the other Pico 
    uart.write(f"{my_duty}\n")

    # Check if other Pico sent a duty
    if uart.any():
        data = uart.readline()
        try:
            other_duty = int(data.decode().strip())

            # Measure PWM from other Pico
            adc_value = adc.read_u16()
            guess_duty = int((adc_value / 65535) * 65535)
            guess_percent = (guess_duty / 65535) * 100
            other_percent = (other_duty / 65535) * 100
            difference = abs(guess_percent - other_percent)

            print(f"Other PWM Sent: {other_percent:.1f}% | ADC Guess: {guess_percent:.1f}% | Δ={difference:.1f}%")

            # LED feedback 
            if difference < 5:
                led_ok.value(1)
                led_error.value(0)
            else:
                led_ok.value(0)
                led_error.value(1)

        except:
            print("Error decoding received duty")
            led_error.toggle()

    time.sleep(1)