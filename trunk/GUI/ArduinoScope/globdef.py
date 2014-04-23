#!/usr/bin/env python
# -*- coding: utf-8 -*-

##This file is part of pyArduinoScope
#############################################################################
#############################################################################
##                                                                         ##
##                                 globdef                                 ##
##                                                                         ##
#############################################################################
#############################################################################

## Copyright (C) 2012 Cédrick FAURY

#    pyArduinoScope is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    pyArduinoScope is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pyArduinoScope; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


# Dossiers ##########################################################################################
import sys, os

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(PATH)
sys.path.append(PATH)


SOURCE = "Arduino"#"Audio"#

# Communication ##########################################################################################
#import serial.tools.list_ports
#Ports = []
#lst = serial.tools.list_ports.comports()
#for name, desc, nid in lst:
#    print name, desc, nid
#    Ports.append(name)
#print "Ports COM disponibles :", Ports

BaudRate = ['2400', '4800', '9600', '19200', '38400', '57600', '115200']

DATAGEN_INTERVAL_MS = 5  # Période d'acquisition des données
BAUDRATE = 115200
COM_PORT = ''

import comscan
def GetArduinoCOMPort():
    res=comscan.comscan()
    lst = []
    for r in res:
        rkeys=r.keys()
        
        rkeys.sort()
        if r['active']:
            if "arduino" in r['driverprovider'] or "Arduino" in r['description']:
                lst.append((r['name'], r['description']))
    return lst
        
COM_PORTS_ARDUINO = GetArduinoCOMPort()
if len(COM_PORTS_ARDUINO) > 0:
    COM_PORT = COM_PORTS_ARDUINO[0][0]
    print u"Arduino trouvé sur", COM_PORT
    
#if type(p) == list:
#    PORT = p[0]
#    Ports = [p]
#    print u"Arduino trouvé sur", PORT
#else:
#    Ports = p
#    print u"Arduino non trouvé", Ports
#
#print PORT

## A function that tries to list serial ports on most common platforms
#""" http://stackoverflow.com/questions/11303850/what-is-the-cross-platform-method-of-enumerating-serial-ports-in-python-includi
#"""
#import platform, glob
#def list_serial_ports():
#    system_name = platform.system()
#    if system_name == "Windows":
#        # Scan for available ports.
#        available = []
#        for i in range(256):
#            try:
#                s = serial.Serial(i)
#                available.append(i)
#                s.close()
#            except serial.SerialException:
#                pass
#        return available
#    elif system_name == "Darwin":
#        # Mac
#        return glob.glob('/dev/tty*') + glob.glob('/dev/cu*')
#    else:
#        # Assume Linux or something else
#        return glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*')
#
#print "Found ports:"
#print list_serial_ports()
#for n,s in list_serial_ports(): print "(%d) %s" % (n,s)



#import winreg, itertools
#
#def enumerate_serial_ports():
#    """ Uses the Win32 registry to return an 
#          iterator of serial (COM) ports 
#          existing on this computer.
#      """
#    path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
#    try:
#        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
#    except WindowsError:
#        raise IterationError
#    
#    for i in itertools.count():
#        try:
#            val = winreg.EnumValue(key, i)
#            yield str(val[1])
#        except EnvironmentError:
#            break

# Tracés ##########################################################################################
X_MIN = X_MAX = Y_MIN = Y_MAX = None
X_RANGE = 1000 #(ms)
X_HISTORY = 2000 #(ms)
NBR_POINTS = 1
LINE_STYLE = '-'
LineStyles = [ '-' , '--' , '-.' , ':' , 'None' , ' ' , '' ]
MARKER_STYLE = '.'
MarkerStyles = [ 'o' , 'D' , 'h' , 'H' , '_' , '' , 'None' , ' ' , '8' , 'p', ',' , '+' , '.' , 's' , '*' , 'd' , '1' , '3' , '4' , '2' , 'v' , '<' , '>' , '^' , '|' , 'x' ]
listeColor = [(1,1,0), (0,1,0), (1,0,0), (0,1,1), (1,0,1), (1,1,1), (0,0,1),
              (.8,.8,0.1), (0.1,.8,0.1), (.8,0.1,0.1), (0.1,.8,.8), (1,0.1,.8), (.8,.8,.8), (0.1,0.1,.8),
              (.5,.5,0.1), (0.1,.5,0.1), (0.1,.5,0.5)]
REFRESH_INTERVAL_MS = 100 # Période de raffraichissement de l'affichage


# Arduino ##########################################################################################
MCU_names = ['avr2', 'at90s2313', 'at90s2323', 'at90s2333', 'at90s2343', 'attiny22', 'attiny26', 'at90s4414', 'at90s4433',
             'at90s4434', 'at90s8515', 'at90c8534', 'at90s8535', 'avr25', 'attiny13', 'attiny13a', 'attiny2313', 'attiny24',
             'attiny44', 'attiny84', 'attiny25', 'attiny45', 'attiny85', 'attiny261', 'attiny461', 'attiny861', 'attiny43u',
             'attiny48', 'attiny88', 'at86rf401', 'avr3', 'at43usb320', 'at43usb355', 'at76c711', 'avr31', 'atmega103',
             'avr35', 'at90usb82', 'at90usb162', 'attiny167', 'avr4', 'atmega8', 'atmega48', 'atmega48p', 'atmega88',
             'atmega88p', 'atmega8515', 'atmega8535', 'atmega8hva', 'at90pwm1', 'at90pwm2', 'at90pwm2b', 'at90pwm3',
             'at90pwm3b', 'avr5', 'atmega16', 'atmega161', 'atmega162', 'atmega163', 'atmega164p', 'atmega165', 'atmega165p',
             'atmega168', 'atmega168p', 'atmega169', 'atmega169p', 'atmega32', 'atmega323', 'atmega324p', 'atmega325',
             'atmega325p', 'atmega3250', 'atmega3250p', 'atmega328p', 'atmega329', 'atmega329p', 'atmega3290', 'atmega3290p',
             'atmega406', 'atmega64', 'atmega640', 'atmega644', 'atmega644p', 'atmega645', 'atmega6450', 'atmega649',
             'atmega6490', 'atmega16hva', 'at90can32', 'at90can64', 'at90pwm216', 'at90pwm316', 'atmega32m1', 'atmega32c1',
             'atmega32u4', 'atmega32u6', 'at90usb646', 'at90usb647', 'at94k', 'avr51', 'atmega128', 'atmega1280', 'atmega1281',
             'atmega1284p', 'at90can128', 'at90usb1286', 'at90usb1287', 'avr6', 'atmega2560', 'atmega2561', 'avrxmega4',
             'atxmega64a3', 'avrxmega5', 'atxmega64a1', 'avrxmega6', 'atxmega128a3', 'atxmega256a3', 'atxmega256a3b',
             'avrxmega7', 'atxmega128a1', 'avr1', 'at90s1200', 'attiny11', 'attiny12', 'attiny15', 'attiny28']
ARDUINO_PATH = "C:\\arduino-1.0.1"
ARDUINO_NAME = 'atmega328p'
ARDUINO_PROG = 'stk500'
ARDUINO_FCPU = '16000000'
ARDUINO_PORT = 5
TYPE_PORT = "A" # "A" ou "N"
TYPE_DATA = "CSV" # "CSV"
SIMPLE_PORT = False
ECHELLE = 5.0/1024

CODE_ARDUINO_SIMPLE_A = """
/*
Script généré par pyArduinoScope
*/

int val = 0;

void setup() {
 Serial.begin(%(baudrate)s);
}

void loop() {
    val = analogRead(%(arport)s);
    Serial.write(val %% 256);
    Serial.write(val / 256);
    Serial.println();
    delay(%(delay)s);
}
"""

CODE_ARDUINO_SIMPLE_N = """
/*
Script généré par pyArduinoScope
*/

void setup() {
 pinMode(%(arport)s, INPUT);
 Serial.begin(%(baudrate)s);
}

void loop() {
    Serial.write(digitalRead(%(arport)s));
    Serial.println();
    delay(%(delay)s);
}
"""

CODE_ARDUINO_MULTI = """
/*
Script généré par pyArduinoScope
*/

// holds temp vals
int val;

void setup() {
  // set 2-12 digital pins to read mode
  for (int i=2;i<12;i++){
    pinMode(i, INPUT);
  }
  
  Serial.begin(%(baudrate)s);  
}

void loop() {  
  // read all analog ports, split by " "
  for (int i=0;i<6;i++){
    val = analogRead(i);
    Serial.write(val %% 256);
    Serial.write(val / 256);
  }
  
  // read all digital ports, split by " "
  for (int i=2;i<12;i++){
    Serial.write(digitalRead(i));
  }
  
  // frame is marked by LF
  Serial.println();
  delay(%(delay)s);
}
"""


# Capture Audio
#import pyaudio
#CHUNK = 1024
#FORMAT = pyaudio.paInt16#pyaudio.paFloat32
#CHANNELS = 1
#RATE = 44100



## Quelques fonctions utiles  a propos des ports série
## thanks to Eli Bendersky's website
## (http://eli.thegreenplace.net/2009/07/31/listing-all-serial-ports-on-windows-with-python/)
#import _winreg as winreg
#import itertools
#
#def enumerate_serial_ports():
#    """ Uses the Win32 registry to return an
#        iterator of serial (COM) ports
#        existing on this computer.
#    """
#    path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
#    try:
#        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
#    except WindowsError:
#        raise IterationError
#
#    for i in itertools.count():
#        try:
#            val = winreg.EnumValue(key, i)
#            yield str(val[1])
#        except EnvironmentError:
#            break
#
#
#import re
#
#def full_port_name(portname):
#    """ Given a port-name (of the form COM7,
#        COM12, CNCA0, etc.) returns a full
#        name suitable for opening with the
#        Serial class.
#    """
#    m = re.match('^COM(\d+)$', portname)
#    if m and int(m.group(1)) < 10:
#        return portname
#    return '\\\\.\\' + portname
