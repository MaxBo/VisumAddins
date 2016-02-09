# -*- coding: utf8 -*-
#------------------------------------------------------------------------------
# Name:        VISUM Matrices to HDF5 for each time
# Purpose:     importiert Zeitscheiben in Verfahrensparametersetzs
#
# Author:      Max Bohnet
#
#------------------------------------------------------------------------------
if __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from helpers.get_folders import get_folders
from XMLHelper import XMLReader
import codecs
import os
import sys
import subprocess
import getpass
import VisumPy.AddIn
import tempfile


# Zeitschiebe aus GUI
class AddTimeSlices(object):
    def __init__(self, params):
        pythonpath, project_folder = get_folders(Visum)
        self.pythonpath = pythonpath
        self.user = getpass.getuser()
        self.project_folder = project_folder
        self.scenario_name = params['demand_scenario']
        self.parametersets = params['parametersets']
        self.temp_xml = self.create_xml()
        self.add_xml()

    def create_xml(self):
        """create time interval xml and import into Visum"""
        #project_xml_file = os.path.join(self.project_folder, 'project.xml')
        cmd = '{pythonpath} -m gui_vm.write_time_slice_xml -f "{project_folder}" -s "{scenario_name}"'
        full_cmd = cmd.format(pythonpath=self.pythonpath,
                                        project_folder=self.project_folder.rstrip("\\"),
                                        scenario_name=self.scenario_name)
        #raise ValueError(full_cmd)
        c = subprocess.Popen(full_cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             shell=True)

        temp_path = tempfile.mktemp(suffix='.xml')
        xml = c.stdout.read()
        if not xml.startswith('<'):
            raise ValueError(xml)
        with open(temp_path, mode='wb') as t:
            t.write(xml)
        return temp_path

    def add_xml(self):
        project = Visum.ScenarioManagement.CurrentProject
        procedure_parametersets = project.ProcedureParameterSets
        if not project:
            msg = u'Must be called with an project opened in the scenario management'
            addIn.ReportMessage(msg)
        for parameterset, checked in enumerate(self.parametersets):
            if checked:
                if parameterset == 0:
                    # Basisszenario
                    self.modifyBaseVersion()
                else:
                    procedure_parameterset = procedure_parametersets.ItemByKey(
                        parameterset)
                    procedure_parameterset.StartEditProcedureParameterSet()
                    self.load_timeslice_from_xml()
                    procedure_parameterset.EndEditProcedureParameterSet()

    def modifyBaseVersion(self):
        """Modify the base version"""
        project = Visum.ScenarioManagement.CurrentProject
        base_version = os.path.join(u'..',
                                    project.AttValue(u'BaseVersionFile'))
        Visum.LoadVersion(base_version)
        self.load_timeslice_from_xml()
        Visum.SaveVersion(base_version)
        msg = u'Basisversion: Zeitscheiben des DemandScenarios {scenario} durch Benutzer {user} eingefügt'.format(
            scenario=self.scenario_name,
            user=self.user,
        )
        project.AddLogEntry(msg)

    def load_timeslice_from_xml(self):
        """load timeslices and add operations"""
        ReadOperations_ReplaceAll = 0
        Visum.Procedures.OpenXmlWithOptions(
            self.temp_xml,
            readOperations=False,
            readFunctions=True,
            roType=ReadOperations_ReplaceAll)
        self.remove_group_skim_matrix_calculation()
        self.add_operations()

    def remove_group_skim_matrix_calculation(self):
        OPERATIONTYPE_GROUP = 75
        operations = Visum.Procedures.Operations
        in_group = False

        for operation in operations.GetAll:
            idx = int(operation.AttValue('No'))
            group_member = True
            if operation.AttValue('OperationType') == OPERATIONTYPE_GROUP:
                group_member = False
                if operation.AttValue('Comment') == u'PuTSkimMatrixCalculation':
                    in_group = True
                    idx_to_remove = idx + 1
                else:
                    in_group = False
            if in_group and group_member:
                    operations.RemoveOperation(idx_to_remove)

    def add_operations(self):
        """
        add operations for each time interval
        """
        OPERATIONTYPE_GROUP = 75
        # find the position to insert
        operations = Visum.Procedures.Operations
        group_found = False
        for operation in operations.GetAll:
            if operation.AttValue('OperationType') == OPERATIONTYPE_GROUP:
                if operation.AttValue('Comment') == 'PuTSkimMatrixCalculation':
                    position = int(operation.AttValue('No'))
                    group_found = True
                    break
        # create Group SkimMatrixCalculation if not exists
        if not group_found:
            self.create_group_put_skim_matrix_calculation()

        # add for each analysis time the operations
        at = Visum.Procedures.Functions.AnalysisTimes
        n_intervals = at.NumTimeIntervals
        for t in range(1, n_intervals + 1):
            time_interval = at.TimeInterval(t)
            is_aggregate = time_interval.AttValue('IsAggregate')
            if not is_aggregate:
                at.CurrentTimeInterval = t
                self.add_operation_timeslice(position, time_interval)
                position += 1

    def create_group_put_skim_matrix_calculation(self):
        OPERATIONTYPE_GROUP = 75
        # find the position to insert
        operations = Visum.Procedures.Operations
        n_operations = len(operations.GetAll)
        op = operations.AddOperation(n_operations + 1)
        op.SetAttValue('OperationType', OPERATIONTYPE_GROUP)
        op.SetAttValue('Comment', 'PuTSkimMatrixCalculation')
        position = n_operations + 1



    def add_operation_timeslice(self, position, time_interval):
        """
        Add for each timeslice the operations
        """
        # modify xml-file
        tmp_filename = tempfile.mktemp(suffix='.xml')
        filetype_ProcSettings = 12
        folder_ProcSettings = Visum.GetPath(filetype_ProcSettings)
        default_xml_file = os.path.join(folder_ProcSettings,
                                        'ov_kgmatrix_operation.xml')
        #with codecs.open(tmp_filename, "w", "utf_8_sig") as f:
            #xml = XMLReader(default_xml_file)
            #op = xml.GetElementsByName(u'OPERATION')[0]
            #op.setAttribute('NO', str(position))
            #f.write(xml._XMLReader__config.toprettyxml())

        # insert operation at given position
        ReadOperations_Insert = 2
        Visum.Procedures.OpenXmlWithOptions(default_xml_file,
                                            readOperations=True,
                                            readFunctions=False,
                                            roType=ReadOperations_Insert,
                                            insertPosition=position)
        # modify start and end time
        operations = Visum.Procedures.Operations
        op = operations.ItemByKey(position + 1)
        put_ckmp = op.PuTCalcSkimMatrixParameters
        ttp = put_ckmp.TimetableBasedParameters
        ttbp = ttp.BaseParameters
        ttbp.SetTimeIntervalEnd(time_interval.AttValue('EndTime'))  # Time in seconds
        ttbp.SetTimeIntervalStart(time_interval.AttValue('StartTime'))  # Time in seconds
        #addIn.ReportMessage('{}'.format(position))


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
        AddTimeSlices(param)
    except Exception as e:
        addIn.ReportMessage(e.message)
        addIn.HandleException(addIn.TemplateText.MainApplicationError)
