# -*- coding: utf-8 -*-


import sys

if __package__ is None:
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import numpy as np
from helpers.visumpy_with_progress_dialog import AddIn, AddInState


def main(Visum, addIn):
    """"""
    code = 'VisemT'
    dm = Visum.Net.DemandModels.ItemByKey(code)
    delete_all_demand_segments(dm, addIn)


def delete_all_demand_segments(dm, addIn):

    n_demand_strata = dm.DemandStrata.Count

    addIn.ShowProgressDialog(
        u"Delete {N} Demand Strata".format(N=n_demand_strata),
        u"Delete Demand Strata", n_demand_strata, setTimeMode=True)

    # Distribution Parameters by Group
    i = 0
    for ds in dm.DemandStrata:
        i += 1
        if addIn.ExecutionCanceled:
            raise RuntimeError(u'Aborted at Demand Stratum {i}'.format(i=i))       
        Visum.Net.RemoveDemandStratum(ds)

        addIn.UpdateProgressDialog(
            i, u'Delete Demand Stratum {i}'.format(i=i))


    addIn.UpdateProgressDialog(n_demand_strata)
    addIn.CloseProgressDialog()
    addIn.ReportMessage(u'{i} Demand Strata deleted'.format(i=i),
                        messageType=2)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        addIn = AddIn()
    else:
        addIn = AddIn(Visum)    
        
    if addIn.State != AddInState.OK:
        addIn.ReportMessage(addIn.ErrorObjects[0].ErrorMessage)
    else:
        try:            
            main(Visum, addIn)
        except:
            addIn.HandleException(addIn.TemplateText.MainApplicationError)
