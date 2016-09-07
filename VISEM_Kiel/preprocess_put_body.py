# -*- coding: utf-8 -*-


import numpy as np


def main(Visum):
    """"""
    code = 'VisemT'
    dm = Visum.Net.DemandModels.ItemByKey(code)

    add_pjt_by_activity(dm)
    calculate_min_ticket_price()


def calculate_min_ticket_price():
    """Calculate the minimum Ticket price over the whole day"""
    n_zones = Visum.Net.Zones.Count
    far_matrices = Visum.Net.Matrices.ItemsByRef('Matrix([CODE]="FAR")')
    far_attrs = np.rec.fromrecords(
        far_matrices.GetMultipleAttributes(('CODE', 'FROMTIME', 'TOTIME', 'NO')),
        names=['code', 'fromtime', 'totime', 'no'])

    res = np.zeros((n_zones, n_zones), dtype='d')
    for m in far_attrs:
        # only matrices with fromtime-value
        if not m['fromtime'] is None:
            values = np.array(Visum.Net.Matrices.ItemByKey(m['no']))
            res = np.minimum(res, values)

    masked_res = np.ma.masked_equal(res, 0, copy=False)
    min_price = np.minimum(masked_res.min(0), masked_res.min(1))
    np.fill_diagonal(res, min_price)

    ref = 'Matrix([CODE]="SINGLETICKET")'
    res_matrix = Visum.Net.Matrices.ItemsByRef(ref).GetAll[0]
    res_matrix.SetValues(res)


def add_pjt_by_activity(dm2, skim='PJT', home='W'):
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
Matrix([CODE] = "PJT" & [FROMTIME]={f} & [TOTIME]={t}), 0)'''

    formula_one_way = '''
IF((Matrix([CODE]="{nc}")<999999),
Matrix([CODE]="{nc}")* 0.5 * ({f}),
999999)'''

    acts = dm2.Activities.GetAll
    for act in acts:
        if not act.AttValue('IsHomeActivity'):
            a_code = act.AttValue('Code')

            # get the target matrix
            ref = 'Matrix([CODE]="{}_{}")'.format(skim, a_code)
            m = Visum.Net.Matrices.ItemsByRef(ref).GetAll[0]

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

            # set the weighted_skim_matrix

            # forward
            matrices2 = [formula2.format(f=ti['start'], t=ti['end'], w=w)
                         for ti, w in zip(time_intervals, weights_forward)]
            formula_forward = formula_one_way.format(
                nc='No_Connection_Forward',
                f='\n+'.join(matrices2))

            # backward
            matrices2 = [formula2.format(f=ti['start'], t=ti['end'], w=w)
                         for ti, w in zip(time_intervals, weights_backward)]
            formula_backward = formula_one_way.format(
                nc='No_Connection_Backward',
                f='\n+'.join(matrices2))

            # both
            complete_formula = '\n + \n'.join([formula_forward,
                                               formula_backward])

            weighted_skim_matrix.SetAttValue('Formula', complete_formula)

            e = np.array(weighted_skim_matrix.GetValues())
            m.SetValues(e)


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
    main(Visum)
