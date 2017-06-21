
import RPi.GPIO as GPIO
import socket
import sys
import os
import paho.mqtt.client as mqtt
from sht1x.Sht1x import Sht1x as SHT1x
import select
import json
import time


pumpButtonHome = 16
pumpButtonComm = 18
wlButton = 29
ledHome = 13
ledComm = 15
ledWL = 11
pumpPinHome = 31
pumpPinComm = 36



#  set the pins numbering mode
GPIO.setmode(GPIO.BOARD)

#sensor pins
#watering buttons, with software pull down resistor enabled
GPIO.setup(pumpButtonHome, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pumpButtonComm, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(wlButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#red LED shows timed Dectivated system status
GPIO.setup (ledHome,GPIO.OUT)
GPIO.output (ledHome,0)
GPIO.setup (ledComm,GPIO.OUT)
GPIO.output (ledComm,0)
GPIO.setup (ledWL,GPIO.OUT)
GPIO.output (ledWL,0)

GPIO.setup (pumpPinHome,GPIO.OUT)
GPIO.output(pumpPinHome, 0)
GPIO.setup (pumpPinComm,GPIO.OUT)
GPIO.output(pumpPinComm, 0)

# water lock flag
wlStatus = False

def turn_home(on_off):
    #print "Turning home " + ("on" if on_off else "off")
    GPIO.output(pumpPinHome, on_off)
    GPIO.output(ledHome, on_off)

def turn_comm(on_off):
    #print "Turning comm " + ("on" if on_off else "off")
    GPIO.output(pumpPinComm, on_off)
    GPIO.output(ledComm, on_off)
                
try:
    while True:
        if wlStatus == False:
            GPIO.output (ledWL,0)
            
            #when pump buttons are pressed activate both pumps
            if GPIO.input(pumpButtonHome) or GPIO.input(pumpButtonComm):
                print "A pump BUTTON PRESSED, turning both pumps on"
                turn_home(1)
                turn_comm(1)
            else:
                turn_home(0)
                turn_comm(0)
                
            if GPIO.input(wlButton):
                print " LOCK BUTTON ON"
                wlStatus = True
                GPIO.output(ledWL, 1)
            
        elif wlStatus == True:
            if GPIO.input(pumpButtonHome):
                print "HOME pump BUTTON PRESSED, water lock, activating both pumps"
                turn_home(1)
                turn_comm(1)
            elif GPIO.input(pumpButtonComm):
                print "COMM pump BUTTON PRESSED, water lock, activating comm"
                turn_home(0)
                turn_comm(1)
            else:
                turn_home(0)
                turn_comm(0)
                
            if GPIO.input(wlButton):
                wlStatus = False

        time.sleep(0.1)         # wait 0.1 seconds

finally:                   # this block will run no matter how the try block exits
    GPIO.cleanup()         # clean up after yourself
