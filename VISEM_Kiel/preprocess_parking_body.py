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

    add_parking_by_activity(dm, addIn)


def add_parking_by_activity(dm, skim='PARKING', home='W'):
    """Add weighted PT Skim Matrices"""

    p = Visum.Net.Zones.GetMultipleAttributes(('Park_Typ',))
    park_typ = np.array(p).ravel().astype('i4')
    different_park_zones, park_id = np.unique(park_typ, return_inverse=True)
    n_park_zones = len(different_park_zones)
    
    park_costs_home = np.zeros((n_park_zones), dtype='d')
    park_costs = np.zeros((n_park_zones), dtype='d')
    activities = dm.Activities
    acts = activities.GetAll
    n_activities = len(acts)
    
    addIn.ShowProgressDialog("Calculate Parking Matrices for {N} Activities".format(N=n_activities).decode("iso-8859-15"),
                             "Calculate Parking Matrices", n_activities, setTimeMode=True)
    i = 1
    for act in acts:
        if act.AttValue('IsHomeActivity'):
            if addIn.ExecutionCanceled:
                raise RuntimeError('Aborted at Activity {i}'.format(i=i))       
            addIn.UpdateProgressDialog(i, u'Calculate Parking at Home')
            
            for z, p in enumerate(different_park_zones):
                park_costs_home[z] = \
                    act.AttValue('PARKING_ZONE_{p}'.format(p=p))
                costs_at_homezone = np.take(
                    park_costs_home, park_id)[:, np.newaxis]

    for act in acts:
        if not act.AttValue('IsHomeActivity'):
            i += 1
            a_code = act.AttValue('Code')
            a_name = act.AttValue('Name')
            if addIn.ExecutionCanceled:
                raise RuntimeError('Aborted at Activity {i}'.format(i=i))       
            addIn.UpdateProgressDialog(i, u'Calculate Matrix PARKING_{a} for {b}'.format(
                a=a_code, b=a_name))
            
            for z, p in enumerate(different_park_zones):
                park_costs[z] = act.AttValue('PARKING_ZONE_{p}'.format(p=p))
                costs_at_destination = np.take(park_costs, park_id)
            total_costs = (costs_at_homezone + costs_at_destination) / 2
            ref = 'MATRIX([CODE] = "PARKING_{a}")'.format(a=a_code)
            try:
                m = Visum.Net.Matrices.ItemsByRef(ref).GetAll[0]
            except Exception:
                raise ValueError(ref)
            m.SetValues(total_costs)

    addIn.UpdateProgressDialog(n_activities)
    addIn.CloseProgressDialog()
    addIn.ReportMessage(u'calculated Parking Matrices for {i} activities'.format(i=i),
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
