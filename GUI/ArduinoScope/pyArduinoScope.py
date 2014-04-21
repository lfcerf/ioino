#!/usr/bin/env python
# -*- coding: utf-8 -*-

##This file is part of pyArduinoScope
#############################################################################
#############################################################################
##                                                                         ##
##                               pyArduinoScope                            ##
##                                                                         ##
#############################################################################
#############################################################################

## Copyright (C) 2012 Cédrick FAURY

#    pyArduinoScope is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
    
#    pyArduinoScope is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pyArduinoScope; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
pyArduinoScope.py
Un oscilloscope avec Arduino

@author: Cedrick FAURY

Code très largement inspiré de http://www.blendedtechnologies.com/realtime-plot-of-arduino-serial-data-using-python/231
    par Eli Bendersky (eliben@gmail.com)
"""
__appname__= "pyArduinoScope"
__author__ = u"Cédrick FAURY"
__version__ = "0.3"


import os
#import pprint
#import random
#import sys
import wx

import Options
import globdef

import subprocess
import tempfile

import time

from widgets import *
# The recommended way to use wx with mpl is with the WXAgg
# backend.
#
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab
#Data comes from here
from Arduino_Monitor import SerialData as DataGen
from Arduino_Monitor import DataGen_Thread

#from Audio_Monitor import *

class GraphFrame(wx.Frame):
    """ The main frame of the application
"""
    title = 'pyArduinoScope'
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)
        
#        AjoutVariablesEnv()

        self.paused = False
        self.fichier = None
        self.nomfichier = ""
        
        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()
        
        #############################################################################################
        # Instanciation et chargement des options
        #############################################################################################
        options = Options.Options()
        if options.fichierExiste():
#            options.ouvrir()
            try :
                options.ouvrir()
            except:
                print "Fichier d'options corrompus ou inexistant !! Initialisation ..."
                options.defaut()
                
        # On applique les options ...
        self.DefinirOptions(options)
        self.AppliquerOptions() 
        self.initTimer()
        
        
        
        # Interception de la demande de fermeture
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        
        
        
    def initSerial(self):
        """ Initialisation de la communication série
        """
        print "initSerial", globdef.COM_PORT, globdef.BAUDRATE
        
        if hasattr(self, 'datagen'):
            self.datagen.Terminer()
            
        if globdef.SOURCE == "Arduino":
            self.datagen = DataGen(baudrate = globdef.BAUDRATE, port = globdef.COM_PORT)
        else:
            self.datagen = AudioData()
        
        if not self.datagen.ser:
            print u"  Connexion échouée !!"

        #
        # Remise à 0 des données et des tracés
        #
        self.initData()
        for p in range(16):
            self.plot_data[p].set_xdata([0.])
            self.plot_data[p].set_ydata([0.])
        
        self.temps = []
        
        
    def initData(self):
        if globdef.TYPE_DATA == "ES" :
            if globdef.SIMPLE_PORT or globdef.SOURCE != "Arduino":
                self.data = [(0., 0.)]
            else:
                self.data = [(0., np.zeros(16))]
        elif globdef.TYPE_DATA == "CSV" :
            self.data = [(0., np.zeros(16))]
        self.csv = []
        
        if hasattr(self, "cb_e") and self.cb_e.GetValue():
            if self.nomfichier == "":
                dlg = wx.FileDialog(
                self, message=u"Selectionner un fichier",
                defaultDir=os.getcwd(), 
                defaultFile="",
                style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
                )
    
                if dlg.ShowModal() == wx.ID_OK:
                    # This returns a Python list of files that were selected.
                    self.nomfichier = dlg.GetPaths()[0]
                    self.ds.SetPath(self.nomfichier)
            try:
                self.fichier = open(self.nomfichier, 'w')
            except:
                self.fichier = None
        else:
            self.fichier = None
        
    def initTimer(self):
        """ Initialisation et démarrage du timer
        """
        print "initTimer", globdef.REFRESH_INTERVAL_MS
        
        if hasattr(self, 'redraw_timer'):
            self.redraw_timer.Stop()
            
        if hasattr(self, 'datagen_thread'):
            self.datagen_thread.stop()
            
        if globdef.SOURCE == "Arduino":
            self.datagen_thread = DataGen_Thread(self)
        else:
            self.datagen_thread = Audio_Thread(self)
        
        self.datagen_thread.start()
        
        self.redraw_timer = wx.Timer(self)
        
        self.redraw_timer.Start(globdef.REFRESH_INTERVAL_MS)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
        
        
    def create_menu(self):
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, u"&Enregistrer le tracé\tCtrl-S", u"Enregistrer le tracé dans un fichier")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "Quitter\tCtrl-Q", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
                
        menu_tool = wx.Menu()
        m_expt = menu_tool.Append(-1, u"&Options\tCtrl-O", u"Options")
        self.Bind(wx.EVT_MENU, self.on_options, m_expt)
        
        
        self.menubar.Append(menu_file, "&Fichier")
        self.menubar.Append(menu_tool, "&Outils")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)


        #
        # La scroll bar
        #
        self.sb = wx.ScrollBar(self.panel, -1)
        self.Bind(wx.EVT_SCROLL, self.OnScroll, self.sb)
        self.sb.Enable(False)
        
        #
        # Axe des X
        #
        sbX = wx.StaticBox(self.panel, -1, u"Axe du temps")
        sbsX = wx.StaticBoxSizer(sbX, wx.VERTICAL)
        
        self.rb1 = wx.RadioButton( self.panel, -1, "Auto", style = wx.RB_GROUP )
        rb2 = wx.RadioButton( self.panel, -1, "Manuel" )
        self.Bind(wx.EVT_RADIOBUTTON, self.on_update_manualX, self.rb1)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_update_manualX, rb2)
#        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manualX, self.rb1)
        
        self.vX = Variable(u"Intervalle ", lstVal = [globdef.X_RANGE], nomNorm = "", typ = VAR_ENTIER_POS, 
                 bornes = [None,None], modeLog = True,
                 expression = None, multiple = False)
        self.vcX = VariableCtrl(self.panel, self.vX, coef = None, labelMPL = False, signeEgal = False, 
                 slider = True, fct = None, help = "", sizeh = -1, color = wx.BLACK)
        self.vcX.Enable(False)
        self.Bind(EVT_VAR_CTRL, self.OnRangeX)
        
        self.cb_xlab = wx.CheckBox(self.panel, -1,
            u"Afficher le temps")
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)
        self.cb_xlab.SetValue(True)

        sbsX.Add(self.rb1, flag = wx.EXPAND)
        sbsX.Add(rb2, flag = wx.EXPAND)
        sbsX.Add(self.vcX, flag = wx.EXPAND)
        sbsX.Add(self.cb_xlab, flag = wx.EXPAND)
        
        #
        # Axe des Y
        #
        sbY = wx.StaticBox(self.panel, -1, u"Axe des Y")
        sbsY = wx.StaticBoxSizer(sbY, wx.HORIZONTAL)
        self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
        self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 100)
        sbsY.Add(self.ymin_control, flag = wx.EXPAND)
        sbsY.Add(self.ymax_control, flag = wx.EXPAND)
        
        #
        # Bouton pause
        #
        self.pause_button = wx.Button(self.panel, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
        
        #
        # Autres options
        #
        self.cb_grid = wx.CheckBox(self.panel, -1,
            u"Montrer la grille")
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(True)
        
        #
        # Enregistrement
        #
        sbe = wx.StaticBox(self.panel, -1, u"Enregistrement")
        sbse = wx.StaticBoxSizer(sbe, wx.VERTICAL)
        self.cb_e = wx.CheckBox(self.panel, -1,
            u"Enregistrer les données")
        self.Bind(wx.EVT_CHECKBOX, self.on_check_enregistrer, self.cb_e)
        self.ds = URLSelectorCombo(self.panel)
        sbse.Add(self.cb_e, flag = wx.EXPAND|wx.ALL, border = 2)
        sbse.Add(self.ds, flag = wx.EXPAND|wx.ALL, border = 2)
        
        #
        # Selection de ports
        #
        self.selectA = ChannelChoiceBox(self.panel, -1, u"Ana", 6, globdef.listeColor[:6])
        self.selectN = ChannelChoiceBox(self.panel, -1, u"Num", 10, globdef.listeColor[6:])
        
        #
        # Mise en place
        #
        self.hbox_select = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_select.Add(self.selectA, flag = wx.EXPAND)
        self.hbox_select.Add(self.selectN, flag = wx.EXPAND)
        
        self.vbox_droite = wx.BoxSizer(wx.VERTICAL)
        self.vbox_droite.Add(self.hbox_select, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.vbox_droite.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.vbox_droite.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.vbox_droite.Add(sbse, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.hbox_bas = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_bas.Add(sbsX, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox_bas.Add(sbsY, border=5, flag=wx.ALL|wx.EXPAND)
        
        
        self.vbox_gauche = wx.BoxSizer(wx.VERTICAL)
        self.vbox_gauche.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.EXPAND)
        self.vbox_gauche.Add(self.sb, 0, flag=wx.LEFT | wx.TOP | wx.EXPAND)
        self.vbox_gauche.Add(self.hbox_bas, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.vbox_gauche, 1, flag=wx.EXPAND)
        self.hbox.Add(self.vbox_droite, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.panel.SetSizer(self.hbox)
        self.hbox.Fit(self)
        
     
    
    
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((3.0, 3.0), dpi=self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_bgcolor('black')
#        self.axes.set_title('ArduinoScope - port '+str(globdef.ARDUINO_PORT), size=12)
        
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        # plot the data as a line series, and save the reference
        # to the plotted line series
        #
        self.initData()
        
        x, y = zip(*self.data)
        self.plot_data = []
        for p in range(16):
            self.plot_data.append(self.axes.plot(
                x, y,
                linewidth=1,
                linestyle = globdef.LINE_STYLE,
                marker = globdef.MARKER_STYLE,
                color=globdef.listeColor[p],
                )[0])


    #########################################################################################################
    def dezipperData(self):
        x, y = zip(*self.data)
        
        if type(y[0]) == np.ndarray:
            y = zip(*y)
#        print y
        return x, y
        
    #########################################################################################################
    def AjusterVue(self, x = None, y = None, pos = None):
        """ Ajustement de la vue en fonction des paramètres d'affichage
        """
        if x == None or y == None:
            x, y = self.dezipperData()
            if pos == None:
                pos = x[-1]
            else:
                pos = x[-1]-globdef.X_HISTORY+globdef.X_RANGE+pos
#            print pos
            redraw = True
        else:
            pos = x[-1]
            redraw = False
        
        
        #
        # Xmax
        #
        if self.rb1.GetValue(): # Zomm "tout"
            xmax = pos if pos > globdef.X_HISTORY else globdef.X_HISTORY
        else:
            xmax = pos if pos > globdef.X_RANGE else globdef.X_RANGE
            
        #
        # Xmin
        #
        if self.rb1.GetValue(): # Zomm "tout"
            xmin = xmax - globdef.X_HISTORY
        else:
            xmin = xmax - globdef.X_RANGE
        
        #
        # Y
        #
        yyy = []
        if globdef.TYPE_DATA == "ES":
            if not globdef.SIMPLE_PORT:
                lstC = self.selectA.GetValues() + self.selectN.GetValues()
                for i, s in enumerate(lstC):
                    if s:
                        yyy.append(y[i])
                M_y, m_y = [max(Y) for Y in yyy], [min(Y) for Y in yyy]
            
            else:
                yyy = [y]
                M_y, m_y = [max(Y) for Y in yyy], [min(Y) for Y in yyy]
        
        elif globdef.TYPE_DATA == "CSV":
            yyy = y
            M_y, m_y = [max(Y) for Y in yyy], [min(Y) for Y in yyy]
            
        if yyy == []:
            return
        
        
#        print "min-max", m_y, M_y
        if self.ymin_control.is_auto():
            ymin = round(min(m_y), 0) - 1
        else:
            ymin = int(self.ymin_control.manual_value())
        
        if self.ymax_control.is_auto():
            ymax = round(max(M_y), 0) + 1
        else:
            ymax = int(self.ymax_control.manual_value())

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)
        
        if redraw:
            self.canvas.draw()

    #########################################################################################################
    def draw_plot(self):
        """ Redraws the plot
        """
#        print 'draw_plot', self.data[-1]
        x, y = self.dezipperData()
#        print len(self.data)
#        print "x", x[-100:]
#        print "y", y[0][-100:]
        
        self.AjusterVue(x, y)

        if self.cb_grid.IsChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly
        # iterate, and setp already handles this.
        #
        pylab.setp(self.axes.get_xticklabels(),
            visible=self.cb_xlab.IsChecked())
        
        if globdef.SOURCE != "Arduino":
            self.plot_data[0].set_xdata(np.array(x))
            self.plot_data[0].set_ydata(np.array(y[0]))
        
        elif globdef.TYPE_DATA == "ES":
            if globdef.SIMPLE_PORT: 
                if globdef.TYPE_PORT == "A":
                    i = globdef.ARDUINO_PORT
                else:
                    i = globdef.ARDUINO_PORT + 6
                self.plot_data[i].set_xdata(np.array(x))
                self.plot_data[i].set_ydata(np.array(y))
            else:
                lstC = self.selectA.GetValues() + self.selectN.GetValues()
                for i, s in enumerate(lstC):
                    if s:
                        self.plot_data[i].set_xdata(np.array(x))
                        self.plot_data[i].set_ydata(np.array(y[i]))
        
        elif globdef.TYPE_DATA == "CSV":
            for i, s in enumerate(y):
                self.plot_data[i].set_xdata(np.array(x))
                self.plot_data[i].set_ydata(np.array(y[i]))
            
        self.canvas.draw()
    
    def OnScroll(self, event):
        if not self.paused:
            return
        self.AjusterVue(pos = self.sb.GetThumbPosition())
        
    def OnRangeX(self, event):
        globdef.X_RANGE = self.vX.v[0]
        self.ReglerScrollBar()
#        print self.sb.GetThumbPosition()
        self.AjusterVue()
        
        
    def on_update_manualX(self, event):
        self.vcX.Enable(not self.rb1.GetValue())
        self.sb.Enable(self.paused and not self.rb1.GetValue())
        if not self.rb1.GetValue():
            self.AjusterVue(pos = self.sb.GetThumbPosition())
        else:
            self.AjusterVue()
#        globdef.X_RANGE == self.vX.v[0]
            
    def on_pause_button(self, event = None):
        self.paused = not self.paused
        
        self.sb.Enable(self.paused and not self.rb1.GetValue())
        if self.sb.IsEnabled():
            self.ReglerScrollBar()
        
        if self.paused:
            self.datagen_thread.stop()
            self.redraw_timer.Stop()
            self.draw_plot()
            if self.fichier != None:
                self.fichier.close()
        else:
            self.initData()
            self.initTimer()

        self.datagen.Pause(self.paused)
            
    
    def on_update_pause_button(self, event):
        label = u"Reprise" if self.paused else u"Pause"
        self.pause_button.SetLabel(label)
    
    def on_cb_grid(self, event):
        self.draw_plot()
    
    def on_check_enregistrer(self, event):
        return
    
    def on_cb_xlab(self, event):
        self.draw_plot()
    
    def on_options(self, event):
        if not self.paused:
            self.on_pause_button()
            
        options = self.options.copie()

        dlg = Options.FenOptions(self, options)
        dlg.CenterOnScreen()
#        dlg.nb.SetSelection(page)

        val = dlg.ShowModal()
    
        if val == wx.ID_OK:
            self.DefinirOptions(options)
            self.AppliquerOptions(dlg.modif)
            self.datagen.Pause(True)
        else:
            pass
#            print "You pressed Cancel"

        dlg.Destroy()
        
#        if notpaused:
#            self.on_pause_button()
        
    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self,
            message= u"Enregistrer le tracé sous...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)
    
    
#    def on_datagen_timer(self, event):
#        if not self.paused:
#            if globdef.SIMPLE_PORT:
#                data = self.datagen.next_simple()
#            else:
#                data = self.datagen.next_multi()
#                
##            print data
#            if data == None:
#                data = [100]
##                self.DemanderLancerArduino()
#            self.t = time.time() - self.t0
#            print self.t
#            self.data.append((self.t*1000, data))
##            self.t += globdef.REFRESH_INTERVAL_MS
##            self.t += time.time() - self.time
#        
#        # Calcul approximatif du nombre de points correspondant à l'historique
#        n = int(1.*globdef.X_HISTORY/globdef.DATAGEN_INTERVAL_MS + 1)
#        self.data = self.data[-n:]
##        print self.data
        
        
    def on_redraw_timer(self, event):
#        print "on_redraw_timer"
        self.draw_plot()
        self.sauverCSV()
        self.AfficherRate()
    
    def sauverCSV(self):
        if self.cb_e.GetValue() and self.fichier != None:
            if globdef.TYPE_DATA == "CSV":
                self.fichier.write("\n".join(self.csv)+"\n")
                self.csv = []
    
    def on_exit(self, event):
        print 'on_exit'
        event.Skip()
        self.redraw_timer.Stop()
        self.datagen_thread.stop()
        self.datagen.Terminer()
        self.options.enregistrer()
        self.Destroy()
    
    
    def AfficherRate(self):
        try:
            if self.temps != []:
                t = np.array(self.temps)
                t1 = t[1:]
                t0 = t[:-1]
                t = t1-t0
                moy = np.average(t)
                msg = str(int(moy))+"ms"
                self.statusbar.SetStatusText(msg)
                self.temps = []
        except:
            pass
    
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER,
            self.on_flash_status_off,
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')

    def DefinirOptions(self, options):
        self.options = options.copie()
        #
        # Options Communication
        #
        globdef.BAUDRATE = self.options.optGenerales["Baudrate"]
        globdef.COM_PORT = self.options.optGenerales["Port"]
        globdef.DATAGEN_INTERVAL_MS = self.options.optGenerales["AcquisInterval"]
        globdef.ARDUINO_PATH = self.options.optGenerales["RepArduino"]
        globdef.ARDUINO_PORT = self.options.optGenerales["ArduinoPort"]
        globdef.SIMPLE_PORT = self.options.optGenerales["SimplePort"]
        globdef.TYPE_PORT = self.options.optGenerales["TypePort"]
        globdef.TYPE_DATA = self.options.optGenerales["TypeData"]
        
        
        #
        # Options Affichage
        #
        globdef.X_RANGE = self.options.optAffichage["XRange"]
        globdef.X_HISTORY = self.options.optAffichage["XHistory"]
        globdef.LINE_STYLE = self.options.optAffichage["LineStyle"]
        globdef.MARKER_STYLE = self.options.optAffichage["MarkerStyle"]
        globdef.REFRESH_INTERVAL_MS = self.options.optAffichage["RefreshInterval"]
#        globdef.X_MINself.optAffichage["Xmin"] = 
#        self.optAffichage["Xmax"] = globdef.X_MAX   
#        self.optAffichage["Ymin"] = globdef.Y_MIN
#        self.optAffichage["Ymax"] = globdef.Y_MAX
       
    #########################################################################################################
    def ReglerScrollBar(self):
        #
        # Réglage de la scrollbar
        #
        self.sb.SetScrollbar(globdef.X_HISTORY, globdef.X_RANGE, globdef.X_HISTORY, globdef.X_RANGE-1)
        
    #########################################################################################################
    def AppliquerOptions(self, modifCode = False):
        """ Procédure mettant en application toutes les options sauvegardées
        """
        if globdef.TYPE_PORT == "A":
            self.selectA.Enable(not globdef.SIMPLE_PORT, globdef.ARDUINO_PORT)
            self.selectN.Enable(not globdef.SIMPLE_PORT)
        else:
            self.selectA.Enable(not globdef.SIMPLE_PORT)
            self.selectN.Enable(not globdef.SIMPLE_PORT, globdef.ARDUINO_PORT)
        
        if globdef.SIMPLE_PORT:
            self.axes.set_title('ArduinoScope - port ' + globdef.TYPE_PORT + str(globdef.ARDUINO_PORT), size=12)
        else:
            self.axes.set_title('ArduinoScope', size=12)
        
        if self.sb.IsEnabled():
            self.ReglerScrollBar()
        
        if modifCode:
            if hasattr(self, 'datagen'):
                self.datagen.Terminer()
            lancerArduino(self)
        
        for i in range(16):
            self.plot_data[i].set_linestyle(globdef.LINE_STYLE)
            self.plot_data[i].set_marker(globdef.MARKER_STYLE)
        
        # Calcul approximatif du nombre de points correspondant à l'historique
        globdef.NBR_POINTS = int(1.*globdef.X_HISTORY/globdef.DATAGEN_INTERVAL_MS + 1)
        
        self.initSerial()
#        self.initTimer()
       
    #########################################################################################################
    def DemanderLancerArduino(self):
        self.on_pause_button()
        lancerArduino(self)

class ChannelChoiceBox(wx.Panel):
    """ Une staticBox pour selectionner les voies d'acquisition de l'Arduino
"""
    def __init__(self, parent, ID, label, nbr, listColor):
        wx.Panel.__init__(self, parent, ID)
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        self.listColor = listColor
        self.backGround = self.GetBackgroundColour()
        self.cb = []
        for i in range(nbr):
            self.cb.append(wx.CheckBox(self, -1, str(i)))
            r,v,b = listColor[i]
            self.cb[-1].SetForegroundColour(wx.Colour(r*255,v*255,b*255))
#            self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, self.cb[-1])
            sizer.Add(self.cb[-1], 0, wx.ALL, 5)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
        
    def GetValues(self):
        return [cb.GetValue() for cb in self.cb]
    
    def GetValue(self, num):
        return self.cb[num].GetValue()

    def Enable(self, etat, port = None):
        for i, cb in enumerate(self.cb):
            if etat:
                r,v,b = self.listColor[i]
                cb.SetForegroundColour(wx.Colour(r*255,v*255,b*255))
                cb.SetBackgroundColour(wx.Colour(0,0,0))
            else:
                cb.SetBackgroundColour(self.backGround)
                cb.SetForegroundColour(self.backGround)
#            cb.SetFont(wx.Font(10, wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ))
            cb.Enable(etat)
        if port != None:
            self.cb[port].SetBackgroundColour(wx.Colour(0,0,0))
            r,v,b = self.listColor[port]
            self.cb[port].SetForegroundColour(wx.Colour(r*255,v*255,b*255))

        self.Refresh()

class BoundControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
box. Allows to switch between an automatic mode and a
manual mode with an associated value.
"""
    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)
        
        self.value = initval
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        self.radio_auto = wx.RadioButton(self, -1,
            label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1,
            label="Manuel")
        self.manual_text = wx.TextCtrl(self, -1,
            size=(35,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)
        
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)
        
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
        
        sizer.Add(self.radio_auto, 0, wx.ALL, 5)
        sizer.Add(manual_box, 0, wx.ALL, 5)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())
    
    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()
    
    def is_auto(self):
        return self.radio_auto.GetValue()
        
    def manual_value(self):
        return self.value
    
    
def AjoutVariablesEnv():
    os.putenv('ARDUINO_PATH', globdef.ARDUINO_PATH)
    os.putenv('ARDUINO_MCU', globdef.ARDUINO_NAME)
    os.putenv('ARDUINO_PROGRAMMER', globdef.ARDUINO_PROG)
    os.putenv('ARDUINO_FCPU', globdef.ARDUINO_FCPU)
    os.putenv('ARDUINO_COMPORT', globdef.COM_PORT)
    os.putenv('ARDUINO_BURNRATE', str(globdef.BAUDRATE))


def BuildAndUpload():
#    script = globdef.CODE_ARDUINO %("CAN_PORT" : globdef.PORT,
#                                   "BAUDRATE" : str(globdef.BAUDRATE),
#                                   "DELAY" : str(globdef.REFRESH_INTERVAL_MS))
    
    if globdef.SIMPLE_PORT:
        script = globdef.CODE_ARDUINO1 %{"arport" : globdef.ARDUINO_PORT,
                                         "baudrate" : str(globdef.BAUDRATE),
                                         "delay" : str(globdef.REFRESH_INTERVAL_MS)}
    else:
        script = globdef.CODE_ARDUINO2 %{"baudrate" : str(globdef.BAUDRATE),
                                         "delay" : str(globdef.REFRESH_INTERVAL_MS)}
    
#    scriptfile = tempfile.TemporaryFile(suffix = '.pde')
    
    scriptfile = open("test.pde", 'w')
    try:
        scriptfile.write(script)
        subprocess.call('abuild.bat ' + scriptfile.name, shell=True)
    finally:
        # Automatically cleans up the file
        scriptfile.close()
    
#    scriptfile = tempfile.TemporaryFile([mode='w+b'[, bufsize=-1[, suffix=''[, prefix='tmp'[, dir=None]]]]])
    
    
    
    
##########################################################################################################
#
#  DirSelectorCombo
#
##########################################################################################################
class URLSelectorCombo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.SetMaxSize((-1,22))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.texte = wx.TextCtrl(self, -1, "", size = (-1, 16))
    
        bt2 =wx.BitmapButton(self, 101, wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))
        bt2.SetToolTipString(u"Sélectionner un fichier")
        self.Bind(wx.EVT_BUTTON, self.OnClick, bt2)
        self.Bind(wx.EVT_TEXT, self.EvtText, self.texte)
        
        sizer.Add(bt2)
        sizer.Add(self.texte,1,flag = wx.EXPAND)
        self.SetSizerAndFit(sizer)
        self.fichier = ""

    # Overridden from ComboCtrl, called when the combo button is clicked
    def OnClick(self, event):
        
        if event.GetId() == 100:
            dlg = wx.DirDialog(self, u"Sélectionner un dossier",
                          style=wx.DD_DEFAULT_STYLE,
                          defaultPath = self.pathseq
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )
            if dlg.ShowModal() == wx.ID_OK:
                self.SetPath(dlg.GetPath())
    
            dlg.Destroy()
        else:
            dlg = wx.FileDialog(self, u"Sélectionner un fichier",
                                wildcard = self.ext,
    #                           defaultPath = globdef.DOSSIER_EXEMPLES,
                               style = wx.DD_DEFAULT_STYLE
                               #| wx.DD_DIR_MUST_EXIST
                               #| wx.DD_CHANGE_DIR
                               )
    
            if dlg.ShowModal() == wx.ID_OK:
                self.SetPath(dlg.GetPath())
    
            dlg.Destroy()
        
        self.SetFocus()


    ##########################################################################################
    def EvtText(self, event):
        self.fichier = event.GetString()


    ##########################################################################################
    def GetPath(self):
        return self.fichier
    
    ##########################################################################################
    def SetPath(self, nom):
        self.fichier = nom
        self.texte.SetValue(nom)
  
    
def lancerArduino(app):
    
    dlg = wx.MessageDialog(app,  u"Téléversement du programme dans l'Arduino\n\n" \
                                 u"Depuis le programme Aduino qui vient de s'ouvrir,\n" \
                                 u"cliquer sur \"Téléverser\".\n" \
                                 u"Une fois le téléversement terminé\n" \
                                 u"fermer le programme Arduino.\n\n" \
                                 u"Ne pas fermer ce message avant !",
                                 u'Téléversement',
                                 wx.ICON_INFORMATION | wx.OK
                                 )
     
    if globdef.SIMPLE_PORT:
        if globdef.TYPE_PORT == "A":
            script = globdef.CODE_ARDUINO_SIMPLE_A %{"arport" : globdef.ARDUINO_PORT,
                                                     "baudrate" : str(globdef.BAUDRATE),
                                                     "delay" : str(globdef.DATAGEN_INTERVAL_MS)}
        else:
            script = globdef.CODE_ARDUINO_SIMPLE_N %{"arport" : globdef.ARDUINO_PORT,
                                                     "baudrate" : str(globdef.BAUDRATE),
                                                     "delay" : str(globdef.DATAGEN_INTERVAL_MS)}
    else:
        script = globdef.CODE_ARDUINO_MULTI %{"baudrate" : str(globdef.BAUDRATE),
                                              "delay" : str(globdef.DATAGEN_INTERVAL_MS)}
    
    path = tempfile.mkdtemp()
    nomscript = path.split("\\")[-1]+'.pde'
    
    scriptfile = open(os.path.join(path, nomscript), 'w')
    try:
        scriptfile.write(script)
        scriptfile.close()
        subprocess.call(os.path.join(globdef.ARDUINO_PATH, 'arduino.exe ') + scriptfile.name, shell=True)
    finally:
        # Automatically cleans up the file
        res = dlg.ShowModal()
        dlg.Destroy()
        os.remove(scriptfile.name)
        os.rmdir(path)


if __name__ == '__main__':
    app = wx.App()
    app.frame = GraphFrame()
    app.frame.Show()
    app.MainLoop()