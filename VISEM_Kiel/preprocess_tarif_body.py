# -*- coding: utf-8 -*-


import numpy as np


def main(Visum):
    """"""
    calculate_min_ticket_price()


def calculate_min_ticket_price():
    """Calculate the minimum Ticket price over the whole day"""
    n_zones = Visum.Net.Zones.Count
    far_matrices = Visum.Net.Matrices.ItemsByRef('Matrix([CODE]="FAR")')
    far_attrs = np.rec.fromrecords(
        far_matrices.GetMultipleAttributes(('CODE', 'FROMTIME', 'TOTIME', 'NO')),
        names=['code', 'fromtime', 'totime', 'no'])

    res = np.full((n_zones, n_zones), 999999, dtype='d')
    for m in far_attrs:
        # only matrices with fromtime-value
        if m['fromtime'] is not None:
            values = np.array(Visum.Net.Matrices.ItemByKey(m['no']).GetValues())
            res = np.minimum(res, values)

    masked_res = np.ma.masked_equal(res, 0, copy=False)
    min_price = np.minimum(masked_res.min(0), masked_res.min(1))
    np.fill_diagonal(res, min_price)

    ref = 'Matrix([CODE]="SINGLETICKET")'
    res_matrix = Visum.Net.Matrices.ItemsByRef(ref).GetAll[0]
    res_matrix.SetValues(res)


if __name__ == '__main__':
    main(Visum)
