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


class CalcDemand(object):
    def __init__(self, Visum):
        self.Visum = Visum
        pythonpath, project_folder = get_folders(Visum)
        self.pythonpath = pythonpath
        self.project_folder = project_folder
        self.scenario_name = Visum.Net.AttValue('ScenarioCode')
        self.run_name = Visum.Net.AttValue('RunCode')

    def execute(self):
        project_xml_file = os.path.join(self.project_folder, 'project.xml')
        cmd = '{pythonpath} -m gui_vm.main -o "{project_xml_file}" -s "{scenario_name}" --run-specific {run}{balancing}'
        full_cmd = cmd.format(pythonpath=self.pythonpath,
                                        project_xml_file=project_xml_file,
                                        scenario_name='"{}"'.format(
                                            self.scenario_name),
                                        run='"{}"'.format(self.run_name),
                                        balancing=' --balancing')
        c = subprocess.Popen(full_cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             shell=True)
        return c.stdout.read()


if __name__ == '__main__':
    calc_demand = CalcDemand(Visum)
    calc_demand.execute()

