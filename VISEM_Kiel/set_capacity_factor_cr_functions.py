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
    n_cr_functions = 54
    
    addIn.ShowProgressDialog(
        u"Set CR Capacity Factors",
        u"Set CR Capacity Factors", n_cr_functions, setTimeMode=True)
    for i in range(1, n_cr_functions):
        if addIn.ExecutionCanceled:
            raise RuntimeError(u'Aborted at Linktype {i}'.format(i=i))       
        cr = crs.CrFunction(i)
        cr.SetAttValue('capacityFactor', capacityFactor)
        addIn.UpdateProgressDialog(
            i, u'"Set CR Capacity Factor for linktype {i}'.format(i=i))
    addIn.UpdateProgressDialog(n_cr_functions)
    addIn.CloseProgressDialog()
    addIn.ReportMessage(u'Capacity Factors set for {i} linktypes'.format(i=i),
                        messageType=2)
        


if __name__ == '__main__':
    argparse = ArgumentParser()
    argparse.add_argument('-f', help='CapacityFactor',
                          dest='capacityFactor', default=11.0)
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


    
