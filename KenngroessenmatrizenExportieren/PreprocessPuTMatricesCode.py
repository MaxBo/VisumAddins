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

if __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from helpers.get_folders import get_folders

import subprocess
import os
import numpy
import tables
from tables.exceptions import NoSuchNodeError
import VisumPy
from KenngroessenmatrizenExportierenBody import ExportSkims, NoSuchNodeError
import VisumPy.AddIn

class PreprocessMatrices(ExportSkims):
    """Preprocess the Public Transport Matrices"""


    def __init__(self, Visum):
        self.Visum = Visum

        super(PreprocessMatrices, self).__init__(Visum)
        pythonpath, project_folder = get_folders(Visum,
                                                 exe_folder='TDMKSFolder')
        self.pythonpath = pythonpath
        self.project_folder = project_folder
        self.scenario_name = Visum.Net.AttValue('ScenarioCode')


    def export_zones(self):
        """Exportiere die Verkehrszellendefinition"""
        filepath = self.params[self.mode]
            # Open File
        with tables.openFile(filepath, 'a') as h:
            # Tabelle Bezirke
            try:
                zonetable = h.getNode(h.root.Bezirke)
                zonetable.remove()
            except NoSuchNodeError:
                pass
            zones = self.Visum.Net.Zones
            nummer = numpy.array(VisumPy.helpers.GetMulti(zones, 'No'))
            name = numpy.char.encode(VisumPy.helpers.GetMulti(zones, 'Name'),
                                     'cp1252')
            rec = numpy.rec.fromarrays([nummer, name],
                                       names=['zone_no',
                                      'zone_name'],
                                       titles=['Bezirke', 'BezirksNamen'],
                                       formats=['<i4', 'S255'])
            zonetable = h.createTable(h.root, 'Bezirke', rec)

            h.flush()


    def execute(self):
        project_xml_file = os.path.join(self.project_folder, 'project.xml')
        cmd = '{pythonpath} -m tdmks.main_xml -xml "{project_xml_file}" -n "{scenario_name}" {pp_cmd} --skip_run'
        full_cmd = cmd.format(pythonpath=self.pythonpath,
                              project_xml_file=project_xml_file,
                              scenario_name=self.scenario_name,
                              pp_cmd=self.preprocess_command
                              )
        with open(r'C:\temp\test.log', 'w') as f:
            f.write(full_cmd)
        c = subprocess.Popen(full_cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             shell=True)
        ret = c.stdout.read()
        return full_cmd

