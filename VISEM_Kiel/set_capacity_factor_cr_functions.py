# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import sys

if __package__ is None:
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from helpers.visumpy_with_progress_dialog import AddIn, AddInState


def main(Visum, capacityFactor, addIn):
    """"""
    crs = Visum.Procedures.Functions.CRFunctions
    linkTypeList = Visum.Lists.CreateLinkTypeList
    linkTypeList.AddColumn("VDFunction\VdFunctionNumber",GroupOrAggrFunction=1) # Group column
    linkTypeList.AddColumn("No",GroupOrAggrFunction=9)                          # aggregate : count
    linkTypeList.AddColumn("No",GroupOrAggrFunction=10)                         # aggregate: concatenate
    
    crFuncUsage = linkTypeList.SaveToArray()
    

    n_cr_functions = len(crFuncUsage)
    
    addIn.ShowProgressDialog(
        u"Set CR Capacity Factors",
        u"Set CR Capacity Factors", n_cr_functions, setTimeMode=True)
    for i, crFunc in enumerate(crFuncUsage):
        cr_type =  int(crFunc[0])
        used_in = int(crFunc[1])
        ref_link_types = crFunc[2]
        if isinstance(ref_link_types, float):
            ref_link_types = str(int(ref_link_types))
        if addIn.ExecutionCanceled:
            raise RuntimeError(u'Aborted at Linktype {i}'.format(i=i))       
        cr = crs.CrFunction(cr_type)
        cr.SetAttValue('capacityFactor', capacityFactor)
        addIn.UpdateProgressDialog(
            i, u'"Set CR Capacity Factor for CR-Function {cr_type}, used {used_in} times in linktypes {lt}'.format(
                cr_type=cr_type,
                used_in=used_in, lt=ref_link_types))
    addIn.UpdateProgressDialog(n_cr_functions)
    addIn.CloseProgressDialog()
    addIn.ReportMessage(u'Capacity Factors set for {i} CR-Functions'.format(i=i),
                        messageType=2)
        


if __name__ == '__main__':
    argparse = ArgumentParser()
    argparse.add_argument('-f', help='CapacityFactor',
                          dest='capacityFactor', default=12.0)
    options = argparse.parse_args()

    if len(sys.argv) > 1:
        addIn = AddIn()
    else:
        addIn = AddIn(Visum)    
        
    if addIn.State != AddInState.OK:
        addIn.ReportMessage(addIn.ErrorObjects[0].ErrorMessage)
    else:
        try:            
            main(Visum, options.capacityFactor, addIn)
        except:
            addIn.HandleException(addIn.TemplateText.MainApplicationError)


    
