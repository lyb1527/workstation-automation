# Copyright 2016 VMware, Inc.  All rights reserved. -- VMware Confidential
# -*- coding: utf-8 -*-
import os
from vm import *
from hostd import *
from tools import *
from install import *
from snapshot import *
from settings import *
from preferences import *
from generalactions import *
from commonutils import *
from objname import *
from loong import *
import socket

class General(object):
   def __init__(self, harness):
      self.harness = harness
      self.vmInst = VM(self.harness)
      self.settingsInst = Settings(self.harness)
      self.generalInst = GeneralActions(self.harness)
      self.hostInst = Hostd(self.harness)
      self.prefInst = Preferences(self.harness)
      self.vmname_win10x64 = 'Microsoft Windows 10 (64-bit)'
      self.local_vmname_win10x64 = 'Windows 10 x64*'
      self.testvmDir = self.harness.testInfo['wintestvmdir']
      self.defaultSharedVMDir = self.harness.testInfo['winhostdshareddir']

   def shareVMViaMenu(self):
      selectmenuitem(mainWindow, mnuToSharing)
      waittillguiexist(shareWizard, btnClose)
      click(shareWizard, btnNext)
      click(shareWizard, btnFinish)
      status = False
      while not status:
          status =self.generalInst.VerifyState(shareWizard, btnClose,
                                               'ENABLED')
          if status:
              click(shareWizard, btnClose)

   def connectToServer(self, testdata):
      testdata = getTestDataList(testdata)
      self.vmname = testdata['vmname']
      selectrow(mainWindow, 'ttbl0', sharedVms)
      if waittillguiexist(dlgConnecttoServer):
          username = testdata['username']
          password = testdata['password']
          settextvalue(connectToServer, txtUsername, username)
          enterstring(connectToServer, txtPassword, password)
          click(connectToServer, btnConnect)

      click(dlgConnecttoServer, btnCancel)
      click(dlgConnecttoServer, btnCancel)



   def deleteSharedVM(self, vmname):
      selectmenuitem(mainWindow, mnuStopSharing)
      click(stopSharingWizard, btnNext)
      click(stopSharingWizard, btnFinish)
      if waittillguiexist(stopSharingWizard):
          click(stopSharingWizard, btnClose)
      self.vmInst.DeleteVM(vmName=vmname)

   def endTest(self):
      if self.harness.performanceTest:
         self.harness.performanceFlag = False
      self.harness.UpdateTestcaseResult()
      self.generalInst.DeleteTestVMDir()
      self.generalInst.DeleteSharedVMDir()

   def startRecovery(self):
      self.generalInst.DeleteTestVMDir()
      self.generalInst.DeleteSharedVMDir()
      self.generalInst.DeletePreferenceFile()

class sharedVM1(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription("SharedVM 1 - Create a shared vm from"
                                      " Shared VMs tab")
      self.harness.AddTestComment("Launch Workstation")
      self.vmInst.LaunchWorkstation()
      self.vmInst.CreateNewVM(osVersion = self.vmname_win10x64,
                              shared = True)
      self.settingsInst.SetWorkspacePrefs('NEWVMPATH')
      self.vmInst.PowerOnVM()
      self.generalInst.VerifyMenuState(False, 'VM', 'Power', 'Power On')
      self.generalInst.VerifyMenuState(True, 'View', mnuFullScreen)
      self.vmInst.PowerOffVM()
      self.generalInst.VerifyMenuState(False, 'VM', 'Power', 'Power Off')
      self.vmInst.CloseWorkstation()

class sharedVM2(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription("Shared VM 2 - Default unsharing location"
                                      " validation")
      self.harness.AddTestComment("Launch Workstation")
      self.vmInst.LaunchWorkstation()
      self.vmInst.CreateNewVM(osVersion = self.vmname_win10x64,
                              shared = True)
      self.settingsInst.SetWorkspacePrefs('NEWVMPATH')
      self.harness.AddTestComment("Get default standard vm location")
      self.prefInst.OpenPrefWindow()
      default_location = gettextvalue(prefWindow,
                                      txtDefaultlocationforvirtualmachines)
      self.prefInst.VerifyClosePrefWindow()
      self.harness.AddTestComment("Select Win 10 shared VM")
      self.vmInst.selectVM(self.vmname_win10x64)
      self.harness.AddTestComment("Open stop share vm Wizard")
      self.hostInst.OpenStopShareVMWizard(vmName=self.vmname_win10x64)
      if waittillguiexist(stopSharingWizard) == 0:
         raise LdtpExecutionError('%s does not appear' % stopSharingWizard)
      self.harness.AddTestComment("Click Next button on Stop sharing Wizard")
      click(stopSharingWizard, btnNext)
      unshareVM_location = gettextvalue(stopSharingWizard,
                                        stopShareVMLocationValue)
      default_vm_path = default_location + "\\{}".format(self.vmname_win10x64)
      if default_vm_path == unshareVM_location:
         status = True
      else:
         status = False
      self.harness.VerifySafely(status, True, "The stop sharing location "
                                              "matched with standard vm "
                                              "location!")
      self.hostInst.VerifyCloseStopSharingWizard()
      self.vmInst.CloseWorkstation()

class sharedVM3(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription("Shared VM 3 - Disable VM Sharing "
                                      "in preferences")
      self.harness.AddTestComment("Launch Workstation")
      self.vmInst.LaunchWorkstation()
      self.prefInst.OpenPrefWindow()
      selectrow(prefWindow, lst0, lstSharedVMs)
      click(prefWindow, disable_sharing_btn)
      status = False
      if waittillguiexist(prefWindow, enable_sharing_btn):
         status = True
      self.harness.VerifySafely(status, True, "The Enable Sharing button "
                                              "is enabled.")
      self.prefInst.ClosePrefWindow()
      selectrow(mainWindow, 'ttbl0', sharedVms)
      status = False
      if waittillguiexist(dlgError2):
         status = True
         click(dlgError2, btnOK)
      self.harness.VerifySafely(status, True, "The Sharing is disabled.")
      self.prefInst.EnableSharing()
      self.vmInst.CloseWorkstation()

class sharedVM4(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription("Shared VM 4 - Shared VM node in the "
                                      "Library")
      self.harness.AddTestComment("Launch Workstation")
      self.vmInst.LaunchWorkstation()
      self.vmInst.CreateNewVM(osVersion = self.vmname_win10x64,
                              shared = True)
      self.settingsInst.SetWorkspacePrefs('NEWVMPATH')
      self.harness.AddTestComment("Select Win 10 shared VM")
      self.vmInst.selectVM(self.vmname_win10x64)
      objname = self.generalInst.getObjName('btn',self.vmname_win10x64)
      status = False
      if waittillguiexist(mainWindow, objname):
         status = True
      self.harness.VerifySafely(status, True, "The Shared VM tab is opened.")
      self.vmInst.CloseWorkstation()

class sharedVM5(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription("Shared VM 5 - Custom unsharing location")
      self.harness.AddTestComment("Launch Workstation")
      self.vmInst.LaunchWorkstation()
      self.vmInst.CreateNewVM(osVersion = self.vmname_win10x64,
                              shared = True)
      self.settingsInst.SetWorkspacePrefs('NEWVMPATH')
      self.harness.AddTestComment("Select Win 10 shared VM")
      self.vmInst.selectVM(self.vmname_win10x64)
      self.harness.AddTestComment("Open stop share vm Wizard")
      self.hostInst.OpenStopShareVMWizard(vmName=self.vmname_win10x64)
      if waittillguiexist(stopSharingWizard) == 0:
         raise LdtpExecutionError('%s does not appear' % stopSharingWizard)
      self.harness.AddTestComment("Click Next button on Stop sharing Wizard")
      click(stopSharingWizard, btnNext)
      custom_unshare_location = '{}\\sharevm_temp\\{}'.format(self.testvmDir,
                                                         self.vmname_win10x64)
      custom_unshare_vmx_location = '{}\\{}.vmx'.format(self.vmname_win10x64,
                                                        self.vmname_win10x64)
      settextvalue(stopSharingWizard, stopShareVMLocationValue,
                   custom_unshare_location)
      click(stopSharingWizard, btnFinish)
      if waittillguiexist(stopSharingWizard, btnClose):
         self.harness.AddTestComment("Close the stop share wizard")
         click(stopSharingWizard, btnClose)
      vm_objname = self.generalInst.getObjName('tblc', self.vmname_win10x64)
      waittillguiexist(mainWindow, vm_objname)
      status = False
      if getobjectproperty(mainWindow, vm_objname, 'parent') == MY_COMPUTER:
         status = True
      self.harness.VerifySafely(status, True, "The Shared VM is unshared.")
      status = False
      if os.path.exists(custom_unshare_vmx_location):
         status = True
      self.harness.VerifySafely(status, True, "The Shared VM exists in "
                                              "custom path.")
      self.vmInst.CloseWorkstation()

class sharedVM6(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription("Shared VM 6 - Modify datastore location "
                                      "if shared VMs are available")
      self.harness.AddTestComment("Launch Workstation")
      self.vmInst.LaunchWorkstation()
      self.vmInst.CreateNewVM(osVersion = self.vmname_win10x64,
                              shared = True)
      # Open Preference to change shared vm location
      self.prefInst.OpenPrefWindow()
      selectrow(prefWindow, lst0, lstSharedVMs)
      # Check the Browse button is disabled
      status = False
      if not hasstate(prefWindow, btnBrowse, 'enabled'):
         status = True
      self.harness.VerifySafely(status, True, "The Browse button is disabled")
      status = False
      if not hasstate(prefWindow, SHARED_VM_LOCATION, 'enabled'):
         status = True
      self.harness.VerifySafely(status, True, "The Browse path text box "
                                              "is disabled")
      self.vmInst.CloseWorkstation()

class sharedVM7(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription("Shared VM 7 - Modify datastore location "
                                      "if there is no Shared VMs")
      self.harness.AddTestComment("Launch Workstation")
      self.vmInst.LaunchWorkstation()
      # Open Preference to change shared vm location
      self.prefInst.OpenPrefWindow()
      selectrow(prefWindow, lst0, lstSharedVMs)
      for i in range(10):
         currentSharedVMPath = gettextvalue(prefWindow, SHARED_VM_LOCATION)
         if currentSharedVMPath == '':
            wait(1)
         else:
            break
      click(prefWindow, btnBrowse)
      selectrow(winBrowseForFolder, BROWSE_FILE_PATH, 'Desktop')
      click(winBrowseForFolder, btnOK)
      #Click OK to save the new Path
      click(prefWindow, btnOK)
      # Open Preference window again to verify shared vm location
      self.prefInst.OpenPrefWindow()
      selectrow(prefWindow, lst0, lstSharedVMs)
      status = False
      if gettextvalue(prefWindow,
                      SHARED_VM_LOCATION) == os.path.expanduser('~\Desktop'):
         status = True
      self.harness.VerifySafely(status, True, "Modify the shared vm path "
                                              "passed")
      settextvalue(prefWindow, SHARED_VM_LOCATION, currentSharedVMPath)
      click(prefWindow, btnOK)
      # Open Preference to change shared vm location
      self.prefInst.OpenPrefWindow()
      selectrow(prefWindow, lst0, lstSharedVMs)
      status = False
      if gettextvalue(prefWindow,
                      SHARED_VM_LOCATION) == currentSharedVMPath:
         status = True
      self.harness.VerifySafely(status, True, "Revert back to default "
                                              "shared vm path")
      click(prefWindow, btnOK)
      self.vmInst.CloseWorkstation()

class sharedVM8(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription("Shared VM 8 - Modify shared VM name "
                                      "while cloning ")
      self.harness.AddTestComment("Launch Workstation")
      self.vmInst.LaunchWorkstation()
      #Create a local VM
      self.vmInst.CreateNewVM(osVersion = self.local_vmname_win10x64)
      self.vmInst.selectVM(self.local_vmname_win10x64)
      self.harness.AddTestComment("Open share vm Wizard")
      self.hostInst.OpenShareVMWizard(vmName=self.local_vmname_win10x64)
      click(shareWizard, btnNext)
      click(shareWizard, MAKE_FULL_CLONE_RADIO_BUTTON)
      cloneName = gettextvalue(shareWizard, txtSharedVirtualMachineName)
      status = bool(cloneName == '{}{}'.format('Clone of ',
                                               self.local_vmname_win10x64))
      self.harness.VerifySafely(status, True, 'The clone name is correct')
      temp_vmname = 'temp_vm'
      settextvalue(shareWizard, txtSharedVirtualMachineName, temp_vmname)
      click(shareWizard, btnFinish)
      waittillguiexist(shareWizard, lblDone)
      click(shareWizard, btnClose)
      status = bool(waittillguiexist(mainWindow, temp_vmname))
      self.harness.VerifySafely(status, True, 'The clone vm is appear')
      self.vmInst.PowerOnVM()
      self.generalInst.VerifyMenuState(False, 'VM', 'Power', 'Power On')
      self.generalInst.VerifyMenuState(True, 'View', mnuFullScreen)
      self.vmInst.PowerOffVM()
      self.generalInst.VerifyMenuState(False, 'VM', 'Power', 'Power Off')
      self.vmInst.CloseWorkstation()

class sharedVM9(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription("Shared VM 9 - New Shared VMs Location "
                                      "registration")
      self.harness.AddTestComment("Launch Workstation")
      self.vmInst.LaunchWorkstation()
      self.prefInst.OpenPrefWindow()
      selectrow(prefWindow, lst0, lstSharedVMs)
      for i in range(10):
         currentSharedVMPath = gettextvalue(prefWindow, SHARED_VM_LOCATION)
         if currentSharedVMPath == '':
            wait(1)
         else:
            break
      temppath = 'C:\\Users\\Public\\Documents\\temppath'
      settextvalue(prefWindow, SHARED_VM_LOCATION, temppath)
      for i in range(10):
         modifiedSharedVMPath = gettextvalue(prefWindow, SHARED_VM_LOCATION)
         if modifiedSharedVMPath == temppath:
            break
         else:
            wait(1)
      #Click OK to save the new Path
      click(prefWindow, btnOK)
      # Wait 2 seconds to let the config write to the datastores.xml
      wait(2)
      status = bool(temppath == self.hostInst.getDatastoreLocation())
      self.harness.VerifySafely(status, True, "The Shared VM path is "
                                              "registered in datastores.xml "
                                              "under C:\ProgramData\VMware\
                                              hostd")
      # Open Preference window again to verify shared vm location
      self.prefInst.OpenPrefWindow()
      selectrow(prefWindow, lst0, lstSharedVMs)
      status = bool(gettextvalue(prefWindow, SHARED_VM_LOCATION) == temppath)
      self.harness.VerifySafely(status, True, "Modify the shared vm path "
                                              "passed")
      # Change shared vm location to default path
      settextvalue(prefWindow, SHARED_VM_LOCATION, currentSharedVMPath)
      for i in range(10):
         modifiedSharedVMPath = gettextvalue(prefWindow, SHARED_VM_LOCATION)
         if modifiedSharedVMPath == currentSharedVMPath:
            break
         else:
            wait(1)
      click(prefWindow, btnOK)
      self.prefInst.OpenPrefWindow()
      selectrow(prefWindow, lst0, lstSharedVMs)
      status = bool(gettextvalue(prefWindow,
                                 SHARED_VM_LOCATION) == currentSharedVMPath)
      self.harness.VerifySafely(status, True, "Revert back to default "
                                              "shared vm path")
      click(prefWindow, btnOK)
      self.vmInst.CloseWorkstation()

class sharedVM10(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription("Shared VM 10 - Share VM using Clone "
                                      "option")
      self.harness.AddTestComment("Launch Workstation")
      self.vmInst.LaunchWorkstation()
      # Create a local VM
      self.vmInst.CreateNewVM(osVersion=self.local_vmname_win10x64)
      self.vmInst.selectVM(self.local_vmname_win10x64)
      self.harness.AddTestComment("Open share vm Wizard")
      self.hostInst.OpenShareVMWizard(vmName=self.local_vmname_win10x64)
      cloneVMName = 'CloneVM'
      self.hostInst.ShareVM("Clone", "menu", cloneVMName, 'Finish')
      self.vmInst.PowerOnVM()
      self.vmInst.VerifyPowerOnState(shared=True)
      self.vmInst.PowerOffVM()
      self.vmInst.VerifyPowerOffState(shared=True)
      self.vmInst.CloseWorkstation()

class sharedVM11(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription("Shared VM 11 - Share VM using Move "
                                      "option")
      self.harness.AddTestComment("Launch Workstation")
      self.vmInst.LaunchWorkstation()
      # Create a local VM
      self.vmInst.CreateNewVM(osVersion=self.local_vmname_win10x64)
      self.vmInst.selectVM(self.local_vmname_win10x64)
      self.harness.AddTestComment("Open share vm Wizard")
      self.hostInst.OpenShareVMWizard(vmName=self.local_vmname_win10x64)
      self.hostInst.ShareVM("Move", "menu", self.local_vmname_win10x64,
                            'Finish')
      self.vmInst.CloseWorkstation()

class sharedVM12(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription("Shared VM 12 - Shared VM unsharing "
                                      "flow")
      self.harness.AddTestComment("Launch Workstation")
      self.vmInst.LaunchWorkstation()
      self.vmInst.CreateNewVM(osVersion = self.vmname_win10x64,
                              shared = True)
      self.harness.AddTestComment("Select Win 10 shared VM")
      self.vmInst.selectVM(self.vmname_win10x64)
      self.harness.AddTestComment("Open stop share vm Wizard")
      self.hostInst.OpenStopShareVMWizard(vmName=self.vmname_win10x64)
      self.hostInst.StopShareVM(self.vmname_win10x64, 'Finish')
      self.vmInst.DeleteVM(self.vmname_win10x64)
      self.vmInst.CloseWorkstation()


class sharedVM14(General):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Sharing related context menu items'
                                        'for standard VM functionality')
        self.vmInst.LaunchWorkstation()
        self.vmInst.CreateNewVM(osVersion = self.local_vmname_win10x64 )
        rightclick(fsmainWindow, ttbl0,
                   self.local_vmname_win10x64)
        selectmenuitem(mnuContext, manageSharing)
        self.harness.VerifySafely(bool(waittillguiexist(shareWizard)),
                                  True, '%s show up.' % shareWizard)
        click(shareWizard, btnCancel)
        self.vmInst.CloseWorkstation()


class sharedVM15(General):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Sharing related context menu items'
                                        'for standard VM tab funtionality')
        self.vmInst.LaunchWorkstation()
        self.connectToServer(testdata)
        self.vmInst.CreateNewVM(osVersion = self.local_vmname_win10x64)
        singleclickrow(fsmainWindow, ttbl0,
                       self.local_vmname_win10x64)
        region = getobjectsize( fsmainWindow,
                                'btn'+ self.local_vmname_win10x64)
        sikuliRightClick(region, [region[0] + 5, region[1] + 5])
        selectmenuitem(mnuContext, manageSharing)
        self.harness.VerifySafely(bool(waittillguiexist(shareWizard)),
                                  True, '%s show up.' % shareWizard)
        click(shareWizard, btnCancel)
        self.vmInst.DeleteVM()
        self.vmInst.CloseWorkstation()


class sharedVM16(General):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Sharing related menu items for "'
                                        'standard VM functionality')
        self.vmInst.LaunchWorkstation()
        self.connectToServer(testdata)
        self.vmInst.CreateNewVM(osVersion = self.local_vmname_win10x64)
        status = bool(selectmenuitem(mainWindow, mnuToSharing))
        self.harness.VerifySafely(status, True,
                                  "Open share wizard successfully")
        self.harness.VerifySafely(bool(waittillguiexist(shareWizard)),
                                  True, '%s show up.' % shareWizard)
        click(shareWizard, btnClose)
        self.vmInst.DeleteVM()
        self.vmInst.CloseWorkstation()


class sharedVM17(General):
    def startTest(self, testdata):
        self.harness.SetTestDescription("Sharing VMs into new datastore")
        self.vmInst.LaunchWorkstation()
        testdata = getTestDataList(testdata)
        self.vmname = testdata['vmname']
        selectmenuitem(mainWindow, mnueditToPreferences)
        selectrow(prefWindow, VMSettingsTableName, sharedVms)
        newLocation = os.path.join(self.defaultSharedVMDir, "New Shared VM")
        os.mkdir(newLocation)
        settextvalue(prefWindow, SHARED_VM_LOCATION, newLocation)
        click(prefWindow, btnOK)

        self.vmInst.CreateNewVM( vmName=self.vmname)
        self.shareVMViaMenu()
        status = os.path.exists("%s/%s/%s.vmdk" % (newLocation, self.vmname,
                                                   self.vmname))
        self.harness.VerifySafely(status, True, "VM appeared in the new"
                                                      "shared VM location")
        singleclickrow(fsmainWindow, ttbl0, self.vmname)
        #wait(2)
        selectmenuitem(mainWindow, mnuStopSharing)
        click(stopSharingWizard, btnNext)
        click(stopSharingWizard, btnFinish)
        if waittillguiexist(stopSharingWizard):
            click(stopSharingWizard, btnClose)
        self.vmInst.DeleteVM(vmName=self.vmname)
        selectmenuitem(mainWindow, mnueditToPreferences)
        selectrow(prefWindow, VMSettingsTableName, sharedVms)
        settextvalue(prefWindow, SHARED_VM_LOCATION, self.defaultSharedVMDir)
        click(prefWindow, btnOK)
        self.vmInst.CloseWorkstation()



class sharedVM18(General):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Sharing VMs with supported HW '
                                        'versions')
        self.vmInst.LaunchWorkstation()
        testdata = getTestDataList(testdata)
        self.vmname = testdata['vmname']
        hwCompatList = ['Workstation 12.x',
                        'Workstation 11.x']
        for hwcompat in hwCompatList:
            self.vmInst.CreateCustomVM(vmName = self.vmname,
                                       hwCompatibility = hwcompat)
            self.shareVMViaMenu()
            status = bool(selectrowpartialmatch(fsmainWindow, ttbl0,
                                                self.vmname))
            self.harness.VerifySafely(status, True,
                                      'The Shared VM detected in UI')
            sharedVMPath = os.path.join(self.defaultSharedVMDir, self.vmname)
            if os.path.exists(sharedVMPath):
                status = True
            self.harness.VerifySafely(status, True, "The Shared VM exists in "
                                                    "custom path.")
            self.deleteSharedVM(self.vmname)
        self.vmInst.CloseWorkstation()


class sharedVM19(General):
    def startTest(self, testdata):
        self.harness.SetTestDescription("Sharing Wizard UI pages flow")
        self.vmInst.LaunchWorkstation()
        testdata = getTestDataList(testdata)
        self.vmname = testdata['vmname']
        self.vmInst.CreateCustomVM(osVersion = self.local_vmname_win10x64,
                                 vmName=self.vmname)
        selectmenuitem(mainWindow, mnuToSharing)
        click(shareWizard, btnNext)
        status = bool(objectexist(shareWizard, selectTransferVMtoShared))
        self.harness.VerifySafely(status, True, "transfer type description"
                                                "found on the page, thereofre"
                                                "reached the 'Select Transfer"
                                                "Type' page of the sharing "
                                                "wizard'" )
        click(shareWizard, btnFinish)
        status = bool(objectexist(shareWizard, lblDone))
        self.harness.VerifySafely(status, True, "label Done found on the"
                                                "page, so reached the last "
                                                "page of sharing wizard")
        click(shareWizard, btnClose)
        singleclickrow(fsmainWindow, ttbl0, self.vmname)
        # wait 2 seconds to access the ShareVM
        wait(2)
        self.deleteSharedVM(self.vmname)
        self.vmInst.CloseWorkstation()


class sharedVM20(General):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Sharing Wizard UI components')
        self.vmInst.LaunchWorkstation()
        testdata = getTestDataList(testdata)
        self.vmname = testdata['vmname']
        self.vmInst.CreateCustomVM(osVersion = self.local_vmname_win10x64,
                                                vmName = self.vmname)
        selectmenuitem(mainWindow, mnueditToPreferences)
        selectrow(prefWindow, VMSettingsTableName, sharedVms)
        wait(2)
        sharedVMPath = gettextvalue(prefWindow, SHARED_VM_LOCATION)
        click(prefWindow, btnCancel)
        selectmenuitem(mainWindow, mnuToSharing)
        # verify elements on the first page
        status = self.generalInst.VerifyState(shareWizard,
                                              lblWelcometotheShareVMWizard,
                                              'SHOWING')
        self.harness.VerifySafely(status, True, "Welcome to Share VM text "
                                                "showing on the welcome "
                                                "page")
        status = self.generalInst.VerifyState(shareWizard,
                                              shareVMWizardHelpText,
                                              'SHOWING')
        self.harness.VerifySafely(status, True, "Helper text showing on the "
                                                "share VM welcome page")
        status = bool(stateenabled(shareWizard, btnBack))
        self.harness.VerifySafely(status, False, "Back button disabled")
        buttonsEnabled = [btnNext, btnCancel]
        for button in buttonsEnabled:
            status = bool(stateenabled(shareWizard, button))
            self.harness.VerifySafely(status, True, '%s enabled' % button)
        # tabbing order
        shareWizardWelcomePageTabOrder = [btnNext, btnCancel]
        self.generalInst.VerifyTabIndex(shareWizard,
                                        shareWizardWelcomePageTabOrder)
        click(shareWizard, btnNext)
        # verify elements on the second page
        status = bool(gettextvalue(shareWizard,
                                   txtSharedVirtualMachineName) == self.vmname)
        self.harness.VerifySafely(status,
                                  True,
                                  "Default value set to %s" % self.vmname)
        status = bool(verifycheck(shareWizard, rbtnMovethevirtualmachine))
        self.harness.VerifySafely(status, True,
                                  "move the VM button selectedd")
        status = bool(verifyuncheck(shareWizard, MAKE_FULL_CLONE_RADIO_BUTTON))
        self.harness.VerifySafely(status, True, "make a clone of VM "
        "unselected")
        sharedVMPath = os.path.join(sharedVMPath, self.vmname)
        status = bool(gettextvalue(shareWizard,vmTransferredPath) ==
                      sharedVMPath)
        self.harness.VerifySafely(status,
                                  True,
                                  "Default path to %s" % sharedVMPath)
        shareWizardSelectTransferTabOrder = [txtSharedVirtualMachineName,
                                             rbtnMovethevirtualmachine,
                                             vmTransferredPath,
                                             btnBack,
                                             btnFinish,
                                             btnCancel]
        self.generalInst.VerifyTabIndex(shareWizard,
                                        shareWizardSelectTransferTabOrder)
        click(shareWizard, btnFinish)
        # verify the last page
        lblList = [lblClosingvirtualmachine, lblMovingvirtualmachine,
                   lblRegisteringvirtualmachine, lblDone]
        for item in lblList:
            status = bool(objectexist(shareWizard, item))
            self.harness.VerifySafely(status,
                                      True,
                                      "Last page of share VM wizard "
                                      "contains %s " % item)
        status = bool(hasstate(shareWizard, btnClose, state.FOCUSED))
        self.harness.VerifySafely(status, True, "button close is focused")
        click(shareWizard, btnClose)
        singleclickrow(fsmainWindow, ttbl0,self.vmname)
        wait(2)
        self.deleteSharedVM(self.vmname)
        self.vmInst.CloseWorkstation()


class sharedVM21(General):
    def startTest(self, testdata):
        self.harness.SetTestDescription("Standard VM sharing flow")
        self.vmInst.LaunchWorkstation()
        testdata = getTestDataList(testdata)
        self.vmname = testdata['vmname']
        self.vmInst.CreateCustomVM(osVersion = self.local_vmname_win10x64,
                                   vmName = self.vmname)
        self.shareVMViaMenu()
        status = bool(selectrowpartialmatch(fsmainWindow, ttbl0, self.vmname))
        self.harness.VerifySafely(status,
                                  True,
                                  'Newly shared VM shows up under the'
                                  "Shared VMs folder")
        sharedvmpath = self.hostInst.getSharedVMPath(
            xmlfile='C:\\ProgramData\\VMware'
                    '\\hostd\\vmInventory.xml',
            xmltag='vmxCfgPath')
        status = os.path.exists(sharedvmpath)
        self.harness.VerifySafely(status,
                                  True,
                                  "VMX file existed at %s,therefore shared"
                                  " VM created successfully" % sharedvmpath)
        self.deleteSharedVM(self.vmname)
        self.vmInst.CloseWorkstation()


class sharedVM22(General):
    def startTest(self, testdata):
        self.harness.SetTestDescription("Unsharing context menu items for "
                                        "VM tab functionality")
        self.vmInst.LaunchWorkstation()
        testdata = getTestDataList(testdata)
        self.vmname = testdata['vmname']
        self.vmInst.CreateCustomVM(osVersion = self.local_vmname_win10x64,
                                                vmName = self.vmname)
        self.shareVMViaMenu()
        singleclickrow(fsmainWindow, ttbl0, self.vmname)
        region = getobjectsize(fsmainWindow,
                               'btn' + self.vmname + '*')
        sikuliRightClick(region, [region[0] + 10, region[1] + 10])
        selectmenuitem(mnuContext, manageStopSharing)
        status = bool(waittillguiexist(stopSharingWizard))
        self.harness.VerifySafely(status,
                                  True,
                                  "%s shows up" % stopSharingWizard)
        click(stopSharingWizard, btnCancel)
        sikuliRightClick(region, [region[0] + 10, region[1] + 10])
        selectmenuitem(mnuContext, managePermissions)
        status = bool(waittillguiexist(permissionsWindow))
        self.harness.VerifySafely(status,
                                  True,
                                  "%s shows up" % permissionsWindow)
        click(permissionsWindow, btnCancel)
        self.deleteSharedVM(self.vmname)
        self.vmInst.CloseWorkstation()


class sharedVM23(General):
    def startTest(self, testdata):
        self.harness.SetTestDescription("Unsharing context menu items "
                                        "functionality")
        self.vmInst.LaunchWorkstation()
        testdata = getTestDataList(testdata)
        self.vmname = testdata['vmname']
        self.vmInst.CreateNewVM(osVersion=self.local_vmname_win10x64,
                                vmName=self.vmname )
        self.shareVMViaMenu()
        singleclickrow(fsmainWindow, ttbl0, self.vmname )
        wait(2)
        rightclick(fsmainWindow, ttbl0, self.vmname )
        selectmenuitem(mnuContext, manageStopSharing)
        status = bool(waittillguiexist(stopSharingWizard))
        self.harness.VerifySafely(status,
                                  True,
                                  "%s shows up" % stopSharingWizard)
        click(stopSharingWizard, btnCancel)
        rightclick(fsmainWindow, ttbl0, self.vmname )
        selectmenuitem(mnuContext, managePermissions)
        status = bool(waittillguiexist('Permissions'))#
        self.harness.VerifySafely(status,
                                  True,
                                  "%s shows up" % 'Permissions')
        click('Permissions', btnCancel)
        self.deleteSharedVM(self.vmname)
        self.vmInst.CloseWorkstation()


class sharedVM24(General):
    def startTest(self, testdata):
        self.harness.SetTestDescription("Unsharing menu items functionality")
        self.vmInst.LaunchWorkstation()
        testdata = getTestDataList(testdata)
        self.vmname = testdata['vmname']
        self.vmInst.CreateCustomVM(osVersion=self.local_vmname_win10x64,
                                   vmName=self.vmname)
        self.shareVMViaMenu()
        # has to wait for the sharedVM to be accessible
        wait(2)
        status = bool(selectmenuitem(mainWindow, mnuStopSharing))
        self.harness.VerifySafely(status, True,
                                  "successfully selected stop sharing "
                                  "wizard")
        status = bool(waittillguiexist(stopSharingWizard))
        self.harness.VerifySafely(status,
                                  True,
                                  "%s shows up" % stopSharingWizard)
        click(stopSharingWizard, btnCancel)
        status = bool(selectmenuitem(mainWindow, mnuToPermissions))
        self.harness.VerifySafely(status,
                                  True,
                                  "successfully selected permissions "
                                  "wizard" )
        status = bool(waittillguiexist('Permissions'))
        self.harness.VerifySafely(status,
                                  True,
                                  "%s shows up" % 'Permissions')
        click('Permissions', btnCancel)
        self.deleteSharedVM(self.vmname)
        self.vmInst.CloseWorkstation()


class sharedVM25(General):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Unsharing Wizard pages flow')
        self.vmInst.LaunchWorkstation()
        testdata = getTestDataList(testdata)
        self.vmname = testdata['vmname']
        self.vmInst.CreateCustomVM(osVersion = self.local_vmname_win10x64,
                                 vmName=self.vmname)
        self.shareVMViaMenu()
        wait(2)
        selectmenuitem(mainWindow, mnuStopSharing)
        status = bool(objectexist(stopSharingWizard,
                                  'lblWelcometotheStopSharingVMWizard'))
        self.harness.VerifySafely(status, True, "the welcome page can be "
                                                "found on the stop sharing"
                                                "wizard. therefore reached"
                                                "the first page of stop "
                                                "sharing Vm Wizard")
        click(stopSharingWizard, btnNext)
        status = bool(objectexist(stopSharingWizard,
                                  lblSelectthelocationofthestandardVM))
        self.harness.VerifySafely(status, True, "Select location the VM "
                                                "need to be moved out of"
                                                "on the second page")
        click(stopSharingWizard, btnBrowse)
        self.harness.VerifySafely(
            bool(waittillguiexist(dlgBrowseforfolder)),
            True,
            "'Browse For Folder' invoked by Browse button, which exists"
            "on the second page of stop sharing VM  ")
        click(dlgBrowseforfolder, btnCancel)
        click(stopSharingWizard, btnFinish)
        waittillguiexist
        labels = [lblUnregisteringvirtualmachine, lblClosingvirtualmachine,
                  lblMovingvirtualmachine, lblDone]
        if bool(waittillguiexist(stopSharingWizard)):
            for label in labels:
                status = bool(objectexist(stopSharingWizard, label))
                self.harness.VerifySafely(status, True, '%s exits on the last '
                                                    'page of Stop Sharing '
                                                        'VM wizard' % label)
        click(stopSharingWizard, btnClose)
        wait(2)
        #self.deleteSharedVM(self.vmname)
        self.vmInst.DeleteVM()
        status = os.path.exists('%s/%s/%s.vmx' % (self.defaultSharedVMDir,
                                                  self.vmname,
                                                  self.vmname))
        self.harness.VerifySafely(status, False,
                                  "VM is deleted successfully from the "
                                  "shared vm folder")
        self.vmInst.CloseWorkstation()


class sharedVM26(General):
    def startTest(self, testdata):
        self.harness.SetTestDescription('Shared VMs access from another WS'
                                        'instance on the same host')
        serverName = socket.gethostbyname(socket.gethostname())
        self.vmInst.LaunchWorkstation()
        testdata = getTestDataList(testdata)
        self.vmname = testdata['vmname']
        self.host = testdata['host']
        self.vmInst.CreateNewVM(vmName=self.vmname)
        self.shareVMViaMenu()
        self.vmInst.LaunchWorkstation()
        serverName = socket.gethostbyname(socket.gethostname())
        # connect to lab environment, jenkins
        self.hostInst.Connect(host = testdata['host'],
                            user = testdata['user'],
                            pwd = testdata['pwd'],
                            gui = True)
        # appended a '1' to the shared vm displayed for the local host server
        status = bool(selectrowpartialmatch(fsmainWindow, ttbl0,
                                            self.vmname +'1'))
        self.harness.VerifySafely(status, True, 'VM  shared successfully')

        rightclick(fsmainWindow, ttbl0, self.host)
        selectmenuitem(mnuContext, mnuDisconnect)
        wait(3)
        self.deleteSharedVM(self.vmname)
        # remove the server
        rightclick('*VMware Workstation*', 'ttbl0', '10.117.173.80')
        selectmenuitem('mnuContext', mnuRemove)
        click(fsmainWindow, btnRemove)
        self.vmInst.CloseWorkstation()
        self.vmInst.CloseWorkstation()