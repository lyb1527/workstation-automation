import os
import glob
import os.path
import traceback
from ldtp import *
from vm import VM
from objname import *
from commonutils import *
from snapshot import Snapshot
from settings import Settings
from generalactions import GeneralActions

class General(object):
   def __init__(self, harness):
      self.harness = harness
      self.vmInst = VM(self.harness)
      self.settingsInst = Settings(self.harness)
      self.snapshot = Snapshot(self.harness)
      self.generalInst = GeneralActions(self.harness)

   def endTest(self):
      self.harness.UpdateTestcaseResult()

   def startRecovery(self):
      self.generalInst.DeleteTestVMDir()


class test1(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription('MultiSnapshotUI')
      self.vmInst.LaunchWorkstation()
      self.vmInst.CreateNewVM()
      self.vmInst.PowerOnVM()
      self.vmInst.PowerOffVM()
      self.snapshot.TakeSnapshot('Snapshot1', 'Snapshot1')
      self.snapshot.SnapshotExist('Snapshot1')
      self.vmInst.PowerOnVM()
      self.snapshot.TakeSnapshot('Snapshot2', 'Snapshot2')
      self.snapshot.SnapshotExist('Snapshot2')
      self.vmInst.PowerOffVM()
      self.vmInst.PowerOnVM()
      self.snapshot.GoToSnapshot('Snapshot1')
      self.vmInst.PowerOnVM()
      self.vmInst.PowerOffVM()
      self.snapshot.GoToSnapshot('Snapshot2')
      self.vmInst.DeleteVM()
      self.vmInst.CloseWorkstation()


class test2(General):
   def startTest(self, testdata):
      self.harness.SetTestDescription("MultiSnapshotUI.Menu - Functionality")
      self.harness.AddTestComment("Launch Workstation")
      self.testdatadict = getTestDataList(testdata)
      self.vmInst.LaunchWorkstation()
      self.vmInst.CreateNewVM(vmName=self.testdatadict['vmname'])
      self.harness.AddTestComment("create Snapshot1")
      self.snapshot.TakeSnapshot('Snapshot1', 'Snapshot1')
      self.harness.AddTestComment("create snapshot2")
      self.snapshot.TakeSnapshot('snapshot2', 'snapshot2')
      self.harness.AddTestComment("revert to Snapshot1")
      self.snapshot.GoToSnapshot('Snapshot1')
      self.harness.AddTestComment("Verify snapshot manager is opened"
                                  " with menu")
      selectmenuitem(mainWindow, mnuToSnapshotManager)
      status = bool(waittillguiexist(snapshotManager))
      self.harness.VerifySafely(status, True, 'Snapshot manager opened with '
                                              'menu click')
      click(snapshotManager, btnClose)
      self.harness.AddTestComment('verify most recently used snapshots')
      self.snapshot.SnapshotExist('Snapshot1')
      self.snapshot.SnapshotExist('Snapshot2')
      self.harness.AddTestComment("Delete VM")
      self.vmInst.DeleteVM()
      self.harness.AddTestComment("Close Workstation")
      self.vmInst.CloseWorkstation()