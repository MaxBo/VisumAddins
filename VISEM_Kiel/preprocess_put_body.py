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

    add_pjt_by_activity(dm, addIn)


def add_pjt_by_activity(dm2, addIn, skim='PJT', home='W', factor=.8, exponent=.8):
    """Add weighted PT Skim Matrices"""
    ref = 'Matrix([CODE]="No_Connection_Forward")'
    nc_forward = Visum.Net.Matrices.ItemsByRef(ref).GetAll[0]
    ref = 'Matrix([CODE]="No_Connection_Backward")'
    nc_backward = Visum.Net.Matrices.ItemsByRef(ref).GetAll[0]

    ref = 'Matrix([CODE]="weighted_skim_matrix")'
    weighted_skim_matrix = Visum.Net.Matrices.ItemsByRef(ref).GetAll[0]

    pgr = dm2.PersonGroups.GetAll[0].AttValue('Code')
    time_intervals = get_time_intervals()
    formula = '{w} * (Matrix([CODE] = "PJT" & [FROMTIME]={f} & [TOTIME]={t}) < 99999)'
    formula2 = '''
{w} * IF((Matrix([CODE] = "PJT" & [FROMTIME]={f} & [TOTIME]={t}) < 99999),
Matrix([CODE] = "PJT" & [FROMTIME]={f} & [TOTIME]={t}) +
{factor} * POW((Matrix([CODE] = "XADT" & [FROMTIME]={f} & [TOTIME]={t}) * 4 + 1),{exponent}), 0)'''

    formula_one_way = '''
IF((Matrix([CODE]="{nc}")<999999),
Matrix([CODE]="{nc}")* 0.5 * ({f}),
999999)'''

    acts = dm2.Activities.GetAll
    n_activities = len(acts)
    addIn.ShowProgressDialog(
        u"Calculate Percieved Journey Time Matrices for {N} Activities".format(N=n_activities),
        "Calculate Percieved Journey Time Matrices", n_activities * 10, setTimeMode=True)
    
    for i, act in enumerate(acts):
        c = i * 10
        
        if not act.AttValue('IsHomeActivity'):
            a_code = act.AttValue('Code')
            a_name = act.AttValue('Name')
            progress(addIn, c, a_name, a_code)
            # get the target matrix
            ref = 'Matrix([CODE]="{}_{}")'.format(skim, a_code)
            m = Visum.Net.Matrices.ItemsByRef(ref).GetAll[0]
            
            c += 1
            progress(addIn, c, a_name, a_code)

            # set the no_connection_formula for the forward trips
            ap_code = '{h}{a}'.format(h=home, a=a_code)
            weights_forward = set_no_connection_formula(
                ap_code,
                dm2,
                pgr,
                formula,
                time_intervals,
                nc_forward)

            # set the no_connection_formula for the backward trips
            ap_code = '{a}{h}'.format(h=home, a=a_code)
            weights_backward = set_no_connection_formula(
                ap_code,
                dm2,
                pgr,
                formula,
                time_intervals,
                nc_backward)

            c += 1
            progress(addIn, c, a_name, a_code)

            # set the weighted_skim_matrix

            # forward
            matrices2 = [formula2.format(f=ti['start'], t=ti['end'], w=w,
                                         factor=factor, exponent=exponent)
                         for ti, w in zip(time_intervals, weights_forward)]
            formula_forward = formula_one_way.format(
                nc='No_Connection_Forward',
                f='\n+'.join(matrices2))

            # backward
            matrices2 = [formula2.format(f=ti['start'], t=ti['end'], w=w,
                                         factor=factor, exponent=exponent)
                         for ti, w in zip(time_intervals, weights_backward)]
            formula_backward = formula_one_way.format(
                nc='No_Connection_Backward',
                f='\n+'.join(matrices2))

            # both
            complete_formula = '\n + \n'.join([formula_forward,
                                               formula_backward])

            weighted_skim_matrix.SetAttValue('Formula', complete_formula)

            c += 1
            progress(addIn, c, a_name, a_code)

            e = np.array(weighted_skim_matrix.GetValues())
            
            c += 3
            progress(addIn, c, a_name, a_code)            
            np.fill_diagonal(e, 999999)
            m.SetValues(e)

    addIn.UpdateProgressDialog(n_activities)
    addIn.CloseProgressDialog()
    addIn.ReportMessage(u'calculated Parking Matrices for {i} activities'.format(i=i),
                        messageType=2)

def progress(addIn, c, a_name, a_code):
    if addIn.ExecutionCanceled:
        raise RuntimeError('Aborted at Activity {i}'.format(i=i))       
    addIn.UpdateProgressDialog(c, u'Calculate Matrix PJT_{a} for {b}'.format(
        a=a_code, b=a_name))        


def set_no_connection_formula(ap_code, dm2, pgr,
                              formula, time_intervals, nc_forward):
    weights = get_weights(ap_code, dm2, pgr)
    matrices = [formula.format(f=ti['start'], t=ti['end'], w=w)
                for ti, w in zip(time_intervals, weights)]
    complete_formula = '1 / ((1/999999) + {})'.format('\n+'.join(matrices))
    nc_forward.SetAttValue('Formula', complete_formula)
    return weights


def get_weights(ap_code, dm2, pgr):
    time_series = Visum.Net.TimeSeriesCont
    ap = dm2.ActPairs.ItemByKey(ap_code)
    ts_no = ap.AttValue('TimeSeriesNo({pg})'.format(pg=pgr))
    ts = time_series.ItemByKey(ts_no)
    tsi = ts.TimeSeriesItems
    weights = np.array(tsi.GetMultipleAttributes(['Share'])).flatten() / 100
    return weights


def get_time_intervals():
    """Get the time intervals that are not aggregate time intervals"""
    atimes = Visum.Procedures.Functions.AnalysisTimes
    i = 0
    tis = []
    for t in range(atimes.NumTimeIntervals):
        ti = atimes.TimeInterval(t + 1)
        if not ti.AttValue('IsAggregate'):
            tis.append((i,
                        ti.AttValue('StartTime'),
                        ti.AttValue('EndTime')))
            i += 1
    time_intervals = np.rec.fromrecords(tis,
                                        dtype=[('i', int),
                                               ('start', float),
                                               ('end', float)])
    return time_intervals


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

