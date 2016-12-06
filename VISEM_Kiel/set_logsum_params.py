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
    set_logsum_params(dm, addIn)


def set_logsum_params(dm, addIn):

    VISEM_COMBINED = 85

    vco = get_or_add_operation(
        Visum, OP_TYPE=VISEM_COMBINED).VISEMCombinedParameters


    # Distribution
    vdist_para = vco.VISEMDistributionParameters
    hierarchy = get_hierarchy(dm)


    ls_dict = {}
    for act in dm.Activities.GetAll:
        a = act.AttValue('Code')
        if not act.AttValue('IsHomeActivity'):
            ls_param = Visum.Net.AttValue('LS_{}'.format(a))
            ls_dict[a] = ls_param
            
    n_demand_strata = dm.DemandStrata.Count

    addIn.ShowProgressDialog(
        u"Set Logsum for {N} Demand Strata".format(N=n_demand_strata),
        u"Set Logsum", n_demand_strata, setTimeMode=True)

    # Distribution Parameters by Group
    i = 0
    for ds in dm.DemandStrata:
        i += 1
        if addIn.ExecutionCanceled:
            raise RuntimeError(u'Aborted at Demand Stratum {i}'.format(i=i))       

        calibrate = ds.AttValue('Autocalibrate_Logsum')
        pg_code = ds.AttValue('PersonGroupCodes')
        ac_code = ds.AttValue('ActivityChainCode')
        addIn.UpdateProgressDialog(
            i, u'Set Logsum {i} for {p}:{a}'.format(i=i, p=pg_code, a=ac_code))

        main_activity = get_main_activity(hierarchy, ac_code)
        vgdist_para = vdist_para.VISEMDGroupDistributionParameters(pg_code)
        for a in ac_code[1:-1]:
            if calibrate or a != main_activity:
                vgadist_para = vgdist_para.VISEMDGroupActivityDistributionParameters(a)
                ls_param = ls_dict[a]
    
                vgadist_para.SetAttValue('LogSumCoeff', ls_param)
                # hiermit wird der Parameter in der Nutzenfunktion verändert


    addIn.UpdateProgressDialog(n_demand_strata)
    addIn.CloseProgressDialog()
    addIn.ReportMessage(u'Set Logsum for {i} Demand Strata'.format(i=i),
                        messageType=2)


def get_main_activity(hierarchy, ac_code):
    """get the code of the main """
    main_act = ac_code[np.argmin(np.array([hierarchy[a] for a in ac_code]))]
    return main_act


def get_hierarchy(dm):
    a = np.rec.array(
        dm.Activities.GetMultipleAttributes(['Code', 'Rank', 'IsHomeActivity']),
        names=['code', 'rank', 'home'])
    argsort = np.argsort(a.rank)
    hierarchy = a.code[argsort][a.home[argsort] == 0]
    h = dict(zip(hierarchy, range(len(hierarchy))))
    idx = len(h)
    for act in a[a.home == 1]:
        h[act.code] = idx
    return h


def get_or_add_operation(Visum, OP_TYPE, N=1):
    """
    search the Nth operation of OP_Type

    Parameters:
    -----------
    Visum : Visum-Instance
    OP_TYPE: The OperationType searched
    N: int, optional (Default=1):
        the Nth operation to search
    """
    ops_iter = Visum.Procedures.Operations.Iterator
    ops_iter.Reset()
    found = 0
    while ops_iter.Valid and found < N:
        op = ops_iter.Item
        o_type = op.AttValue('OperationType')
        if o_type == OP_TYPE:
            found += 1
        ops_iter.Next()

    if not found:
        op = Visum.Procedures.Operations.AddOperation(1)
        op.SetAttValue('OperationType', OP_TYPE)
    return op


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
