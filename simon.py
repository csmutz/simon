#!/usr/bin/env python
'''
Implement Simon using LEDs, buttons, and passive buzzer
'''
import RPi.GPIO as GPIO
import time
import random
import sys

#GPIO of buttons, should ground when pushed
buttons = [26, 19, 13, 6]
#GPIO of LEDs, use 33O resistor
leds = [22, 27, 17, 4 ]
#frequency of notes used
notes = [1568, 1760, 1976, 2093]
buzzer = None

def gpio_setup():
    '''
    setup GPIOs at start of program
    '''
    global buzzer
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(18, GPIO.OUT)
    buzzer = GPIO.PWM(18, 2000)	# 18 is GPIO, 2000 is frequency
    buzzer.stop() #buzzer should be stopped
    for i in range(4):
        #set button GPIOs to input with pull up resister
        GPIO.setup(buttons[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #set LED GPIOs to output, start off
        GPIO.setup(leds[i],GPIO.OUT)
        GPIO.output(leds[i],GPIO.LOW)


def led_on(bank):
    GPIO.output(leds[bank],GPIO.HIGH)

def led_off(bank):
    GPIO.output(leds[bank],GPIO.LOW)

def sound_on(freq):
    global buzzer
    buzzer.ChangeFrequency(freq)
    buzzer.start(50) #50 duty cycle

def sound_off():
    global buzzer
    buzzer.stop()

def led_and_sound_on(bank):
    led_on(bank)
    sound_on(notes[bank])
    
def led_and_sound_off(bank):
    global buzzer
    led_off(bank)
    sound_off()

def play_freq(freq, length=.25, rest=.05):
    global buzzer
    sound_on(freq)
    time.sleep(length)
    sound_off()
    time.sleep(rest)


def startup_sound():
    '''
    music and lights to indicate game start
    '''
    global buzzer
    sound_len = .30
    
    led_on(3)
    
    for i in range(3):
        led_on(i)
        play_freq(notes[i],sound_len)
        play_freq(notes[i],sound_len/3)
        play_freq(notes[i],sound_len/3)
        play_freq(notes[i],sound_len/3)
        play_freq(notes[i],sound_len)
        play_freq(notes[i],sound_len*2)
     
    time.sleep(1)
    
    for i in range(4):
        led_off(i)
    time.sleep(1)

def end_game():
    time.sleep(.5)
    play_freq(2000, .5)
    play_freq(1500, 2)
    sys.exit(1)

def main():
    gpio_setup()
    startup_sound()
    
    simon_presses = []
    human_presses = []
    simon_press_len = .5
    simon_rest_len = .1
        
    while True:
        #computer turn
        bank = random.choice(range(4))
        simon_presses.append(bank)
        
        for bank in simon_presses:
            led_and_sound_on(bank)
            time.sleep(simon_press_len)
            led_and_sound_off(bank)
            time.sleep(simon_rest_len)
        
        #human turn
        move_count = 0
        while move_count < len(simon_presses):          
            for bank in range(4):
                #if button pressed, go to GND, values is false
                if GPIO.input(buttons[bank]) == False:
                    #sleep to debounce original press
                    time.sleep(.001)
                    if GPIO.input(buttons[bank]) == False:
                        if bank == simon_presses[move_count]:
                            #correct button pressed
                            led_and_sound_on(bank)
                            #loop while button is still pressed
                            while(GPIO.input(buttons[bank]) == False):
                                time.sleep(.01)
                            led_and_sound_off(bank)
                            time.sleep(0.05)
                            move_count = move_count + 1
                        else:
                            #incorrect move
                            end_game()  
        time.sleep(1)    

if __name__ == "__main__":
    main()