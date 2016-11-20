# -*- coding: utf8 -*-


import wx
from VisumPy.AddIn import AddIn as AddIn_Base, AddInState 


class AddIn(AddIn_Base):
    ''' Use this class in Code of VISUM AddIns. The main features are:
        - determines if an AddIn is executed in DebugMode (e.g. from Eclipse)
        - creates a VISUM instance if AddIn is executed in DebugMode
        - Installs Gettext translations
        - checks if the translation already got installed and prevents installing
          an AddIn translation twice (e.g. in Dialog and the same again in Body script)
        - Logging functionality (writing into VISUM logging and/or displaying an message box)
        - allows a progress dialogue also 
    '''
    
    def ShowProgressDialog(self, captionText, infoText, maxCounter, setTimeMode = False):
        '''
        '''
        if setTimeMode:
            self.__progressDialog = wx.ProgressDialog(captionText, infoText, maxCounter,
                                     style = wx.PD_CAN_ABORT |
                                     wx.PD_ELAPSED_TIME |
                                     wx.PD_REMAINING_TIME |
                                     wx.PD_AUTO_HIDE)
        else:
            self.__progressDialog = wx.ProgressDialog(captionText, infoText, maxCounter,
                                      style = wx.PD_APP_MODAL | wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE)
        
    def UpdateProgressDialog(self, counter, messageText = None):
        '''
        Update the progress dialog
        Arguments: A counter,
                   the message text
        '''
        if self.__progressDialog == None and not self.ExecutionCanceled:
            if self.Language == Language.German:
                self.ReportMessage("Der ProgressDialog wurde nicht initialisiert, "
                                   "aus diesem Grund kann 'ProgressDialog.Update(counter)' nicht ausgeführt "
                                   "werden. Bitte initialisieren Sie den ProgressDialog durch den Aufruf "
                                   "der Funktion 'AddIn.ShowProgressDialog(captionText, infoText, maxCounter)'.")
            else:
                self.ReportMessage("ProgressDialog not initialized, for this 'ProgressDialog.Update' "
                                   "can not be executed. Please initialize the ProgressDialog via calling "
                                   "the function ''AddIn.ShowProgressDialog(captionText, infoText, maxCounter)'.")
        elif self.__progressDialog == None and self.ExecutionCanceled:
            return
        else:
            if messageText == None:
                self.ExecutionCanceled = (self.__progressDialog.Update(counter)[0] == False)
            else:
                self.ExecutionCanceled = (self.__progressDialog.Update(counter, messageText)[0] == False)
            if self.ExecutionCanceled:
                self.__progressDialog.Destroy()
                self.__progressDialog = None
    
    
