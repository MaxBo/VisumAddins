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

    # Nachfragemodell aufrufen
    # call module -m tdmks.main instead of fixed path to .py-file
    cmd = r'C:\Anaconda\python -m tdmks.main'

    cmd_name = '-n %s' % param["Name"]
    cmd_zonal = '--zd %s' % param["Struktur"]
    cmd_put = '--pp_put --put %s' % param["PUT"]
    cmd_prt = '--pp_prt --prt %s' % param["PRT"]
    cmd_nmt = '--pp_nmt --nmt %s' % param["NMT"]
    cmd_par = '--par %s' % param["Parameter"]

    if param['modal_split']:
        cmd_cal = '-c'
    else:cmd_cal=''

    if param['korrektur']:
        cmd_kor = '--update_kf'
    else:cmd_kor=''

    # create full command
    full_cmd = ' '.join([cmd, cmd_name, cmd_put, cmd_prt,
                         cmd_nmt, cmd_zonal, cmd_par, cmd_cal, cmd_kor])

    # double check if really should run with Message box
    title = 'Starte Nachfragemodell mit folgendem Kommando'
    OK_CANCEL = 1
    result = win.MessageBox(0, full_cmd, title, OK_CANCEL)
    # Cancel selected
    if result == 2:
        addIn.ReportMessage('Abbruch')
        return

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
                msg = 'Ziel und Verkehrmittelwahl'
                addIn.ShowProgressDialog(msg, "Gruppe %s" % group, progressMax)
            already_done = progressMax - to_do

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
