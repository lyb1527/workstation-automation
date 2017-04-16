import re
import sys
from shutil import copyfile
from ldtp import *
from vm import *
from objname import *
from commonutils import *
from settings import Settings
from generalactions import GeneralActions

class GeneralSetup(object):

    def __init__(self, harness):
        self.harness = harness
        self.vmInst = VM(self.harness)
        self.settingInstance = Settings(self.harness)
        self.generalInst = GeneralActions(self.harness)

    def preparePath(self, testdata):
        self.testData = getTestDataList(testdata)
        isoPath = self.testData['isopath']
        self.isoFullPath = os.path.join(self.harness.testInfo['isodrive'], isoPath)

    def endTest(self):
        self.harness.UpdateTestcaseResult()

class test1(GeneralSetup):

   def startTest(self, testdata):
      self.harness.SetTestDescription(
         'Enable AutoProtect and verify the state '
         'of components on the AutoProtect setting page')
      self.preparePath(testdata)
      self.vmInst.LaunchWorkstation()
      selectmenuitem(mainWindow, mnuToCreateaNewVirtualMachine)
      status = bool(waittillguiexist(dlgNewVirtualMachineWizard))
      self.harness.VerifySafely(status, True, 'New VM wizard opens up')
      check(dlgNewVirtualMachineWizard, newTypical)
      click(dlgNewVirtualMachineWizard, btnNext)
      self.harness.AddTestComment("input ISO path for the iso image ")
      click(dlgNewVirtualMachineWizard, rbtnInstallerdiscimagefile)
      status = bool(settextvalue(dlgNewVirtualMachineWizard, txt0, self.isoFullPath))
      self.harness.VerifySafely(status, True, 'successfully set the iso path')
      osVersionLabel = bool(waittillguiexist(dlgNewVirtualMachineWizard,
                                             LABEL_DETECTED))
      self.harness.VerifySafely(osVersionLabel, True, '%s detected'
                                % osVersionLabel)
      easyInstallLabel = bool(waittillguiexist(dlgNewVirtualMachineWizard,
                              lblThisoperatingsystemwilluseEasyInstall))
      self.harness.VerifySafely(easyInstallLabel, True, "Easy install label"
                                                        "detected")
      click(dlgNewVirtualMachineWizard, btnCancel)
      self.vmInst.CloseWorkstation()


class test2(GeneralSetup):

   def startTest(self, testdata):
      self.harness.SetTestDescription('Verify if all information provided, '
                                      'Easy Install could install without'
                                      ' intervention')
      self.preparePath(testdata)
      self.vmInst.LaunchWorkstation()
      self.harness.AddTestComment("Launch New VM Wizard and click Next")
      selectmenuitem(mainWindow, mnuToCreateaNewVirtualMachine)
      status = bool(waittillguiexist(dlgNewVirtualMachineWizard))
      self.harness.VerifySafely(status, True, 'New Virtual Machine Wizard'
                                              'is launched')
      check(dlgNewVirtualMachineWizard, newTypical)
      click(dlgNewVirtualMachineWizard, btnNext)
      status = bool(waittillguiexist(dlgNewVirtualMachineWizard,
                                     LABEL_LIKE_PHYSICAL_COMPUTER))
      self.harness.VerifySafely(status, True, 'Easy install inofrmation '
                                              'page is displayed')
      self.harness.AddTestComment("Select iso image and click Next")
      click(dlgNewVirtualMachineWizard, rbtnInstallerdiscimagefile)
      settextvalue(dlgNewVirtualMachineWizard, txt0, self.isoFullPath)
      ret1 = waittillguiexist(dlgNewVirtualMachineWizard, LABEL_DETECTED)
      ret2 = waittillguiexist(dlgNewVirtualMachineWizard,
                              lblThisoperatingsystemwilluseEasyInstall)
      self.harness.VerifyFatal(bool(ret1) and bool(ret2), True,
                               "OS should be detected and will use easy "
                               "install")
      click(dlgNewVirtualMachineWizard, btnNext)
      waittillguiexist(dlgNewVirtualMachineWizard,
                       LABEL_EASY_INSTALL_INFORMATION)
      passwd = self.testData['password']
      passwdConfirm = self.testData['confirmpassword']
      username = self.testData['username']
      settextvalue(dlgNewVirtualMachineWizard, txtFullname, username)
      settextvalue(dlgNewVirtualMachineWizard, txtPassword, passwd)
      settextvalue(dlgNewVirtualMachineWizard, txtConfirmRestriction,
                   passwdConfirm)

      status = bool(objectexist(dlgNewVirtualMachineWizard, chkAutologon))
      self.harness.VerifySafely(status, True, 'Checkbox autologon exists on'
                                              'the Easy Install Information '
                                              'page')
      status = bool(check(dlgNewVirtualMachineWizard, chkAutologon))
      self.harness.VerifySafely(status, True, "check autologon box")
      click(dlgNewVirtualMachineWizard, btnNext)
      click(dlgNewVirtualMachineWizard, btnNext)
      click(dlgNewVirtualMachineWizard, btnNext)
      click(dlgNewVirtualMachineWizard, btnFinish)
      VMToolsInstalled = False
      while not VMToolsInstalled:
          wait(30)
          if EasyInstallInstallingVMwareTools in \
            getobjectlist('*VMware Workstation*'):
              VMToolsInstalled = True
              self.harness.VerifySafely(VMToolsInstalled,
                                        True,
                                        'VM tools installed on theguest')
      self.vmInst.PowerOffVM()
      self.vmInst.DeleteVM()
      self.vmInst.CloseWorkstation()

