#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Listen to serial, return most recent numeric values
Lots of help from here:
http://stackoverflow.com/questions/1093598/pyserial-how-to-read-last-line-sent-from-serial-device
"""

from threading import Thread
import threading
import time
import serial
import globdef


from numpy import short, fromstring, arange, uint16, bool, concatenate, zeros


RANDOM = True # pour essais
VAL = [0.] * 16
VALS = 0.
import random


last_received = ''
last_time = 0.


class Thread_Reception(threading.Thread):
    def __init__(self, ser):
        threading.Thread.__init__(self)
        self.Terminated = False
        self.Pause = False
        self.ser = ser
    
    def run(self):
        print "Thread_Reception run !"
        global last_received, last_time
        i = 0
        buff = ''
        while not self.Terminated:
            if self.Pause:
                time.sleep(0.1)
                continue 
            try:
                buff = buff + self.ser.read(self.ser.inWaiting())
            except:
                pass
    #            print "rien reçu !"
    #            last_received = None # L'arduino ne communique pas ! = pas de programme dedans
            if '\n' in buff:
                lines = buff.split('\n') # Guaranteed to have at least 2 entries
                last_received = lines[-2]
                last_time = time.clock()
                #If the Arduino sends lots of empty lines, you'll lose the
                #last filled line, so you could make the above statement conditional
                #like so: if lines[-2]: last_received = lines[-2]
                buff = lines[-1]
        print "Thread_Reception s'est termine proprement"
    
    def stop(self):
        print "Arrêt thread Reception..."
        self.Terminated = True




class SerialData(object):
    def __init__(self, init=50, baudrate = 9600, port = 'com3'):
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1,
                xonxoff=0,
                rtscts=0,
                interCharTimeout=None
            )
        except serial.serialutil.SerialException:
            print "no serial connection"
            self.ser = None
        else:
            self.t = Thread_Reception(self.ser)
            self.t.start()
        
    def next_multi(self):
        if not self.ser:
            if RANDOM:
                global VAL
                r = [(random.random()-0.5)*20 for i in range(16)]
                VAL = [v+r for v, r in zip(VAL,r)]
                return VAL
            else:  
                return None #return anything so we can test when Arduino isn't connected
        
        #return a float value or try a few times until we get one
        for i in range(40):
            if last_received == None:
                return None
            
            if len(last_received) == 23:
                lstVal = concatenate((fromstring(last_received, count = 6, dtype = uint16), 
                                      fromstring(last_received[-11:], count = 10, dtype = bool)))
                if len(lstVal) == 16:
                    return (last_time, lstVal*globdef.ECHELLE)
        
        return (last_time, zeros(16))
    
    
    
    def next_simple(self, num = False):
        if not self.ser:
            if RANDOM:
                global VALS
                VALS += (random.random()-0.5)*20
                return VALS
            else:  
                return None #return anything so we can test when Arduino isn't connected
        
        #return a float value or try a few times until we get one
        for i in range(40):
            if last_received == None:
                return None
        
            if num:
                if len(last_received) == 2:
                    val = fromstring(last_received, count = 1, dtype = bool)
                    if len(val) == 1:
                        return (last_time, val[0])
            else:
                if len(last_received) == 3:
                    val = fromstring(last_received, count = 1, dtype = uint16)
#                    print val, len(val)
                    if len(val) == 1:
                        return (last_time, val[0]*globdef.ECHELLE)
#            try:
#                val = fromstring(last_received, count = 1, dtype = uint16)
#                return (last_time, float(last_received.strip())*globdef.ECHELLE)
#            except ValueError:
#                print 'bogus data',last_received
#                time.sleep(.005)
        return (last_time, 0.)
    
    
    
    def __del__(self):
        if self.ser:
            self.ser.close()

    def Pause(self, etat):
        if hasattr(self, 't'):
            self.t.Pause = etat
    

    def Terminer(self):
        if hasattr(self, 't'):
            self.t.Terminated = True
        self.__del__()






class DataGen_Thread(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.parent = parent
        self.datagen = self.parent.datagen
        self._stopevent = threading.Event( )
        self.temps = 0.
     
    def run(self):
        print "DataGen run !"
        self.t0 = time.clock()
        self.t = 0.
        while not self._stopevent.isSet():
            self.on_datagen_timer()
#            self._stopevent.wait(0.001*globdef.DATAGEN_INTERVAL_MS)
            
        print u"le thread DataGen s'est terminé proprement"
        
    def stop(self):
        print "Arrêt thread DataGen..."
        self._stopevent.set( )
        
    def on_datagen_timer(self):
        
        #
        # Attente ...
        #
        t_attente = 0.001*globdef.DATAGEN_INTERVAL_MS - (time.clock()-self.temps)
        if t_attente > 0:
            self._stopevent.wait(t_attente)
            
        #
        # Récupération des données
        #
        if globdef.SIMPLE_PORT:
            temps, data = self.datagen.next_simple()
        else:
            temps, data = self.datagen.next_multi()
        

        
        #
        # Enregistrement des données
        #
        if temps > 0 and self.temps != temps:
            self.temps = temps
            self.t = temps - self.t0
#            print (self.t*1000, data)
            self.parent.data.append((self.t*1000, data))
            self.parent.temps.append(self.t*1000)
            
            #
            # Suppression des données plus anciennes que l'historique
            #
            self.parent.data = self.parent.data[-globdef.NBR_POINTS:]
            

if __name__=='__main__':
    s = SerialData()
    for i in range(500):
        time.sleep(.005)
        print s.next()