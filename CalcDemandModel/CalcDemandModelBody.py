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

    modelsplit = param["modelsplit"] 
        # HDF5 Filepaths
    put = param["PUT"]
    prt = param["PRT"]
    nmt = param["NMT"] 
    struktur = param["Struktur"] 
        # Speichern
    name = param["Name"] 

    ##if param["hdf5_save"]:
        # call AddIN Kenngrößen berechnen
        ##operations = Visum.Procedures.Operations
        ##op = operations.AddOperation(1)
        ##op.SetAttValue('OperationType', 84)  # 84 = AddIn aber noch nicht defniert welches???
        ##opa = op.AddInParameters
        ##opa.SetAttValue('AddInID', 'GGR_CALCSAVESKIM')


    # Nachfragemodell aufrufen
    ##cmd = r'C:\Anaconda\python C:\Dev\elan\tdm\src\tdm\tdmks\simulation_steps.py'
    cmd = r'C:\Anaconda\python C:\Dev\elan\tdmks\src\tdmks\main.py'
    cmd = r'C:\Anaconda\python C:\Anaconda\Lib\site-packages\tdmks\main.py'
    cmd_name = '-n %s' %param["Name"]
    cmd_zonal = '--zd %s' %param["Struktur"]
    cmd_put = '--put %s' %param["PUT"]
    cmd_prt = '--prt %s' %param["PRT"]
    cmd_nmt = '--nmt %s' %param["NMT"]
    cmd_par = '--par %s' % r'params.h5'
    #cmd_par = '--par %s' % r'params.h5'
    if param['modelsplit']:
        cmd_cal = '-c'
    else:cmd_cal=''
    
    full_cmd = ' '.join([cmd, cmd_name, cmd_put, cmd_prt, cmd_nmt, cmd_zonal, cmd_par, cmd_cal])  ## cmd_zones
    win.MessageBox(0, full_cmd)
    
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
