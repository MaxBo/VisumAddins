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
    calibrate_demand_model(dm, addIn)


def calibrate_demand_model(dm, addIn, 
                           attenuation=0.4, attenuation_trip_length=.5):

    modes = Visum.Net.Modes
    attrs = modes.Attributes.GetAll
    mode_codes = ['F','R','O','M','P']
    cols = [attr.Code for attr in attrs 
            if attr.Code.startswith(u'TARGET_MODAL_SPLIT') 
            or attr.Code == u'Code']
    target_modal_split = np.rec.array(
        modes.GetMultipleAttributes(cols), names=cols)
    
    group_definitions = ['car_availability', 'occupation']
    groups = {}
    
    for gd in group_definitions:
        groups[gd] = np.unique(
            [a[1] 
             for a in dm.PersonGroups.GetMultiAttValues(gd)])
        for group in groups[gd]:
            if group and group <> 'NULL':
                print(group)
                trips_group = 'trips_{gd}_{g}'.format(gd=gd, g=group)
                total_trips = Visum.Net.AttValue(trips_group)
                print(total_trips)
                addIn.ReportMessage(u'group {g}: total_trips: {t:0.0f}'.format(
                    g=group, t=total_trips), messageType=2)                
                for mode in modes:
                    is_demand = mode.AttValue('DemandMode')
                    if is_demand:
                        mode_code = mode.AttValue('Code')
                        mode_name = mode.AttValue('Name_Coeff')
                        print(mode_name)
                        trips_group_mode = '_'.join([trips_group, mode_code])
                        trips_mode = Visum.Net.AttValue(trips_group_mode)
                        modelled_ms = trips_mode/total_trips
                        print('{ms:.2f}%'.format(ms=modelled_ms*100))
                        target = mode.AttValue(
                            'TARGET_MODAL_SPLIT_{g}'.format(g=group))
                        print('{ms:.2f}%'.format(ms=target*100))
                        addIn.ReportMessage(u'mode {m}: modelled: {ms:.2f}%, target: {ts:.2f}%'.format(
                            m=mode_name, ms=modelled_ms*100, ts=target*100), 
                                            messageType=2)                
                        if modelled_ms > 0:
                            attname = 'Const_{m}_{g}'.format(m=mode_name,
                                                             g=group)
                            print(attname)
                            coeff = Visum.Net.AttValue(attname)
                            print('coeff: {d:.2f}'.format(d=coeff))
                            diff = np.log(target/modelled_ms)
                            print('change: {d:.2f}'.format(d=diff))
                            coeff_new = coeff + (diff * attenuation)
                            addIn.ReportMessage(u'mode {m}: before: {b:.2f}, after: {a:.2f}'.format(
                                m=mode_name, b=coeff, a=coeff_new), 
                                                messageType=2)                
                            Visum.Net.SetAttValue(attname, coeff_new)
                
        
    attname_actual_distance = 'Trip_Distance_Activity_{a}'
    attname_target_distance = 'Target_Mean_Distance'
    for act in dm.Activities.GetAll:
        a = act.AttValue('Code')
        if act.AttValue('AutoCalibrate') :
            target = act.AttValue(attname_target_distance)
            actual = Visum.Net.AttValue(attname_actual_distance.format(a=a))
            ls_param = Visum.Net.AttValue('LS_{}'.format(a))
            print('{a}: ist: {ist:.2f} km, soll:{target:.2f} km, ls: {ls:.2f}'.format(
            a=a, ist=actual, target=target, ls=ls_param))
            factor = (actual / target) ** attenuation_trip_length
            ls_new = ls_param * factor
            print('ls: {ls:.2f}'.format(ls=ls_new))
            addIn.ReportMessage(u'activity {a}: ist: {ist:.2f} km, soll:{target:.2f} km, ls_before: {lb:.2f}, ls_after: {la:.2f}'.format(
                a=a, ist=actual, target=target, lb=ls_param, la=ls_new), 
                                messageType=2)                
            actual = Visum.Net.SetAttValue('LS_{}'.format(a), ls_new)

    addIn.ReportMessage(u'Coefficient changed', messageType=2)


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
