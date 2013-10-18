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
#from simcommon.helpers import latinize
from latinze import latinize
import VisumPy.AddIn

from VisumPy.helpers import GetMatrix, SetMatrix
from tables.exceptions import NoSuchNodeError


def Run(param):

    #File Path from MatrixToHDF5Dlg
    filepath = param['file']
    matrixcode = param['matrix']
    no = matrixcode.split(' ')[0]
    no = float(no)
    m = Visum.Net.Matrices.ItemByKey(no)

    # Open File
    with tables.openFile(filepath, 'a') as h:


        #Create/Open HDF5
        name = latinize(m.AttValue('Name'))
        #name = m.AttValue('Name') # da latinize nur
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
            #if item == 5:
                #zeit = 1
                
                #if param["OVIV"]== "OV":                        
                    #arr_shape = (zeit, m_row, m_col)
                
                #if param["OVIV"]== "IV":
            arr_shape = (m_row, m_col)
                                 

                ##Create Array (here)
            arr = numpy.zeros(arr_shape, dtype='f4')

                ## create Table (in hdf5 file)
                ###arrname = code+str(t)
            table_in_hdf5 = h.createArray(group, name, arr)

            ## Fill table with Matrix
            #if param["OVIV"]== "IV":
                #table_in_hdf5[:] = data
            
            #elif item == 5:
            table_in_hdf5[:] = data
            #else:
                #table_in_hdf5[item] = data

            #Meta Infos (Node)
            table_in_hdf5.attrs['Name'] = name
            t = time.localtime()
            date = time.asctime(t)
            table_in_hdf5.attrs['Last Updated'] = date

            # Save
            h.flush()

            # Tabelle Bezirke
            try:
                zonetable = h.getNode(h.root.Bezirke)
            except NoSuchNodeError:
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
