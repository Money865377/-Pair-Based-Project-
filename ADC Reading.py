from machine import Pin, PWM, ADC
import time

# --- Setup PWM Output ---
pwm_pin = Pin(15)              # PWM output pin (connect to RC filter input)
pwm = PWM(pwm_pin)
pwm.freq(1000)                 # Set PWM frequency to 1 kHz

# --- Setup ADC Input ---
adc = ADC(Pin(26))             # ADC0 reads from GP26

# --- Main Loop ---
print("Starting PWM and ADC test...\n")
print("Duty Cycle (%)   ADC Reading (0-65535)")

for duty in range(0, 65536, 8192):  # Step through duty cycles
    pwm.duty_u16(duty)              # Set PWM duty cycle
    time.sleep(0.5)                 # Allow filter to settle
    adc_value = adc.read_u16()      # Read analog voltage
    duty_percent = (duty / 65535) * 100
    print(f"{duty_percent:6.1f}%          {adc_value}")
    time.sleep(0.5)

pwm.deinit()
print("\nTest complete. Verify that ADC readings increase as duty cycle increases.")