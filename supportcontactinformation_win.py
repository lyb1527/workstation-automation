import os.path
import sys
import re
import commands
import wsconfigparser
from ldtp import *
from objname import *
from vm import *
from commonutils import *
from generalactions import *
from settings import Settings


class test1:
   def __init__(self, harness):
      self.harness = harness

   def startTest(self, testdata):
      self.harness.SetTestDescription(
          "The configured URL can be displayed"
          " in Get_Support menu for Workstation")
      vmInst = VM(self.harness)
      configPath = 'C:\ProgramData\VMware\VMware Workstation\config.ini'
      self.harness.AddTestComment("Add support URL in config file")
      url = "http://www.baidu.com"
      with open(configPath, 'a') as f:
          f.write('\ninstallerDefaults.SupportURL = "%s"' % url)
          f.close()
      self.harness.AddTestComment("Launch Workstation")
      vmInst.LaunchWorkstation()
      status = bool(menuitemenabled(
          mainWindow,'%s;%s;%s' % (mnuHelp,mnuSupport,
                                   'mnuProductSupportCenter')))
      self.harness.VerifySafely(status, False,
                                "Product Support Center' is not available.")
      status = bool(menuitemenabled(
          mainWindow, '%s;%s;%s' %
                      (mnuHelp,mnuSupport, 'mnuSubmitSupportRequest')))
      self.harness.VerifySafely(
          status, False," 'Submit Support Request' is not available.")
      status = bool(menuitemenabled(
          mainWindow, '%s;%s;%s' % (mnuHelp,mnuSupport,'mnuGetSupport')))
      self.harness.VerifySafely(
          status, True, "Menu 'GetSupport' is available.")
      selectmenuitem(mainWindow,'%s;%s;%s' %
                     (mnuHelp,mnuSupport,'mnuGetSupport'))
      baiduWindow = u'frm\u767e\u5ea6\u4e00\u4e0b\uff0c\u4f60\u5c31\u77e5\u9053*'
      status = bool(waittillguiexist())
      self.harness.VerifySafely(status, True, "The browser launched "
                                              "to the correct URL")
      self.harness.AddTestComment("Close Workstation")
      vmInst.CloseWorkstation()
      closewindow(baiduWindow)

   def endTest(self):
      self.harness.UpdateTestcaseResult()