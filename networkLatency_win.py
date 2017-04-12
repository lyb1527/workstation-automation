import re
import subprocess
from ldtp import *
from vm import *
from objname import *
from generalactions import GeneralActions
from settings import Settings
from snapshot import Snapshot
from commonutils import *

class GeneralSetup():
    def __init__(self, harness):
        self.harness = harness
        self.vmInstance = VM(self.harness)
        self.generalInstance = GeneralActions(self.harness)
        self.settingsInstance = Settings(self.harness)

    def startRecovery(self):
      vmInst = VM(self.harness)
      vmGeneral = GeneralActions(self.harness)
      self.harness.VerifySafely(vmInst.VerifyPowerOffVM(), True,"Power Off VM")
      self.harness.VerifySafely(vmInst.VerifyDeleteVM(), True, "Delete VM")
      self.harness.VerifySafely(
          vmInst.VerifyCloseWorkstation(), True, "Close workstation")
      vmGeneral.DeleteTestVMDir()

    def endTest(self):
        self.harness.AddTestComment("Delete VM")
        self.vmInstance.DeleteVM()
        self.harness.AddTestComment("Close VMware Workstation")
        self.vmInstance.CloseWorkstation()
        self.generalInstance.DeleteTestVMDir()
        self.harness.UpdateTestcaseResult()


class test1(GeneralSetup):
    def startTest(self, testdata):
        self.vmInstance.LaunchWorkstation()
        self.harness.SetTestDescription(
            "Default latency setting is disabled")
        self.harness.AddTestComment("Create a new VM")
        self.testdata = getTestDataList(testdata)
        self.vmInstance.CreateNewVM(vmName=self.testdata['vmname'])
        self.harness.AddTestComment("Launch VM Settings Dialog")
        self.settingsInstance.OpenAdvancedNet()

        # verify default values for latency inputs
        latencies = ['txtLatency(ms)', 'txtLatency(ms)1']
        for latency in latencies:
            status = bool(
                gettextvalue(frmNetworkAdapterAdvancedSettings,latency) == '0')
            self.harness.VerifySafely(status, True, " %s is 0" % latency)
        self.settingsInstance.CloseAdvancedNet()

        # incoming  and outgoing transfer latency check
        keys = ['ethernet0.rxlatency.latency','ethernet0.txlatency.latency']
        for key in keys:
            status = bool(self.vmInstance.GetVMXValue(
                self.vmInstance.testvmDir,
                self.testdata['vmname'],'%s.vmx'%self.testdata['vmname'],
                key))
            self.harness.VerifySafely(
                status, False, 'No %s configuration' % key)



class test2(GeneralSetup):
    def startTest(self, testdata):
        self.vmInstance.LaunchWorkstation()
        self.harness.SetTestDescription(
            "Verify that UI related function works well")
        self.harness.AddTestComment("Create a new VM")
        self.testdata = getTestDataList(testdata)
        self.vmInstance.CreateNewVM(vmName=self.testdata['vmname'])
        self.harness.AddTestComment("Launch VM Settings Dialog")

        # check latency input up and down button
        latencyList = ['txtLatency(ms)', 'txtLatency(ms)1']
        keyList = ['ethernet0.rxlatency.latency',
                   'ethernet0.txlatency.latency']
        for key, latency in zip(keyList, latencyList):
            self.settingsInstance.OpenAdvancedNet()
            self.generalInstance.SendKeyboardInput(
                '<UP>', frmNetworkAdapterAdvancedSettings, latency)
            self.settingsInstance.CloseAdvancedNet()
            self.vmInstance.VerifyVMXValue('1', key, testdata=self.testdata)
            self.settingsInstance.OpenAdvancedNet()
            status = bool(gettextvalue(
                frmNetworkAdapterAdvancedSettings, latency) == "1")
            self.harness.VerifySafely(
                status, True, " UP button increments the value by one ")
            self.generalInstance.SendKeyboardInput(
                '<DOWN>', frmNetworkAdapterAdvancedSettings, latency)
            self.settingsInstance.CloseAdvancedNet()
            self.vmInstance.VerifyVMXValue('-1', key, testdata=self.testdata)
            self.settingsInstance.OpenAdvancedNet()
            status = bool(gettextvalue(
                frmNetworkAdapterAdvancedSettings, latency) == "0")
            self.harness.VerifySafely(
                status, True, " DOWN button increments the value by one ")
            self.settingsInstance.CloseAdvancedNet()

        # check latency input selected by Tab order
        self.settingsInstance.OpenAdvancedNet()
        itemList = [btnGenerate, btnOK, btnCancel, btnHelp, cboBandwidth,
                    txtKbps, txtPacketLoss, 'txtLatency(ms)', cboBandwidth1,
                    txtKbps1, txtPacketLoss1, 'txtLatency(ms)1', txtMACAddress
                    ]
        status = self.generalInstance.VerifyTabIndex(
            frmNetworkAdapterAdvancedSettings, itemList)
        self.harness.VerifySafely(
            status, True, 'Both input can be selected by Tab order')

        # input 100 for incoming latency
        for key, latency in zip(keyList, latencyList):
            settextvalue(
                frmNetworkAdapterAdvancedSettings, latency, '100')
            self.settingsInstance.CloseAdvancedNet()
            self.vmInstance.VerifyVMXValue('100', key, testdata=self.testdata)
            self.settingsInstance.OpenAdvancedNet()
            status = bool(gettextvalue(
                frmNetworkAdapterAdvancedSettings, latency) == "100")
            self.harness.VerifySafely(
                status, True, "%s 100 is accepted" % latency)
        self.settingsInstance.CloseAdvancedNet()
