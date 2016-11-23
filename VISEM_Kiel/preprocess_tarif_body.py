# -*- coding: utf-8 -*-


import sys

if __package__ is None:
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import numpy as np
from helpers.visumpy_with_progress_dialog import AddIn, AddInState


def main(Visum, addIn):
    """"""
    calculate_min_ticket_price(addIn)


def calculate_min_ticket_price(addIn):
    """Calculate the minimum Ticket price over the whole day"""
    AUTONUMBER = -1
    OBJECTTYPEREF_ZONE = 2
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
    ticket_matrices = Visum.Net.Matrices.ItemsByRef(ref).GetAll
    if not ticket_matrices:
        m = Visum.Net.AddMatrix(
            No=AUTONUMBER,
            objectTypeRef=OBJECTTYPEREF_ZONE)
        m.SetAttValue('Code', u'SINGLETICKET')
        m.SetAttValue('Name', u'SINGLETICKET')
        m.SetAttValue('MatrixType', 'MATRIXTYPE_SKIM')


    res_matrix = Visum.Net.Matrices.ItemsByRef(ref).GetAll[0]
    res_matrix.SetValues(res)
    addIn.ReportMessage(u'calculated Fare Matrices',
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