# -*- coding: utf8 -*-
#------------------------------------------------------------------------------
# Name:        VISUM Matrices to HDF5 for each time
# Purpose:     Berechnet ÖV Kenngrößen nach vordefiniertem Verfahrem und Zeitscheiben
#              Speichert alle Kenngrößenmatrizen je berechneter Zeitscheibe in HDF5 Datei
#              -> nicht berechnete Matrizen erhalten in jeder Zeitscheibe den zuvor berechneten Wert
#
# Author:      Nina Kohnen
#
# Created:     03.04.2013
# Copyright:   (c) Barcelona 2013
# Licence:     <your licence>
#------------------------------------------------------------------------------

import numpy
import tables
import VisumPy
import os
import sys
import time
import subprocess
#from simcommon.helpers import latinize
from latinze import latinize
import VisumPy.AddIn

from VisumPy.helpers import GetMatrix, SetMatrix
from tables.exceptions import NoSuchNodeError

i = []
# Zeitschiebe aus GUI
def Run(param):

    if param["Zeitscheibe1"]:
        i.append(0)
    if param["Zeitscheibe2"]:
        i.append(1)
    if param["Zeitscheibe3"]:
        i.append(2)
    if param["Zeitscheibe4"]:
        i.append(3)
    if param["Zeitscheibe5"]:
        i.append(4)
##Was machen wir mit diesem FAll???
    if param["Zeitscheibe24"]:
        i.append(5)

    #File Path from MatrixToHDF5Dlg
    filepath = param['filepath']
    
    """ZEITSCHEIBEN"""
    #Addin Path (Com Doku P.62)
    verzeichnis = 65
    path = Visum.GetPath(verzeichnis)
    path_name = str(path)
    ##addIn.ReportMessage(path)
    #Set Zeitscheiben - (COM Docu:99)
    Visum.Procedures.OpenXmlWithOptions(path+'zeitscheiben_addin.xml', 0,1)
    #Import Operation ÖV- (COM Docu:99)
    if param["OVIV"]== "OV": #OperationType 102
        Visum.Procedures.OpenXmlWithOptions(path+'ov_kassel.xml', 1,0,2)
    if param["OVIV"]== "IV": #OperationType 103
            Visum.Procedures.OpenXmlWithOptions(path+'iv_kassel.xml', 1,0,2)
    """BRECHNENEN"""
    # For each i:
    for item in i:
        #Get start/end Time from Analysezeiträume
        f = Visum.Procedures.Functions
        at = f.AnalysisTimes
        a = at.TimeInterval(item + 1)  # auswahl Zeitintervall
        start = a.AttValue('StartTime')
        end = a.AttValue('EndTime')
        if item == 4:
            end = 3600*24-1
        if item == 5:
            start = 0
            end = 3600*24-1
            
        #Get Operation
        operations = Visum.Procedures.Operations
        op = operations.ItemByKey(1)
        
        # Set Parameters ->In Tabelle auf S. 113/114 nachschauen
        if param["OVIV"]== "OV":
            put_ckmp = op.PuTCalcSkimMatrixParameters
            ttp = put_ckmp.TimetableBasedParameters
            ttbp = ttp.BaseParameters
            ttbp.SetTimeIntervalStart(start)  # Time in seconds
            ttbp.SetTimeIntervalEnd(end)    # Time in Seconds
        
        #setcurrentOperation
        Visum.Procedures.OperationExecutor.SetCurrentOperation(1)
        Visum.Procedures.OperationExecutor.ExecuteCurrentOperation()

        """SCHREIBEN"""
        # Open File
        with tables.openFile(filepath, 'a') as h:

            #Alle Matrizen
            AllMatrices = Visum.Net.Matrices.GetAll

            for m in AllMatrices:

                m_type = m.AttValue('MatrixType')

                #Wenn Kenngroessenmatrix
                if m_type == 'MATRIXTYPE_SKIM':

                    #Create/Open HDF5
                    name = latinize(m.AttValue('Name'))
                    if name == 'Fahrtweite-VSys(AST)':
                        name = 'in_vehicle_distance_ast'
                    if name == 'Fahrtweite-VSys(Bus)':
                        name = 'in_vehicle_distance_bus'
                    if name == 'Fahrzeit im Fahrzeug-VSys(AST)':
                        name = 'in_vehicle_time_ast'
                    if name == 'Fahrzeit im Fahrzeug-VSys(Bus)':
                        name = 'in_vehicle_time_bus'
                    if name == 'Fahrtweite':
                        name = 'Fahrweite'
                    if name == 'Gehzeit':
                        name = 'Umsteigegehzeit'
                    if name == 'Fahrzeit im Fahrzeug':
                        name = 'FahrzeitimFahrzeug'
                    code = m.AttValue('Code')
                    no = m.AttValue('No')

                    root = h.root
                    #Matrix als Numpy array (hat funktion shape)
                    data = VisumPy.helpers.GetMatrix(Visum, no)
                    
                    #Knoten visum?
                    try: 
                        group = h.getNode(root, 'visum')
                    except NoSuchNodeError:
                        group = h.createGroup(root,'visum')
                    #addIn.ReportMessage(data)
                    try:
                        # Existiert der Knoten(Tabelle)
                        table_in_hdf5 = h.getNode(group, name)

                    except NoSuchNodeError:
                        # Wenn nicht :
                        m_shape = data.shape          # Get Shape
                        m_row = m_shape[0]             # Get Row Number
                        m_col = m_shape[1]              # Get Col Number
                        zeit = 5
                        # if 24 h
                        if item == 5:
                            zeit = 1
                        
                        if param["OVIV"]== "OV":                        
                            arr_shape = (zeit, m_row, m_col)
                        
                        if param["OVIV"]== "IV":
                            arr_shape = (m_row, m_col)
                                         

                        #Create Array (here)
                        arr = numpy.zeros(arr_shape, dtype='f4')

                        # create Table (in hdf5 file)
                        ##arrname = code+str(t)
                        table_in_hdf5 = h.createArray(group, name, arr)

                    # Fill table with Matrix
                    if param["OVIV"]== "IV":
                        table_in_hdf5[:] = data
                    
                    elif item == 5:
                        table_in_hdf5[0] = data
                    else:
                        table_in_hdf5[item] = data

                    #Meta Infos (Node)
                    table_in_hdf5.attrs['Name'] = name
                    t = time.localtime()
                    date = time.asctime(t)
                    table_in_hdf5.attrs['Last Updated'] = date

                    #Set Attributes (root)
    ##                h.root._v_attrs['VISUM Version'] = inputdata

                    # Save
                    h.flush()

            # Tabelle Bezirke
            try:
                zonetable = h.getNode(h.root.Bezirke)
                zonetable.remove()
            except NoSuchNodeError:
                pass
            zones = Visum.Net.Zones
            nummer = numpy.array(VisumPy.helpers.GetMulti(zones, 'No'))
            name = numpy.array(VisumPy.helpers.GetMulti(zones, 'Name')).view(numpy.chararray).encode('cp1252')
            rec = numpy.rec.fromarrays([nummer, name],
                                       names=['zone_no',
                                      'zone_name'],
                                       titles=['Bezirke', 'BezirksNamen'],
                                       formats=['<i4', 'S255'])
            zonetable = h.createTable(root, 'Bezirke', rec)

            h.flush()

    """CALIBREIEREN"""
    # Nachfragemodell aufrufen
    cmd = r'C:\Anaconda\python C:\Anaconda\Lib\site-packages\tdmks\main.py'
    if param["OVIV"]== "OV":
        pp = '--pp_put'
        p = '--put %s' %param["filepath"].split('\\')[-1]
    if param["OVIV"]== "IV":
        pp = '--pp_prt'
        p = '--prt %s' %param["filepath"].split('\\')[-1]
    full_cmd = ' '.join([cmd, p, pp, '--skip_run'])  ## cmd_zones
    addIn.ReportMessage(full_cmd)
    
    process = subprocess.Popen(full_cmd, stdout=subprocess.PIPE)

    returnvalue = process.wait()
    if returnvalue == 1:
        addIn.ReportMessage('Fehler')
    if returnvalue == 0:
        addIn.ReportMessage('Fertig')

    #Close command line??


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
