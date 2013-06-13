# -*- coding: utf8 -*-
#-------------------------------------------------------------------------------
# Name:        Nachfragemodell anwerfen und Nachfragematrizen ausgeben
# Purpose:
#
# Author:      Nina Kohnen
#
# Created:     03.04.2013
# Copyright:   (c) Barcelona 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import numpy
import tables
import VisumPy
import os
import sys
import time
import subprocess
import VisumPy.AddIn
from VisumPy.helpers import GetMatrix , SetMatrix
from tables.exceptions import NoSuchNodeError
##from simcommon.helpers import latinize
import win32api as win

def Run(param):
    #get parameter
    h5 = param["hdf5_save"] 
    modelsplit = param["modelsplit"] 
    #iv = param["iv"] 
        # HDF5 Filepaths
    kenn = param["Kenngrößenmatrizen"] 
    struktur = param["Strukturdaten"] 
    szenario = param["Szenario"] 
        # Speichern
    name = param["Name"] 
    #savepath = param["Savepath"] 

    if param["hdf5_save"]:
        # call AddIN Kenngrößen berechnen
        operations = Visum.Procedures.Operations
        op = operations.AddOperation(1)
        op.SetAttValue('OperationType', 84)  # 84 = AddIn aber noch nicht defniert welches???
        opa = op.AddInParameters
        opa.SetAttValue('AddInID', 'GGR_CALCSAVESKIM')


    # Nachfragemodell aufrufen
    cmd = r'C:\Anaconda\python C:\Dev\elan\tdm\src\tdm\tdmks\simulation_steps.py'
    cmd_name = '-n %s' %param["Name"]
    #save path?
    cmd_zonal = '--zd %s' %param["Strukturdaten"]
    cmd_put = '--put %s' %param["Kenngrößenmatrizen"]
    cmd_prt = '--prt %s' %param["Szenario"]
    if param['modelsplit']:
        cmd_cal = '-c'
    else:cmd_cal=''
    
    full_cmd = ' '.join([cmd, cmd_name, cmd_zonal, cmd_put, cmd_prt,cmd_cal])
    ##win.MessageBox(0, full_cmd)
    
    process = subprocess.Popen(full_cmd, stdout=subprocess.PIPE)
    message = process.stdout.readline()
    group = None
    while len(message) > 0:
        #addIn.ReportMessage(message)     
        l = message.split("INFO->['")
        if len(l)>1:
            l2 = l[1].split("'")
            new_group = l2[0]
            l3 = l[1].split(',')
            to_do = int(l3[1].strip())
            if group != new_group:
                group = new_group
                progressMax = to_do
                try:
                    addIn.CloseProgressDialog()
                except:
                    pass
                addIn.ShowProgressDialog('Ziel und Verkehrmittelwahl',"Gruppe %s" %group,
                                         progressMax)
            already_done = progressMax - to_do
            #addIn.ReportMessage('%s %s' %(group, to_do))
            addIn.UpdateProgressDialog(already_done)
        message = process.stdout.readline()
             
    #addIn.ReportMessage(message)
        
    returnvalue = process.wait()
    if returnvalue == 1:
        addIn.ReportMessage('Fehler')
    #if returnvalue == 0:
        #win.MessageBox(0,'Fertig')

    try:
        addIn.CloseProgressDialog()
    except:
        pass


    # IV Modell starten
    ##if param["iv"]:
        ##subprocess.Popen()

    # Progressdialog
    # return if terminated

# ADDIN
if len(sys.argv) > 1:
    addIn = AddIn()
else:
    addIn = AddIn(Visum)

if addIn.IsInDebugMode:
    app = wx.PySimpleApp(0)
    Visum = addIn.VISUM
    addInParam = AddInParameter(addIn, None)
else:
    addInParam = AddInParameter(addIn, Parameter)

if addIn.State != AddInState.OK:
    addIn.ReportMessage(addIn.ErrorObjects[0].ErrorMessage)
else:
    try:
        defaultParam = {}

        param = addInParam.Check(True, defaultParam)
        Run(param)
    except:
        addIn.HandleException(addIn.TemplateText.MainApplicationError)
