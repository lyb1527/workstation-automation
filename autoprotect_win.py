import re
import subprocess
from ldtp import *
from vm import *
from objname import *
from generalactions import GeneralActions
from settings import Settings
from snapshot import Snapshot
from commonutils import *
from loong import *
import time



class GeneralCase(object):

   def __init__(self, harness):
      self.harness = harness
      self.vmInst = VM(self.harness)
      self.settingInstance = Settings(self.harness)
      self.generalInst = GeneralActions(self.harness)

   def prepareAutoProtectVM(self, testdata):

       testdata = getTestDataList(testdata)
       self.vmInst.CreateNewVM(vmName=testdata['vmname'])
       selectmenuitem(mainWindow, mnuToSnapshotManager)
       click(snapshotManager, btnAutoProtect)
       check(vmSettingsWindow, chkEnableAutoProtect)
       click(vmSettingsWindow, btnOK)
       click(snapshotManager, btnClose)
       self.vmInst.CloseWorkstation()
       self.vmInst.SetVMXValue(self.vmInst.testvmDir, testdata['vmname'],
                               '%s.vmx' % testdata['vmname'],
                               'rollingTier0.interval', '"60"')
       self.vmInst.LaunchWorkstation()
       self.vmInst.PowerOnVM()
       # loop check if snapshot files exist
       vmName = testdata['vmname']
       status = False
       counter = 0
       timeToCreateFile = 60
       while not status and counter <= timeToCreateFile:
           wait(10)
           status = os.path.exists(
               "%s/%s/%s-Snapshot1.vmsn" % (self.vmInst.testvmDir, vmName,
                                            vmName))
           counter += 10
       self.harness.VerifySafely(status, True,
                                 "Auto-protect files created successfully")
       self.vmInst.PowerOffVM()

   def endTest(self):
      self.harness.UpdateTestcaseResult()

   def startRecovery(self, testdata):
      self.generalInst.DeleteTestVMDir()


class test1(GeneralCase):

   def startTest(self, testdata):
      self.harness.SetTestDescription(
         'Enable AutoProtect and verify the state '
         'of components on the AutoProtect setting page')

      self.vmInst.LaunchWorkstation()
      self.vmInst.CreateNewVM()
      self.settingInstance.OpenVMSettings()

      # Caculate the total memory of the 3 snapshots.
      vmMem = int(gettextvalue(VMSettings, txtMemoryforthisvirtualmachine))
      totalMem = str(round(vmMem * 3.0 / 1024, 1))
      if totalMem.rfind('.0') != -1:
         totalMem = totalMem.split('.0')[0]

      self.settingInstance.SelectSettingsOptions(ptabOptions, AutoProtect)
      check(VMSettings, chkEnableAutoProtect)
      self.generalInst.VerifyCheckBoxState(VMSettings,
                                           chkEnableAutoProtect,
                                           'Enabled')
      self.generalInst.VerifyState(VMSettings,
                                   cboAutoProtectinterval,
                                   'Enabled')
      self.generalInst.VerifyState(VMSettings,
                                   sbtnMaximumAutoProtectsnapshots,
                                   'Enabled')
      self.generalInst.VerifyState(VMSettings,
                                   autoProtectprompttext1,
                                   'Enabled')
      self.generalInst.VerifyState(
         VMSettings,
         'lblAutoProtectwillconsumeaminimumof{}GBofdiskspace'.format(totalMem),
         'Enabled')

      self.settingInstance.CloseVMSettings()
      self.vmInst.DeleteVM()
      self.vmInst.CloseWorkstation()


class test2(GeneralCase):

   def startTest(self, testdata):
      self.harness.SetTestDescription(
         'Open AutoProtect setting page from Snapshot Manager')

      self.vmInst.LaunchWorkstation()
      self.vmInst.CreateNewVM()

      self.harness.AddTestComment('Try to open snapshot manager')
      selectmenuitem(mainWindow, mnuToSnapshotManager)
      self.harness.VerifyFatal(waittillguiexist(snapshotManager),
                               1,
                               'Snapshot manager is opened.')
      click(snapshotManager, AutoProtect)
      self.harness.VerifyFatal(waittillguiexist(VMSettings),
                               1,
                               'VMsetting is opened.')
      self.harness.VerifySafely(guiexist(VMSettings, chkEnableAutoProtect),
                                1,
                                'Auto protect tab is selected.')

      self.settingInstance.CloseVMSettings()
      click(snapshotManager, btnClose)
      self.vmInst.DeleteVM()
      self.vmInst.CloseWorkstation()


class test3(GeneralCase):
    def startTest(self, testdata):
        self.harness.SetTestDescription("Check Show AutoProtect Snapshots "
                                        "checkbox and verify AutoProtect "
                                        "snapshots are displayed in "
                                        "snapshot graph")
        self.harness.AddTestComment("Create a new VM")
        self.vmInst.LaunchWorkstation()
        self.prepareAutoProtectVM(testdata)
        selectmenuitem(fsmainWindow, mnuToSnapshotManager)
        check(snapshotManager,
              chkShowAutoProtectSnapshots)
        region = getobjectsize(snapshotManager, expirePane)
        sikuliHighlight(region, 1)
        snapshotList = sikuliFindAll(region, picSnapshot)
        snapshotList.sort()
        generatemouseevent(snapshotList[0][0], snapshotList[0][1],
                           leftButtonClick)
        status = bool(gettextvalue(snapshotManager,
                                   txtSnapshotName) == autoProtectSnapshot)
        self.harness.VerifySafely(status, True,
                                  " AutoProtect snapshot is displayed")
        # verify un-check "show auto-protect"
        uncheck(snapshotManager, chkShowAutoProtectSnapshots)
        status = bool(gettextvalue(snapshotManager,
                                   txtSnapshotName) == '')
        self.harness.VerifySafely(status, True,
                                  "No Auto-protect snapshot displayed")
        click(snapshotManager, btnClose)
        self.vmInst.DeleteVM()
        self.vmInst.CloseWorkstation()


class test4(GeneralCase):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Delete single AutoProtect Snapshot')
        self.vmInst.LaunchWorkstation()
        self.prepareAutoProtectVM(testdata)
        selectmenuitem(fsmainWindow, mnuToSnapshotManager)
        check(snapshotManager,
              chkShowAutoProtectSnapshots)
        region = getobjectsize(snapshotManager, expirePane)
        sikuliHighlight(region, 1)
        snapshotList = sikuliFindAll(region, picSnapshot)
        snapshotList.sort()
        generatemouseevent(snapshotList[0][0], snapshotList[0][1],
                           leftButtonClick)
        click(snapshotManager, btnDelete)
        status = bool(gettextvalue(snapshotManager,
                                   txtSnapshotName) == autoProtectSnapshot)
        self.harness.VerifySafely(status, False,
                                  " AutoProtect snapshot is deleted")
        # verify snapshot related files deleted
        testdata = getTestDataList(testdata)
        vmName = testdata['vmname']
        status = os.path.exists(
            "%s/%s-Snapshot1.vmsn" % (self.vmInst.testvmDir, vmName))
        self.harness.VerifySafely(status, False,
                                  "Snapshot files removed successfully")
        click(snapshotManager, btnClose)
        self.vmInst.DeleteVM()
        self.vmInst.CloseWorkstation()


class test5(GeneralCase):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Revert to previous AutoProtect'
                                        ' snapshot')
        self.vmInst.LaunchWorkstation()
        self.prepareAutoProtectVM(testdata)
        self.vmInst.PowerOnVM()
        selectmenuitem(fsmainWindow, mnuToSnapshotManager)
        check(snapshotManager,
              chkShowAutoProtectSnapshots)
        region = getobjectsize(snapshotManager, expirePane)
        sikuliHighlight(region, 1)
        snapshotList = sikuliFindAll(region, picSnapshot)
        snapshotList.sort()
        generatemouseevent(snapshotList[0][0], snapshotList[0][1],
                           leftButtonClick)
        click(snapshotManager, btnGoTo)
        waittillguiexist(wsDialog)
        status = bool(gettextvalue(wsDialog,
                                   txt0) == autoSnapshotGoToDialogText )
        click(wsDialog, btnYes)
        # wait for 'go to' operation to finish
        waittillguinotexist(dlgVMwareWorkstation)
        self.vmInst.VerifyPowerOnState()
        self.vmInst.PowerOffVM()
        self.vmInst.DeleteVM()
        self.vmInst.CloseWorkstation()


class test6(GeneralCase):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Verify AutoProtect selector and '
                                        'setting exists under VM Settings '
                                        '-- Options tab')
        self.vmInst.LaunchWorkstation()
        self.vmInst.CreateNewVM()
        self.settingInstance.OpenVMSettings()
        waittillguiexist(vmSettingsWindow)
        status = bool(selecttab(vmSettingsWindow, ptl0, ptabOptions))
        self.harness.VerifySafely(status, True,
                                  "Open VM Settings->Options tab")
        status = bool(click(vmSettingsWindow, lstAutoProtect))
        self.harness.VerifySafely(status, True, "Selector for AutoProtect"
                                                " exists")
        status = getobjectproperty(vmSettingsWindow, lstAutoProtect,
                                   "children").__contains__("Disabled")
        self.harness.VerifySafely(status, True,
                                  "Default setting is Disabled")
        self.settingInstance.CloseVMSettings()
        self.harness.AddTestComment("Delete VM")
        self.vmInst.DeleteVM()
        self.vmInst.CloseWorkstation()


class test7(GeneralCase):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Verify default state of Enable'
                                        ' AutoProtect checkbox')

        self.vmInst.LaunchWorkstation()
        self.harness.AddTestComment("Create a new VM")
        self.vmInst.CreateNewVM()
        self.harness.AddTestComment("Launch VM Settings Dialog")
        self.settingInstance.OpenVMSettings()
        waittillguiexist(vmSettingsWindow)
        status = bool(selecttab(vmSettingsWindow, ptl0, ptabOptions))
        self.harness.VerifySafely(status, True, "Open VM Settings and then"
                                                "Options tab")
        status = bool(click(vmSettingsWindow, lstAutoProtect))
        self.harness.VerifySafely(status, True, "Select AutoProtect setting")

        status = self.generalInst.VerifyState(vmSettingsWindow,
                                              AutoProtect, 'SHOWING')
        self.harness.VerifySafely(status, True, "AutoProtect page is opened")

        status = bool(stateenabled(vmSettingsWindow, chkEnableAutoProtect))
        self.harness.VerifySafely(status, True,
                                  "Enable AutoProtect checkbox is enabled")

        status = bool(verifyuncheck(vmSettingsWindow, 'chkEnableAutoProtect'))
        self.harness.VerifySafely(status, True, "Enable AutoProtect checkbox"
                                                " is unchecked by default")
        self.settingInstance.CloseVMSettings()
        self.harness.AddTestComment("Delete VM")
        self.vmInst.DeleteVM()
        self.vmInst.CloseWorkstation()


class test8(GeneralCase):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Verify Keep functionality for '
                                        'single AutoProtect Snapshot')
        self.vmInst.LaunchWorkstation()
        self.prepareAutoProtectVM(testdata)
        testdata = getTestDataList(testdata)
        status = bool(selectmenuitem(mainWindow, mnuToSnapshotManager))
        self.harness.VerifySafely(status, True,
                                  "Open Snapshot Manager for the VM")
        waittillguiexist(snapshotManager)
        status = bool(check(snapshotManager, chkShowAutoProtectSnapshots))
        self.harness.VerifySafely(status, True, "Check Show AutoProtect "
                                                "Snapshots checkbox")
        region = getobjectsize(snapshotManager, expirePane)
        snapshotList = sikuliFindAll(region, picSnapshot)
        snapshotList.sort()
        generatemouseevent(snapshotList[0][0], snapshotList[0][1] - 10,
                           leftButtonClick)
        status = bool(gettextvalue(snapshotManager,
                                   txtSnapshotName) == autoProtectSnapshot)
        self.harness.VerifySafely(status, True,
                                  "AutoProtect snapshot selected ")
        status = bool(click(snapshotManager, btnKeep))
        self.harness.VerifySafely(status, True, "Click on Keep button")
        settextvalue(snapshotManager, txtSnapshotName, 'Kept Snapshot')

        status = bool(uncheck(snapshotManager, chkShowAutoProtectSnapshots))
        self.harness.VerifySafely(status, True,
                                  "Uncheck Show AutoProtect Snapshots"
                                  " checkbox")
        keptSnapshotImage = './loong/autoprotect/kept_autoprotect.png'
        status = bool(sikuliClick(region, keptSnapshotImage))
        self.harness.VerifySafely(status, True, "Successfully clicked on the"
                                    "kept autoprotect image, which verifies the"
                                    "the autoprotect snapshot is kept")

        click(snapshotManager, btnClose)
        self.vmInst.CloseWorkstation()
        self.vmInst.SetVMXValue(self.vmInst.testvmDir, testdata['vmname'],
                               '%s.vmx' % testdata['vmname'],
                               'rollingTier0.maximum', '"3"')
        self.vmInst.LaunchWorkstation()
        self.vmInst.PowerOnVM()
        selectmenuitem(mainWindow, mnuToSnapshotManager)
        check(snapshotManager, chkShowAutoProtectSnapshots)
        '''
        time for createing 3 AutoProtect snapshots is 180s, wait for 450s,
        if checked snapshot still exists after 450s, that means keepd snapshot
         is notaffected, only newly created AutoProtect is deleted
        '''
        wait(450)
        sikuliClick(region, keptSnapshotImage)
        status = bool(gettextvalue(snapshotManager,
                                   txtSnapshotName) == "Kept Snapshot")
        self.harness.VerifySafely(status, True,
                                  "Kept snapshot unaffected, newly created"
                                  "AutoProtect snapshot replaced")
        self.harness.AddTestComment("Close the Snapshot Manager")
        click(snapshotManager, btnClose)
        self.vmInst.PowerOffVM()
        self.vmInst.DeleteVM()
        self.vmInst.CloseWorkstation()


class test9(GeneralCase):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Verify the AutoProtect will keep'
                                        'text on AutoProtect setting page'
                                        'when AutoProtect interval Hourly')
        self.vmInst.LaunchWorkstation()
        self.vmInst.CreateNewVM()
        self.settingInstance.OpenVMSettings()
        status = bool(selecttab(vmSettingsWindow, ptl0, ptabOptions))
        self.harness.VerifySafely(status, True,
                                  "Open VM Settings->Options tab")
        status = bool(click(vmSettingsWindow, lstAutoProtect))
        self.harness.VerifySafely(status, True, "Select AutoProtect setting")
        status = generalInst.VerifyState(vmSettingsWindow, AutoProtect,
                                         'SHOWING')
        status = bool(check(vmSettingsWindow, chkEnableAutoProtect))
        self.harness.VerifySafely(status, True,
                                  "Check Enable AutoProtect checkbox")
        comboselect(vmSettingsWindow, cboAutoProtectinterval, 'Hourly')
        status = bool(verifyselect(vmSettingsWindow, cboAutoProtectinterval,
                                   'Hourly'))
        self.harness.VerifySafely(status, True,
                                  "AutoProtect interval set Hourly")
        # check default value for hourly
        MaxNumSnapshots = int(gettextvalue(vmSettingsWindow,
                                           sbtnMaximumAutoProtectsnapshots))
        self.harness.VerifySafely(MaxNumSnapshots, 3,
                                  "Verify Maximum snapshots default value")
        # input 10 for maximum snapshots and verify texts below
        settextvalue(vmSettingsWindow, sbtnMaximumAutoProtectsnapshots, '10')
        status = self.generalInst.VerifyState(vmSettingsWindow,
                                              autoprotectHourlyText, 'SHOWING')
        self.harness.VerifySafely(status, True, "Verify the text AutoProtect"
                                                " will keep a range of "
                                                "snapshots to provide different "
                                                "restore options")
        status = self.generalInst.VerifyState(vmSettingsWindow,
            'lblSnapshotstakeneveryhour4Snapshotstakeneveryday3Snapshots'
            'takeneveryweek3', 'SHOWING')
        self.harness.VerifySafely(status, True,
                "Verify that snapshots taken every hour: 4"
                "snapshots taken every day: 3"
                "snapshots taken every week:3")
        self.settingInstance.CloseVMSettings()
        self.harness.AddTestComment("Delete VM")
        self.vmInst.DeleteVM()
        self.vmInst.CloseWorkstation()


class test10(GeneralCase):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Verify the AutoProtect will keep '
                                        'text when AutoProtect interval ='
                                        ' Half Hourly')
        self.vmInst.LaunchWorkstation()
        self.vmInst.CreateNewVM()
        self.settingInstance.OpenVMSettings()
        status = bool(selecttab(vmSettingsWindow, ptl0, ptabOptions))
        self.harness.VerifySafely(status, True, "Open VM Settings then "
                                                "Options tab")
        status = bool(click(vmSettingsWindow, lstAutoProtect))
        self.harness.VerifySafely(status, True, "Select AutoProtect setting")
        status = self.generalInst.VerifyState(vmSettingsWindow,
                                              AutoProtect, 'SHOWING')
        status = bool(check(vmSettingsWindow, chkEnableAutoProtect))
        self.harness.VerifySafely(status, True,
                                  "Check Enable AutoProtect checkbox")
        status = bool(comboselect(vmSettingsWindow,
                                  cboAutoProtectinterval, 'Half-Hourly'))
        self.harness.VerifySafely(status, True,
                                  "AutoProtect interval set to Half-Hourly")
        # check default value
        MaxNumSnapshots = int(gettextvalue(vmSettingsWindow,
                                           sbtnMaximumAutoProtectsnapshots))
        self.harness.VerifySafely(MaxNumSnapshots, 3,
                                  "Verify Maximum snapshots default value")
        # set maximum to 10 to verify texts below
        settextvalue(vmSettingsWindow, sbtnMaximumAutoProtectsnapshots, '10')
        status = self.generalInst.VerifyState(vmSettingsWindow,
            autoprotectHourlyText, 'SHOWING')
        self.harness.VerifySafely(status, True, "Verify the text AutoProtect"
                                                " will keep a range of "
                                                "snapshots to provide "
                                                "different restore options")
        status = self.generalInst.VerifyState(vmSettingsWindow,
                                                           'lblSnapshotstaken'
                                                           'everyhalfhour4'
                                                           'Snapshotstaken'
                                                           'everyhour3Snapshots'
                                                           'takeneveryday3'
                                                            , 'SHOWING')
        self.harness.VerifySafely(status, True,
                "Verify the text snapshot every half hour: 4"
                "snapshot taken every hour : 3"
                "snapshot taken every hour: 3")
        self.settingInstance.CloseVMSettings()
        self.harness.AddTestComment("Delete VM")
        self.vmInst.DeleteVM()
        self.vmInst.CloseWorkstation()


class test11(GeneralCase):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Verify the context menu for single '
                                        'AutoProtect snapshot selection')
        self.vmInst.LaunchWorkstation()
        self.prepareAutoProtectVM(testdata)
        status = bool(selectmenuitem(mainWindow, mnuToSnapshotManager))
        self.harness.VerifySafely(status, True,
                                  "Open Snapshot Manager for the VM")
        check(snapshotManager, chkShowAutoProtectSnapshots)
        region = getobjectsize(snapshotManager, expirePane)
        sikuliHighlight(region, 1)
        sikuliRightClick(region, [region[0] + 100, region[1] + 60])
        items = [mnuGotoSnapshot, mnuKeep, mnuCloneThisSnapshot,
                 mnuDelete, mnuDeleteSnapshotandChildren,
                 mnuSelectAll]
        for item in items:
            status = bool(objectexist(mnuContext, item))
            self.harness.VerifySafely(status, True, "Context menu contains "
                                                    "%s " % item)
        self.generalInst.SendKeyboardInput('<esc>', snapshotManager)
        # ctrl+ t, ctrl + o, ctrl + a
        keys = ['<Ctrl>t', '<Ctrl>o', '<Ctrl>a']
        windows = [takeSnapshotWindow, cloneWizard,  vmSettingsWindow]
        for key, window in zip(keys, windows):
            self.generalInst.SendKeyboardInput(key, snapshotManager)
            self.harness.VerifySafely(bool(waittillguinotexist(window)),
                                      True,
                                      "%s window is closed" % window)
            click(window, btnCancel)
        # ctrl + g
        self.generalInst.SendKeyboardInput('<Ctrl>g', snapshotManager)
        self.harness.VerifySafely(bool(waittillguinotexist(dlgQuestion)),
                                  True,
                                 "Workstation Confirmation window "
                                 "is opened up")
        click(dlgQuestion, btnNo)
        sikuliClick(region, [region[0] + 100, region[1] + 60])
        # ctrl + k
        self.generalInst.SendKeyboardInput('<Ctrl>k', snapshotManager)
        keptSnapshotImage = './loong/autoprotect/kept_autoprotect.png'
        status = bool(sikuliClick(region, keptSnapshotImage))
        self.harness.VerifySafely(status, True, "Autoprotect snapshot"
                                                  "is kept")
        # ctrl + e
        self.generalInst.SendKeyboardInput('<Ctrl>e', snapshotManager)
        self.harness.VerifySafely(bool(
            verifysettext(snapshotManager, txtSnapshotName,
                          autoProtectSnapshot)),
                                  False,
                                  "AutoProtect snapshot is deleted")
        # ctrl + c
        self.generalInst.SendKeyboardInput('<alt>c', snapshotManager)
        self.harness.VerifySafely(
            bool(waittillguinotexist(snapshotManager)),
            True,
            "Snapshot Manager window is closed")

        self.vmInst.DeleteVM()
        self.vmInst.CloseWorkstation()


class test12(GeneralCase):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Verify the state of Show '
                                        'AutoProtect Snapshots checkbox')
        self.vmInst.LaunchWorkstation()
        self.prepareAutoProtectVM(testdata)
        self.vmInst.PowerOnVM()
        status = bool(selectmenuitem(mainWindow, mnuToSnapshotManager))
        self.harness.VerifySafely(status, True,
                                  "Open Snapshot Manager for the VM")
        status = bool(
            verifyuncheck(snapshotManager, chkShowAutoProtectSnapshots))
        self.harness.VerifySafely(status, True,
                                  "The ShowAutoProtectSnapshots checkbox is"
                                  "unchecked as default")
        status = bool(check(snapshotManager, chkShowAutoProtectSnapshots))
        self.harness.VerifySafely(status, True,
                                  "Check Show AutoProtect Snapshots checkbox")
        click(snapshotManager, btnClose)
        self.vmInst.CloseWorkstation()
        wait(2)
        self.vmInst.LaunchWorkstation()
        status = bool(selectmenuitem(mainWindow, mnuToSnapshotManager))
        self.harness.VerifySafely(status, True,
                                  "Open Snapshot Manager for the VM")
        status = bool(verifycheck(snapshotManager,
                                  chkShowAutoProtectSnapshots))
        self.harness.VerifySafely(status, True,
                                  "The ShowAutoProtectSnapshots \
                               checkbox of the VM is checked")
        click(snapshotManager, btnClose)
        self.vmInst.DeleteVM()
        self.vmInst.CloseWorkstation()