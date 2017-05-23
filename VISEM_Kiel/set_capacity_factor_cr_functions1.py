# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import sys
import numpy as np


from visumhelpers.visumpy_with_progress_dialog import AddIn, AddInState, AddInParameter
from visumhelpers.write_xml import VisumXMLProcedures
import tempfile


def main(Visum, capacityFactor, addIn):
    """"""
    crs = Visum.Procedures.Functions.CRFunctions
    linkTypeList = Visum.Lists.CreateLinkTypeList
    AggregationFunctionAggregate = 1
    AggregationFunctionCount = 9
    AggregationFunctionConcatenate = 10
    AggregationFunctionDistinct = 12

    # Group column
    linkTypeList.AddColumn("VDFunction\VdFunctionNumber",
                           GroupOrAggrFunction=AggregationFunctionAggregate)
    linkTypeList.AddColumn("No",
                           GroupOrAggrFunction=AggregationFunctionCount)
    linkTypeList.AddColumn("No",
                           GroupOrAggrFunction=AggregationFunctionConcatenate)
    linkTypeList.AddColumn("VDFunction\VdFunctionType",
                           GroupOrAggrFunction=AggregationFunctionDistinct)
    linkTypeList.AddColumn("VDFunction\capacityFactor",
                           GroupOrAggrFunction=AggregationFunctionDistinct)
    linkTypeList.AddColumn("VDFunction\BPR_A",
                           GroupOrAggrFunction=AggregationFunctionDistinct)
    linkTypeList.AddColumn("VDFunction\BPR_B",
                           GroupOrAggrFunction=AggregationFunctionDistinct)
    linkTypeList.AddColumn("VDFunction\BPR2_A",
                           GroupOrAggrFunction=AggregationFunctionDistinct)
    linkTypeList.AddColumn("VDFunction\BPR2_B1",
                           GroupOrAggrFunction=AggregationFunctionDistinct)
    linkTypeList.AddColumn("VDFunction\BPR2_B2",
                           GroupOrAggrFunction=AggregationFunctionDistinct)

    crFuncUsage = np.rec.fromrecords(linkTypeList.SaveToArray(),
                                     names=['VDFUNCTIONNUMBER',
                                            'n_linktypes',
                                            'linktypes_assigned',
                                            'VDFUNCTIONTYPE',
                                            'CAPACITYFACTOR',
                                            'BPR_A',
                                            'BRP_B',
                                            'BPR2_A',
                                            'BPR2_B1',
                                            'BPR2_B2',
                                            ])

    # set capacityfactor to new value
    crFuncUsage['CAPACITYFACTOR'] = capacityFactor

    # create xml
    tmp = tempfile.mktemp(suffix="xml", prefix='visum_')
    xml = VisumXMLProcedures(tmp)

    functions = {'FUNCTIONS':
                 {'VDFUNCTIONSPARAMETERS':
                  {'LINKVDFUNCTIONSPARAMETERS': {},
                   }
                  ,}
                 ,}
    xml.add_dict_to_node(self.root, functions)

    crfunclist = []
    attrnames = ['VDFUNCTIONNUMBER',
                 'VDFUNCTIONTYPE',
                 'CAPACITYFACTOR',
                 'BPR_A',
                 'BRP_B',
                 'BPR2_A',
                 'BPR2_B1',
                 'BPR2_B2',
                 ]
    for i, row in enumerate(crFuncUsage):
        elem = dict(zip([(attr, '{}'.format(row.getitem(attr)))
                         for attr in attrnames]))
        crfunclist.append(elem)
    xml.add_dict_to_node('LINKVDFUNCTIONSPARAMETERS',
                         {'VDFUNCTION': crfunclist,})

    addIn.ReportMessage(u'{t}: Capacity Factors set to {v} for {i} CR-Functions'.format(t=tmp, i=done,
                                                                                   v=capacityFactor),
                        messageType=2)



if __name__ == '__main__':
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

    default_params = {'Capacity_Factor': 11.0}
    param = addInParam.Check(True, default_params)
    capacityFactor = param['Capacity_Factor']

    if addIn.State != AddInState.OK:
        addIn.ReportMessage(addIn.ErrorObjects[0].ErrorMessage)
    else:
        try:
            main(Visum, capacityFactor, addIn)
        except:
            addIn.HandleException(addIn.TemplateText.MainApplicationError)



