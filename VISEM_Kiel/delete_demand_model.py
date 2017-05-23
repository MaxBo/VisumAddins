# -*- coding: utf-8 -*-


import sys

import numpy as np
from visumhelpers.visumpy_with_progress_dialog import AddIn, AddInState, AddInParameter


def main(Visum, addIn, demand_model):
    """"""
    undo = Visum.UserPreferences.EnvironmentUserPreferences.AttValue("UseUndoStack")
    Visum.UserPreferences.EnvironmentUserPreferences.SetAttValue("UseUndoStack", 0)
    dms = Visum.Net.DemandModels
    if not demand_model in (d[1] for d in dms.GetMultiAttValues('Code')):
        raise KeyError('Demand Model {d} not found'.format(d=demand_model))
    dm = dms.ItemByKey(demand_model)
    delete_all_person_groups(dm, addIn)
    delete_all_activities(dm, addIn)
    delete_demand_model(dm, addIn)
    Visum.UserPreferences.EnvironmentUserPreferences.SetAttValue("UseUndoStack", undo)


def delete_all_person_groups(dm, addIn):

    n_person_groups = dm.PersonGroups.Count

    addIn.ShowProgressDialog(
        u"Delete {N} Person Groups".format(N=n_person_groups),
        u"Delete Person Groups", n_person_groups, setTimeMode=True)

    # Distribution Parameters by Group
    i = 0
    for ds in dm.PersonGroups:
        i += 1
        if addIn.ExecutionCanceled:
            raise RuntimeError(u'Aborted at Person Group {i}'.format(i=i))
        Visum.Net.RemovePersonGroup(ds)

        addIn.UpdateProgressDialog(
            i, u'Delete Person Group {i}'.format(i=i))


    addIn.UpdateProgressDialog(n_person_groups)
    addIn.CloseProgressDialog()
    addIn.ReportMessage(u'{i} Person Groups deleted'.format(i=i),
                        messageType=2)

def delete_all_activities(dm, addIn):

    n_activities = dm.Activities.Count

    addIn.ShowProgressDialog(
        u"Delete {N} Activities".format(N=n_activities),
        u"Delete Activity", n_activities, setTimeMode=True)

    # Distribution Parameters by Group
    i = 0
    for ds in dm.Activities:
        i += 1
        if addIn.ExecutionCanceled:
            raise RuntimeError(u'Aborted at Activity {i}'.format(i=i))
        Visum.Net.RemoveActivity(ds)

        addIn.UpdateProgressDialog(
            i, u'Delete Activity {i}'.format(i=i))


    addIn.UpdateProgressDialog(n_activities)
    addIn.CloseProgressDialog()
    addIn.ReportMessage(u'{i} Activities deleted'.format(i=i),
                        messageType=2)


def delete_demand_model(dm, addIn):
    """Delete the demand model"""
    dm_code = dm.AttValue('Code')
    Visum.Net.RemoveDemandModel(dm)
    addIn.ReportMessage(u'Demand Model {dm} deleted'.format(dm=dm_code),
                        messageType=2)



if __name__ == '__main__':
    if len(sys.argv) > 1:
        addIn = AddIn()
    else:
        addIn = AddIn(Visum)

    if addIn.IsInDebugMode:
        app = wx.PySimpleApp(0)
        Visum = addIn.VISUM
        addInParam = AddInParameter(addIn, None)
    else:
        addInParam = AddInParameter(addIn, Parameter)

    default_params = {'DemandModel': 'VisemT'}
    param = addInParam.Check(True, default_params)
    demand_model = param['DemandModel']

    if addIn.State != AddInState.OK:
        addIn.ReportMessage(addIn.ErrorObjects[0].ErrorMessage)
    else:
        try:
            main(Visum, addIn, demand_model)
        except:
            addIn.HandleException(addIn.TemplateText.MainApplicationError)
