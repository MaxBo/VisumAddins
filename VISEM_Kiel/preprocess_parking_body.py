# -*- coding: utf-8 -*-


import numpy as np


def main():
    """"""
    code = 'VisemT'
    dm = Visum.Net.DemandModels.ItemByKey(code)

    add_parking_by_activity(dm)


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

    for act in acts:
        if act.AttValue('IsHomeActivity'):
            for z, p in enumerate(different_park_zones):
                park_costs_home[z] = \
                    act.AttValue('PARKING_ZONE_{p}'.format(p=p))
                costs_at_homezone = np.take(
                    park_costs_home, park_id)[:, np.newaxis]

    for act in acts:
        if not act.AttValue('IsHomeActivity'):
            a_code = act.AttValue('Code')
            a_name = act.AttValue('Name')
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


if __name__ == '__main__':
    main()
