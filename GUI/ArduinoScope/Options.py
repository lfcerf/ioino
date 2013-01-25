#!/usr/bin/env python
# -*- coding: utf-8 -*-

##This file is part of pyArduinoScope
#############################################################################
#############################################################################
##                                                                         ##
##                                   Options                               ##
##                                                                         ##
#############################################################################
#############################################################################

## Copyright (C) 2009-2012 Cédrick FAURY

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

import ConfigParser
import os.path
#import wx

import globdef
from widgets import VariableCtrl, Variable, VAR_ENTIER_POS, EVT_VAR_CTRL
import wx.combo

##############################################################################
#      Options     #
##############################################################################
class Options:
    """ Définit les options de PySyLic """
    def __init__(self, options = None):
        #
        # Toutes les options ...
        # Avec leurs valeurs par d�faut.
        #
        self.optAffichage = {}
        self.optCouleurs = {}
        self.optGenerales = {}
        self.optImpression = {}
        self.optCalcul = {}
        
        if options == None:
            self.defaut()
          
#        self.listeOptions = [u"Général", u"Affichage", u"Couleurs", u"Impression"] 
         
        self.typesOptions = {u"Communication" : self.optGenerales,
                             u"Affichage" : self.optAffichage,
#                             u"Calcul" : self.optCalcul,
#                             u"Formats de ligne" : self.optCouleurs,
#                             u"Impression" : self.optImpression,
                             }
        
        
        # Le fichier où seront sauvées les options
        self.fichierOpt = os.path.join(globdef.PATH, "ArduinoScope.cfg")

    #########################################################################################################
    def __repr__(self):
        t = "Options :\n"
        for o in self.optGenerales.items() + self.optAffichage.items() + self.optImpression.items() + self.optCouleurs.items():
            if type(o[1]) == int or type(o[1]) == float:
                tt = str(o[1])
            elif type(o[1]) == bool:
                tt = str(o[1])
            else:
#                print tt, type(tt)
                tt = o[1]
            t += "\t" + o[0] + " = " + tt +"\n"
        return t
    
    
    #########################################################################################################
    def fichierExiste(self):
        """ Vérifie si le fichier 'options' existe
        """
#        PATH=os.path.dirname(os.path.abspath(sys.argv[0]))
#        os.chdir(globdef.PATH)
        if os.path.isfile(self.fichierOpt):
            return True
        return False


    #########################################################################################################
    def enregistrer(self):
        """" Enregistre les options dans un fichier
        """
#        print "Enregistrement",self
        config = ConfigParser.ConfigParser()

        for titre,dicopt in self.typesOptions.items():
            titre = titre.encode('utf-8')
            config.add_section(titre)
            for opt in dicopt.items():
                config.set(titre, opt[0], opt[1])
        
        config.write(open(self.fichierOpt,'w'))



    ############################################################################
    def ouvrir(self):
        """ Ouvre un fichier d'options 
        """
        config = ConfigParser.ConfigParser()
        config.read(self.fichierOpt)
        print "ouverture :",self.fichierOpt
        for titre in self.typesOptions.keys():
            titreUtf = titre.encode('utf-8')
            for titreopt in self.typesOptions[titre].keys():
                opt = self.typesOptions[titre][titreopt] 
                
                if type(opt) == int:
                    opt = config.getint(titreUtf, titreopt)
                elif type(opt) == float:
                    opt = config.getfloat(titreUtf, titreopt)
                elif type(opt) == bool:
                    opt = config.getboolean(titreUtf, titreopt)
                elif type(opt) == str or type(opt) == unicode:
                    opt = config.get(titreUtf, titreopt)
                elif isinstance(opt, wx._gdi.Colour):
                    v = eval(config.get(titreUtf, titreopt))
                    opt = wx.Colour(v[0], v[1], v[2], v[3])
                
                self.typesOptions[titre][titreopt] = opt
                


    ############################################################################
    def copie(self):
        """ Retourne une copie des options """
        options = Options()
        for titre,dicopt in self.typesOptions.items():
            titre.encode('utf-8')
            nopt = {}
            for opt in dicopt.items():
                options.typesOptions[titre][opt[0]] = opt[1]
        return options
 
        
    ############################################################################
    def defaut(self):
        print "defaut"
        self.optGenerales["Baudrate"] = globdef.BAUDRATE
        self.optGenerales["Port"] = globdef.PORT
        self.optGenerales["AcquisInterval"] = globdef.DATAGEN_INTERVAL_MS
        self.optGenerales["RepArduino"] = globdef.ARDUINO_PATH
        self.optGenerales["ArduinoPort"] = globdef.ARDUINO_PORT
        self.optGenerales["SimplePort"] = globdef.SIMPLE_PORT
        self.optGenerales["TypePort"] = globdef.TYPE_PORT
        
        
        self.optAffichage["RefreshInterval"] = globdef.REFRESH_INTERVAL_MS
        self.optAffichage["Xmin"] = globdef.X_MIN
        self.optAffichage["Xmax"] = globdef.X_MAX   
        self.optAffichage["Ymin"] = globdef.Y_MIN
        self.optAffichage["Ymax"] = globdef.Y_MAX
        
        self.optAffichage["XRange"] = globdef.X_RANGE
        self.optAffichage["XHistory"] = globdef.X_HISTORY
        self.optAffichage["LineStyle"] = globdef.LINE_STYLE
        self.optAffichage["MarkerStyle"] = globdef.MARKER_STYLE

     

    ###########################################################################
    def extraireRepertoire(self,chemin):
        for i in range(len(chemin)):
            if chemin[i] == "/":
                p = i
        self.repertoireCourant = chemin[:p+1]
        return chemin[:p+1]
        
        
        
##############################################################################
#     Fen�tre Options     #
##############################################################################
class FenOptions(wx.Dialog):
#   "Fen�tre des options"      
    def __init__(self, parent, options):
        wx.Dialog.__init__(self, parent, -1, u"Options de pyArduinoScope")
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.options = options
        self.parent = parent
        
        self.modif = False
        
        
        #
        # Le book ...
        #
        nb = wx.Notebook(self, -1)
        nb.AddPage(pnlGenerales(nb, options.optGenerales), u"Communication")
        nb.AddPage(pnlAffichage(nb, options.optAffichage), u"Affichage")
        nb.SetMinSize((400,-1))
        sizer.Add(nb, flag = wx.EXPAND)#|wx.ALL)
        self.nb = nb
        
        #
        # Les boutons ...
        #
        btnsizer = wx.StdDialogButtonSizer()
        
        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)
        
        btn = wx.Button(self, wx.ID_OK)
        help = u"Valider les changements apportés aux options"
        btn.SetToolTip(wx.ToolTip(help))
        btn.SetHelpText(help)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        help = u"Annuler les changements et garder les options comme auparavant"
        btn.SetToolTip(wx.ToolTip(help))
        btn.SetHelpText(help)
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        
        btn = wx.Button(self, -1, u"Défaut")
        help = u"Rétablir les options par défaut"
        btn.SetToolTip(wx.ToolTip(help))
        btn.SetHelpText(help)
        self.Bind(wx.EVT_BUTTON, self.OnClick, btn)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(btn)
        bsizer.Add(btnsizer, flag = wx.EXPAND|wx.ALIGN_RIGHT)
        
        sizer.Add(bsizer, flag = wx.EXPAND)#|wx.ALL)
        self.SetMinSize((400,-1))
#        print self.GetMinSize()
#        self.SetSize(self.GetMinSize())
        self.SetSizerAndFit(sizer)
        
    def OnClick(self, event):
        self.options.defaut()
        
        for np in range(self.nb.GetPageCount()):
            
            p = self.nb.GetPage(np)
#            print "   ",p
            for c in p.GetChildren():
#                print c
                c.Destroy()
#            p.DestroyChildren()
#            print p.GetSizer().GetChildren()
            p.CreatePanel()
            p.Layout()
        
        
        
#############################################################################################################
class pnlGenerales(wx.Panel):
    def __init__(self, parent, optGene):
        
        wx.Panel.__init__(self, parent, -1)
        
        self.opt = optGene
        
        self.CreatePanel()

    
    def CreatePanel(self):
        
        self.ns = wx.BoxSizer(wx.VERTICAL)
        
        #
        # Connexion : Ports COM et Baudrate
        #
        sb0 = wx.StaticBox(self, -1, u"Connexion", size = (200,-1))
        sbs0 = wx.StaticBoxSizer(sb0,wx.VERTICAL)
        
        listPorts = [n+' '+d for n,d in globdef.Ports]
        cb = wx.ComboBox(self, -1, globdef.PORT, size = (40, -1), 
                         choices = listPorts,
                         style = wx.CB_DROPDOWN|wx.CB_READONLY)
        cb.SetToolTip(wx.ToolTip(u"Choisir le port de communication"))
        sbs0.Add(cb, flag = wx.EXPAND|wx.ALL, border = 5)
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxP, cb)
        
        cb = wx.ComboBox(self, -1, str(globdef.BAUDRATE), size = (40, -1), 
                         choices = globdef.BaudRate,
                         style = wx.CB_DROPDOWN|wx.CB_READONLY)
        cb.SetToolTip(wx.ToolTip(u"Choisir le Baudrate"))
        sbs0.Add(cb, flag = wx.EXPAND|wx.ALL, border = 5)
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxB, cb)
        self.ns.Add(sbs0, flag = wx.EXPAND|wx.ALL)
        
        #
        # coté Arduino
        #
        sb1 = wx.StaticBox(self, -1, u"Arduino", size = (200,-1))
        sbs1 = wx.StaticBoxSizer(sb1,wx.VERTICAL)
        self.ncp = Variable(u'Période (ms)', 
                            lstVal = globdef.DATAGEN_INTERVAL_MS, 
                            typ = VAR_ENTIER_POS, bornes = [1,1000])
        vc2 = VariableCtrl(self, self.ncp, coef = 1, labelMPL = False, signeEgal = False,
                          help = u"Période de l'acquisition (ms)", sizeh = 60)
        self.Bind(EVT_VAR_CTRL, self.EvtVariable, vc2)
        sbs1.Add(vc2, flag = wx.EXPAND|wx.ALL, border = 5)
        self.ns.Add(sbs1, flag = wx.EXPAND|wx.ALL)
        
        
        ts = wx.StaticText(self, -1, u"Dossier Arduino")
        fs = DirSelectorCombo(self, -1)
        fs.SetValueWithEvent(self.opt["RepArduino"])
        fs.SetToolTip(wx.ToolTip(u"Permet de selectionner le dossier\n" \
                                   u"où se trouve l'application arduino.exe"))
        
        ss = wx.BoxSizer(wx.HORIZONTAL)
        ss.Add(ts, flag = wx.ALIGN_CENTER)
        ss.Add(fs, 1, flag = wx.EXPAND|wx.ALL, border = 3)
        sbs1.Add(ss, flag = wx.EXPAND|wx.ALL, border = 5)
        fs.Bind(wx.EVT_TEXT, self.EvtComboCtrl)
        
        sb2 = wx.StaticBox(self, -1, u"Port E/S", size = (-1,-1))
        sbs2 = wx.StaticBoxSizer(sb2,wx.VERTICAL)
        self.radio_multi = wx.RadioButton(self, -1,
            label="Multi port", style=wx.RB_GROUP)
        self.radio_simple = wx.RadioButton(self, -1,
            label="Simple port")
        self.radio_simple.SetValue(globdef.SIMPLE_PORT)
        
        sbs2.Add(self.radio_multi, flag = wx.EXPAND|wx.ALL, border = 2)
        sbs2.Add(self.radio_simple, flag = wx.EXPAND|wx.ALL, border = 2)
        
        self.radio_ana = wx.RadioButton(self, -1,
            label=u"Analogique", style=wx.RB_GROUP)
        self.radio_num = wx.RadioButton(self, -1,
            label=u"Numérique")
        self.radio_ana.Enable(globdef.SIMPLE_PORT)
        self.radio_num.Enable(globdef.SIMPLE_PORT)
        
        sbs2.Add(self.radio_ana, flag = wx.EXPAND|wx.ALL, border = 2)
        sbs2.Add(self.radio_num, flag = wx.EXPAND|wx.ALL, border = 2)
        
        v = Variable(u'Port E/S', 
                            lstVal = globdef.ARDUINO_PORT, 
                            typ = VAR_ENTIER_POS, bornes = [0,9])
        vc2 = VariableCtrl(self, v, coef = 1, labelMPL = False, signeEgal = False,
                          help = u"Choisir le port E/S de l'Arduino", sizeh = 30)
        vc2.Enable(globdef.SIMPLE_PORT)
        
        
        self.Bind(wx.EVT_RADIOBUTTON, self.on_multi_simple, self.radio_multi)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_ana_num, self.radio_num)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_multi_simple, self.radio_simple)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_ana_num, self.radio_ana)
        self.Bind(EVT_VAR_CTRL, self.EvtVariableP, vc2)
        self.vc = vc2
        sbs2.Add(vc2, flag = wx.EXPAND|wx.ALL, border = 5)
        
        sbs1.Add(sbs2, flag = wx.EXPAND|wx.ALL, border = 5)
        
        self.SetSizerAndFit(self.ns)
    
 
    def on_multi_simple(self, event):
        self.vc.Enable(self.radio_simple.GetValue())
        self.radio_ana.Enable(self.radio_simple.GetValue())
        self.radio_num.Enable(self.radio_simple.GetValue())
        self.opt["SimplePort"] = self.radio_simple.GetValue()
        self.Parent.Parent.modif = True
        
#    def on_portAuto(self, event):
#        self.cbPort.Enable(self.radio_portManu.GetValue())
#        self.opt["SimplePort"] = self.radio_simple.GetValue()
#        self.Parent.Parent.modif = True
        
    def on_ana_num(self, event):
        if self.radio_ana.GetValue():
            self.opt["TypePort"] = "A"
            self.vc.SetBornes((0, 5))
        else:
            self.opt["TypePort"] = "N"
            self.vc.SetBornes((0, 10))
        
        self.Parent.Parent.modif = True
        
    def EvtComboBoxB(self, event):
        cb = event.GetEventObject()
        data = cb.GetValue()
        self.opt["Baudrate"] = eval(data)
        self.Parent.Parent.modif = True
        
    def EvtComboBoxP(self, event):
        cb = event.GetEventObject()
        data = cb.GetValue()
        self.opt["Port"] = data.split()[0]
        
        
    def EvtVariable(self, event):
        self.opt["AcquisInterval"] = event.GetVar().v[0]
        self.Parent.Parent.modif = True


    def EvtVariableP(self, event):
        self.opt["ArduinoPort"] = event.GetVar().v[0]
        self.Parent.Parent.modif = True
        
    def EvtComboCtrl(self, event):
        self.opt["RepArduino"] = event.GetEventObject().GetValue()
        self.Parent.Parent.modif = True

#######################################################################################################
class pnlAffichage(wx.Panel):
    def __init__(self, parent, optAffichage):
        
        wx.Panel.__init__(self, parent, -1)
        
        self.opt = optAffichage
        
        self.CreatePanel()
        
        
    def CreatePanel(self):
        
        self.ns = wx.BoxSizer(wx.VERTICAL)
        
        # 
        # Axe du temps
        #
        sb3 = wx.StaticBox(self, -1, u"Axe du temps")
        sbs3 = wx.StaticBoxSizer(sb3, wx.VERTICAL)
        
#        self.vi = Variable(u'Intervalle (ms)', 
#                            lstVal = globdef.X_RANGE, 
#                            typ = VAR_ENTIER_POS, bornes = [1,1000000])
#        vc1 = VariableCtrl(self, self.vi, coef = 1, labelMPL = False, signeEgal = False,
#                          help = u"Intervalle de l'axe du temps (ms)")
#        self.Bind(EVT_VAR_CTRL, self.EvtVariableR, vc1)
#        
#        sbs3.Add(vc1, flag = wx.EXPAND|wx.ALL, border = 5)


        self.vh = Variable(u'Historique (ms)', 
                            lstVal = globdef.X_HISTORY, 
                            typ = VAR_ENTIER_POS, bornes = [1,1000000])
        vc2 = VariableCtrl(self, self.vh, coef = 1, labelMPL = False, signeEgal = False,
                          help = u"Historique des données (ms)")
        self.Bind(EVT_VAR_CTRL, self.EvtVariableH, vc2)
        
        sbs3.Add(vc2, flag = wx.EXPAND|wx.ALL, border = 5)
        
        self.ns.Add(sbs3, flag = wx.EXPAND)

        #
        # Rafraichissement de l'affichage
        #
        sb2 = wx.StaticBox(self, -1, u"Raffraichissement")
        sbs2 = wx.StaticBoxSizer(sb2, wx.VERTICAL)
        
        self.ncp = Variable(u'Période (ms)', 
                            lstVal = globdef.REFRESH_INTERVAL_MS, 
                            typ = VAR_ENTIER_POS, bornes = [1,1000])
        vc2 = VariableCtrl(self, self.ncp, coef = 1, labelMPL = False, signeEgal = False,
                          help = u"Période de rafraichissement (ms)", sizeh = 60)
        self.Bind(EVT_VAR_CTRL, self.EvtVariable, vc2)
        sbs2.Add(vc2, flag = wx.EXPAND|wx.ALL, border = 5)
        self.ns.Add(sbs2, flag = wx.EXPAND)
        
        # 
        # style de ligne
        #
        sb0 = wx.StaticBox(self, -1, u"Style de ligne")
        sbs0 = wx.StaticBoxSizer(sb0, wx.VERTICAL)
        
        ts = wx.StaticText(self, -1, u"Ligne")
        cb = wx.ComboBox(self, -1, globdef.LINE_STYLE, size = (60, -1), 
                         choices = globdef.LineStyles,
                         style = wx.CB_DROPDOWN|wx.CB_READONLY)
        cb.SetToolTip(wx.ToolTip(u"Style de la Ligne"))
        
        bs1 = wx.BoxSizer(wx.HORIZONTAL)
        bs1.Add(ts, flag = wx.EXPAND|wx.ALL, border = 5)
        bs1.Add(cb, flag = wx.EXPAND|wx.ALL, border = 5)
        sbs0.Add(bs1, flag = wx.EXPAND|wx.ALL, border = 5)
        
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxL, cb)
        
        ts = wx.StaticText(self, -1, u"Points")
        cb = wx.ComboBox(self, -1, globdef.MARKER_STYLE, size = (60, -1), 
                         choices = globdef.MarkerStyles,
                         style = wx.CB_DROPDOWN|wx.CB_READONLY)
        cb.SetToolTip(wx.ToolTip(u"Style des Points"))
        
        bs1 = wx.BoxSizer(wx.HORIZONTAL)
        bs1.Add(ts, flag = wx.EXPAND|wx.ALL, border = 5)
        bs1.Add(cb, flag = wx.EXPAND|wx.ALL, border = 5)
        sbs0.Add(bs1, flag = wx.EXPAND|wx.ALL, border = 5)
        
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBoxP, cb)
        
        self.ns.Add(sbs0, flag = wx.EXPAND)
        self.SetSizerAndFit(self.ns)
        
    
    def OnRadio(self, event):
        radio = event.GetId() - 100
        self.opt["FONT_TYPE"] = radio
         
    def EvtVariable(self, event):
        self.opt["RefreshInterval"] = event.GetVar().v[0]
        
        
    def EvtVariableH(self, event):
        self.opt["XHistory"] = self.vh.v[0]
   
    def EvtComboBoxL(self, event):
        cb = event.GetEventObject()
        data = cb.GetValue()
        self.opt["LineStyle"] = data
        
    def EvtComboBoxP(self, event):
        cb = event.GetEventObject()
        data = cb.GetValue()
        self.opt["MarkerStyle"] = data
        

#############################################################################################################
class pnlImpression(wx.Panel):
    def __init__(self, parent, opt):
        
        wx.Panel.__init__(self, parent, -1)
        
        self.opt = opt
        
        
        
        self.CreatePanel()
        
        
        
    def CreatePanel(self):
        
        self.ns = wx.BoxSizer(wx.VERTICAL)
        #
        # Mise en page
        #
        sb1 = wx.StaticBox(self, -1, _(u"Mise en page"), size = (200,-1))
        sbs1 = wx.StaticBoxSizer(sb1,wx.VERTICAL)
        cb2 = wx.CheckBox(self, -1, _(u"Garder les proportions de l'�cran"))
        cb2.SetToolTip(wx.ToolTip(_(u"Si cette case est coch�e, les trac�s imprim�s\n"\
                                    u"auront les m�mes proportions (largeur/hauteur) qu'� l'�cran.")))
        cb2.SetValue(self.opt["PRINT_PROPORTION"])
        sbs1.Add(cb2, flag = wx.EXPAND|wx.ALL, border = 5)
        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, cb2)
        self.ns.Add(sbs1, flag = wx.EXPAND|wx.ALL)
        
        #
        # Elements � imprimer
        #
        sb2 = wx.StaticBox(self, -1, _(u"El�ments � imprimer"), size = (200,-1))
        sbs2 = wx.StaticBoxSizer(sb2,wx.VERTICAL)
        sup = u"\n"+_(u"En d�cochant cette case, vous pouvez choisir un texte personnalis�")
        selTitre = selecteurTexteEtPosition(self, _(u"Nom du fichier syst�me"),
                                            self.Parent.Parent.Parent.fichierCourant,
                                            _(u"Nom de fichier sous lequel le syst�me actuel est sauvegard�")+sup,
                                            "IMPRIMER_TITRE", "POSITION_TITRE", "TEXTE_TITRE")
        selNom = selecteurTexteEtPosition(self, _(u"Nom de l'utilisateur"),
                                            globdef.NOM,
                                            _(u"Nom de l'utilisateur de l'ordinateur")+sup,
                                            "IMPRIMER_NOM", "POSITION_NOM", "TEXTE_NOM")
        sbs2.Add(selTitre, flag = wx.EXPAND|wx.ALL, border = 5)
        sbs2.Add(selNom, flag = wx.EXPAND|wx.ALL, border = 5)
        self.ns.Add(sbs2, flag = wx.EXPAND|wx.ALL)
        
        #
        # Qualit� de l'impression
        #
        sb3 = wx.StaticBox(self, -1, _(u"Qualit� de l'impression"), size = (200,-1))
        sbs3 = wx.StaticBoxSizer(sb3,wx.VERTICAL)
        hs = wx.BoxSizer(wx.HORIZONTAL)
        ttr = wx.StaticText(self, -1, _(u"R�solution de l'impression :"))
        cb = wx.ComboBox(self, -1, str(self.opt["MAX_PRINTER_DPI"]), size = (80, -1), 
                         choices = ['100', '200', '300', '400', '500', '600'],
                         style = wx.CB_DROPDOWN|wx.CB_READONLY)
        help = _(u"Ajuster la r�solution de l'impression.\n"\
                 u"Attention, une r�solution trop �lev�e peut augmenter\n"\
                 u"significativement la dur�e de l'impression.")
        cb.SetToolTipString(help)
        ttr.SetToolTipString(help)
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, cb)
        hs.Add(ttr, flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL, border = 4)
        hs.Add(cb, flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL, border = 4)
        sbs3.Add(hs, flag = wx.EXPAND|wx.ALL, border = 5)
        self.ns.Add(sbs3, flag = wx.EXPAND|wx.ALL)
        
        self.SetSizerAndFit(self.ns)
    
    def EvtComboBox(self, event):
        cb = event.GetEventObject()
        data = cb.GetValue()
        self.opt["MAX_PRINTER_DPI"] = eval(data)
        
    def EvtCheckBox(self, event):
        self.opt["PRINT_PROPORTION"] = event.GetEventObject().GetValue()
        


class selecteurTexteEtPosition(wx.Panel):
    def __init__(self, parent, titre, textedefaut, tooltip, impoption, posoption, txtoption, ctrl = True):
        wx.Panel.__init__(self, parent, -1)
        
        self.impoption = impoption
        self.posoption = posoption
        self.txtoption = txtoption
        self.textedefaut = textedefaut
        
        self.lstPos = ["TL","TC","TR","BL","BC","BR"]
        tooltips = [_(u"En haut � gauche"), _(u"En haut au centre"), _(u"En haut � droite"),
                   _(u"En bas � gauche"), _(u"En bas au centre"), _(u"En bas � droite")]
        #
        # Le titre
        #
        self.titre = wx.CheckBox(self, -1, titre)
        self.titre.SetValue(self.Parent.opt[self.impoption])
        self.titre.SetToolTip(wx.ToolTip(tooltip))
        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, self.titre)
        
        #
        # Le texte � afficher
        #
        if not self.Parent.opt[self.impoption]:
            txt = self.Parent.opt[self.txtoption]
        else:
            txt = self.textedefaut
            
        if ctrl:
#            print self.Parent.opt[self.txtoption]
            self.texte = wx.TextCtrl(self, -1, txt)
            self.Bind(wx.EVT_TEXT, self.EvtText, self.texte)
        else:
            self.texte = wx.StaticText(self, -1, txt)
        self.texte.Enable(not self.Parent.opt[self.impoption])
            
        #
        # La position
        #
        radio = []
        box1_title = wx.StaticBox(self, -1, _(u"position") )
        box1 = wx.StaticBoxSizer( box1_title, wx.VERTICAL )
        grid1 = wx.BoxSizer(wx.HORIZONTAL)
        radio.append(wx.RadioButton(self, 101, "", style = wx.RB_GROUP ))
        radio.append(wx.RadioButton(self, 102, "" ))
        radio.append(wx.RadioButton(self, 103, "" ))
        for r in radio:
            grid1.Add(r)
        box1.Add(grid1)
        
        img = wx.StaticBitmap(self, -1, Images.Zone_Impression.GetBitmap())
        img.SetToolTip(wx.ToolTip(_(u"Choisir ici la position du texte par rapport aux trac�s")))
        box1.Add(img)
        
        grid2 = wx.BoxSizer(wx.HORIZONTAL)
        radio.append(wx.RadioButton(self, 104, "" ))
        radio.append(wx.RadioButton(self, 105, "" ))
        radio.append(wx.RadioButton(self, 106, "" ))
        for r in radio[3:]:
            grid2.Add(r)
        box1.Add(grid2)
        
        for i, r in enumerate(radio):
            r.SetToolTip(wx.ToolTip(tooltips[i]))
            self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, r)
        
        self.radio = self.lstPos.index(self.Parent.opt[self.posoption])
        for i, r in enumerate(radio):
            if i == self.radio:
                r.SetValue(True)
            else:
                r.SetValue(False)
        
#        sizerV = wx.BoxSizer(wx.VERTICAL)
#        sizerV.Add(box1)
#        sizerV.Add(img)
#        sizerV.Add(box2)
        
#        posList = [" "," "," "," "," "," "]
#        rb = wx.RadioBox(self, -1, _(u"position"), wx.DefaultPosition, wx.DefaultSize,
#                         posList, 2, wx.RA_SPECIFY_ROWS)
#        self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox, rb)
#        try:
#            rb.SetSelection(self.lstPos.index(self.Parent.opt[self.posoption]))
#        except:
#            pass
#        self.rb = rb
#        self.rb.Enable(self.titre.GetValue())
        
        
        #
        # Mise en place
        #
        sizerG = wx.BoxSizer(wx.VERTICAL)
        sizerG.Add(self.titre, flag = wx.EXPAND)
        sizerG.Add(self.texte, flag = wx.EXPAND|wx.ALL, border = 15)
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(sizerG, 1, flag = wx.EXPAND)
        self.sizer.Add(box1, flag = wx.EXPAND|wx.ALIGN_LEFT)
        self.SetSizer(self.sizer)
        self.sizer.Fit( self )
        
    def OnRadio(self, event):
        self.radio = event.GetId()-101
        self.Parent.opt[self.posoption] = self.lstPos[self.radio]
#        print self.radio
    
#    def EvtRadioBox(self, event):
#        p = event.GetInt()
#        self.Parent.opt[self.posoption] = self.lstPos[p]
        
    def EvtText(self, event):
        txt = event.GetString()
        self.Parent.opt[self.txtoption] = txt
        
    def EvtCheckBox(self, event):
        self.Parent.opt[self.impoption] = event.GetEventObject().GetValue()
        self.texte.Enable(not self.Parent.opt[self.impoption])
        
#        self.Parent.opt[self.posoption] = self.lstPos[self.radio]
        
    
        if not self.Parent.opt[self.impoption]:
            self.Parent.opt[self.txtoption] = self.texte.GetValue()
            self.texte.SetValue(self.Parent.opt[self.txtoption])    
        else:
            self.texte.SetValue(self.textedefaut)
            self.Parent.opt[self.txtoption] = ""
            
        
#        self.rb.Enable(event.GetEventObject().GetValue())
            
#class pnlImpression(wx.Panel):
#    def __init__(self, parent, opt):
#        wx.Panel.__init__(self, parent, -1)
#        ns = wx.BoxSizer(wx.VERTICAL)
#        self.opt = opt
#        
#        sb1 = wx.StaticBox(self, -1, u"Contenu du rapport", size = (200,-1))
#        sbs1 = wx.StaticBoxSizer(sb1,wx.VERTICAL)
#        tree = ChoixRapportTreeCtrl(self, self.opt)
#        sbs1.Add(tree, flag = wx.EXPAND|wx.ALL, border = 5)
#        
##        print tree.GetVirtualSize()[1], tree.GetBestSize()[1]
#        
#        cb2 = wx.CheckBox(self, -1, u"Demander ce qu'il faut inclure � chaque cr�ation de rapport")
#        cb2.SetValue(self.opt["DemanderImpr"])
#        
#        sbs1.Add(cb2, flag = wx.EXPAND|wx.ALL, border = 5)
#        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, cb2)
#        
#        ns.Add(sbs1, flag = wx.EXPAND|wx.ALL)
#        self.SetSizerAndFit(ns)
#        sb1.SetMinSize((-1, 130))
#        
##    def EvtComboCtrl(self, event):
##        self.opt["FichierMod"] = event.GetEventObject().GetValue()
#    
#    def EvtCheckBox(self, event):
#        self.opt["DemanderImpr"] = event.IsChecked()
#     
#class pnlAnalyse(wx.Panel):
#    def __init__(self, parent, options):
#        wx.Panel.__init__(self, parent, -1)
#        ns = wx.BoxSizer(wx.VERTICAL)
#        self.options = options
#        
#        sb1 = wx.StaticBox(self, -1, u"Outils visuels d'analyse")
#        sbs1 = wx.StaticBoxSizer(sb1,wx.VERTICAL)
#        
#        label = {"AnimMontage"  : u"Proposer l'animation du d�montage/remontage",
#                 "AnimArrets"   : u"Proposer l'animation du manque d'arr�t axial",
#                 "ChaineAction" : u"Proposer le trac� des cha�nes d'action"}
#
#        self.cb = {}
#        for titre, opt in options.items():
#            c = wx.CheckBox(self, -1, label[titre])
#            self.cb[c.GetId()] = titre
#            c.SetValue(opt)
#            self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, c)
#            sbs1.Add(c, flag = wx.ALL, border = 5)
#        
#        ns.Add(sbs1, flag = wx.EXPAND)
#
#        self.SetSizerAndFit(ns)
#
#    def EvtCheckBox(self, event):
#        self.options[self.cb[event.GetId()]] = event.IsChecked()
        
class pnlCouleurs(wx.Panel):
    """ Dialog de selection d'un format de ligne
        <format> = liste : [couleur, style, �paisseur]
    """
    def __init__(self, parent, opt):
        wx.Panel.__init__(self, parent, -1)
        
        self.opt = opt
        
        lstIDCoul = ["COUL_POLES", "COUL_PT_CRITIQUE", "COUL_MARGE_OK", "COUL_MARGE_NO"]
        
        lstIDForm = ["FORM_GRILLE", "FORM_ISOGAIN", "FORM_ISOPHASE"]

        self.lstIDCoul = lstIDCoul
        self.lstIDForm = lstIDForm
        
        self.CreatePanel()
        
        
        
    def CreatePanel(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        nomCouleurs = {"COUL_MARGE_OK"      : _(u'Marge de stabilit� "valide"'),
                       "COUL_MARGE_NO"      : _(u'Marge de stabilit� "non valide"'),
                       "COUL_POLES"         : _(u'P�les'),
                       "COUL_PT_CRITIQUE"   : _(u'Point critique et Courbe "lambda"')
                        }
        
        nomFormatLigne  = {"FORM_GRILLE"        : _(u'Grille'),
                           "FORM_ISOGAIN"       : _(u'Courbe "isogain"'),
                           "FORM_ISOPHASE"      : _(u'Courbe "isophase"')
                           }
        
        self.lstButton = {}
        for i, k in enumerate(self.lstIDCoul):
            sizerH = wx.BoxSizer(wx.HORIZONTAL)
            txtColor = wx.StaticText(self, i+100, nomCouleurs[k])
            selColor = wx.Button(self, i, "", size = (80,22))
            selColor.SetToolTipString(_(u"Modifier la couleur de l'�l�ment") + " :\n" + nomCouleurs[k])
            selColor.SetBackgroundColour(self.opt[k])
            
            sizerH.Add(txtColor, flag = wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, border = 5)
            sizerH.Add(selColor, flag = wx.ALIGN_LEFT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, border = 5)
            self.sizer.Add(sizerH, flag = wx.ALIGN_RIGHT|wx.ALL)
            
            self.lstButton[k] = selColor
            self.Bind(wx.EVT_BUTTON, self.OnClick, id = i)
    
        for i, k in enumerate(self.lstIDForm):
            sizerH = wx.BoxSizer(wx.HORIZONTAL)
            txtColor = wx.StaticText(self, i+100, nomFormatLigne[k])
            selColor = SelecteurFormatLigne(self, i+len(self.lstIDCoul), self.opt[k], 
                                            _(u"Modifier le format de ligne de l'�l�ment") + " :\n" + nomFormatLigne[k],
                                            size = (80,22))
            
            sizerH.Add(txtColor, flag = wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, border = 5)
            sizerH.Add(selColor, flag = wx.ALIGN_LEFT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, border = 5)
            self.sizer.Add(sizerH, flag = wx.ALIGN_RIGHT|wx.ALL)
            
            self.lstButton[k] = selColor
            self.Bind(EVT_FORMAT_MODIFIED, self.OnFormatModified)
            
        self.SetSizer(self.sizer)
        
    ###############################################################################################
    def OnFormatModified(self, event = None):    
        return
        
    ###############################################################################################
    def OnClick(self, event = None):      
        id = event.GetId()
        colourData = wx.ColourData()
        colourData.SetColour(wx.NamedColour(self.opt[self.lstIDCoul[id]]))
        dlg = wx.ColourDialog(self, colourData)

        # Ensure the full colour dialog is displayed, 
        # not the abbreviated version.
        dlg.GetColourData().SetChooseFull(True)

        if dlg.ShowModal() == wx.ID_OK:

            # If the user selected OK, then the dialog's wx.ColourData will
            # contain valid information. Fetch the data ...

            self.opt[self.lstIDCoul[id]] = dlg.GetColourData().GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
            self.lstButton[self.lstIDCoul[id]].SetBackgroundColour(self.opt[self.lstIDCoul[id]])
#            print self.opt[self.lstID[id]]
            
        # Once the dialog is destroyed, Mr. wx.ColourData is no longer your
        # friend. Don't use it again!
        dlg.Destroy()
        return
    
    
#class nbOptions(wx.Notebook):
#    def __init__(self, parent, options):
#        wx.Notebook.__init__(self, parent, -1)
#        
#        self.AddPage(pnlGenerales(self, options.optGenerales), _(u"G�n�ral"))
#        self.AddPage(pnlAffichage(self, options.optAffichage), _(u"Affichage"))
##        self.AddPage(pnlImpression(self, options.optImpression), u"Rapport")
##        self.AddPage(pnlAnalyse(self, options.optAnalyse), u"Analyse")
#        self.SetMinSize((350,-1))
            
##########################################################################################################
#
#  DirSelectorCombo
#
##########################################################################################################
class DirSelectorCombo(wx.combo.ComboCtrl):
    def __init__(self, *args, **kw):
        wx.combo.ComboCtrl.__init__(self, *args, **kw)

        # make a custom bitmap showing "..."
        bw, bh = 14, 16
        bmp = wx.EmptyBitmap(bw,bh)
        dc = wx.MemoryDC(bmp)

        # clear to a specific background colour
        bgcolor = wx.Colour(255,254,255)
        dc.SetBackground(wx.Brush(bgcolor))
        dc.Clear()

        # draw the label onto the bitmap
        label = "..."
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        tw,th = dc.GetTextExtent(label)
        dc.DrawText(label, (bw-tw)/2, (bw-tw)/2)
        del dc

        # now apply a mask using the bgcolor
        bmp.SetMaskColour(bgcolor)

        # and tell the ComboCtrl to use it
        self.SetButtonBitmaps(bmp, True)
        

    # Overridden from ComboCtrl, called when the combo button is clicked
    def OnButtonClick(self):
        # In this case we include a "New directory" button. 
#        dlg = wx.FileDialog(self, "Choisir un fichier mod�le", path, name,
#                            "Rich Text Format (*.rtf)|*.rtf", wx.FD_OPEN)
        dlg = wx.DirDialog(self, "Choisir un dossier",
                           defaultPath = globdef.ARDUINO_PATH,
                           style = wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )

        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it. 
        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue(dlg.GetPath())

        # Only destroy a dialog after you're done with it.
        dlg.Destroy()
        
        self.SetFocus()

    # Overridden from ComboCtrl to avoid assert since there is no ComboPopup
    def DoSetPopupControl(self, popup):
        pass




