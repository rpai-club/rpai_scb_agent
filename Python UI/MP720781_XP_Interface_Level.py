#
# Hardware specific interface functions
# For Multicomp Pre MP720781 Scope Meter (6-2-2025)
# Written using Python version 3.10, Windows OS 
#
try:
    import serial
    import serial.tools.list_ports
except:
    root.update()
    showwarning("WARNING","Serial Library not installed?!")
    root.destroy()
    exit()
try:
    import usb.core
    import usb.util
    import usb.control
    from usb.backend import libusb0, libusb1, openusb # , IBackend
    be0, be1 = libusb0.get_backend(), libusb1.get_backend()
    be3 = openusb.get_backend()
except:
    root.update()
    showwarning("WARNING","Pyusb not installed?!")
    root.destroy()
    exit()
#
ConfigFileName = "alice-last-config.cfg"
Tdiv.set(12)
ZeroGrid.set(6)
TimeDiv = 0.0002
import yaml
#
# adjust for your specific hardware by changing these values
DevID = "MP72"
TimeSpan = 0.001
CHANNELS = 2 # Number of supported Analog input channels
AWGChannels = 1 # Number of supported Analog output channels
PWMChannels = 0 # Number of supported PWM output channels
DigChannels = 0 # Number of supported Dig channels
LogicChannels = 0 # Number of supported Logic Analyzer channels
EnablePGAGain = 0 # 1
EnableOhmMeter = 0
EnableDmmMeter = 0
EnableDigIO = 0
UseSoftwareTrigger = 0
AllowFlashFirmware = 0
SMPfft = 4 * 300 # Set FFT size based on fixed acquisition record length
InterpRate = 4
MatrixStatus = IntVar()
MatrixStatus.set(0)
AWGBuffLen = 1024
AWGPeakToPeak = 4.095 # Iternal reference voltage for MCP4822
AWGRes = 4095 # For 8 bits, 4095 for 12 bits, 1023 for 10 bits
ATmin = 8 # set minimum DAC update rate to 8 uSec
MaxAWGSampleRate = 1.0 / (ATmin / 1000000) # set to 1 / 8 uSec
AWGSampleRate = MaxAWGSampleRate
XpID = "Pi Pico Cross Point Mini"
SerComPort = 'Auto'
#
# Breadboard pin maping for Mimi Red 1 layout
#
TL1 = "CA0"; TL2 = "CA1"; TL3 = "CA2"; TL4 = "CA3"; TL5 = "CA4"; TL6 = "CA5"; TL7 = "CA12"; TL8 = "CA13"
BL1 = "CA14"; BL2 = "CA15"; BL3 = "CA6"; BL4 = "CA7"; BL5 = "CA8"; BL6 = "CA9"; BL7 = "CA10"; BL8 = "CA11"
TL9 = "CB0"; TL10 = "CB1"; TL11 = "CB2"; TL12 = "CB3"; TL13 = "CB4"; TL14 = "CB5"; TL15 = "CB12"; TL16 = "CB13"
BL9 = "CB14"; BL10 = "CB15"; BL11 = "CB6"; BL12 = "CB7"; BL13 = "CB8"; BL14 = "CB9"; BL15 = "CB10"; BL16 = "CB11"
BL17 = "CE2"; TL17 = "CE0"; TR1 = "CE1"

TR2 = "CC0"; TR3 = "CC1"; TR4 = "CC2"; TR5 = "CC3"; TR6 = "CC4"; TR7 = "CC5"; TR8 = "CC12"; TR9 = "CC13"
BR1 = "CC14"; BR2 = "CC15"; BR3 = "CC6"; BR4 = "CC7"; BR5 = "CC8"; BR6 = "CC9"; BR7 = "CC10"; BR8 = "CC11"
TR10 = "CD0"; TR11 = "CD1"; TR12 = "CD2"; TR13 = "CD3"; TR14 = "CD4"; TR15 = "CD5"; TR16 = "CD12"; TR17 = "CD13"
BR9 = "CD14"; BR10 = "CD15"; BR11 = "CD6"; BR12 = "CD7"; BR13 = "CD8"; BR14 = "CD9"; BR15 = "CD10"; BR16 = "CD11"

AINH = "CE14"; BINH = "CE15"; CINH = "CE6"
AWG1 = "CE7"; AWG2 = "CE8"
JP5 = "CE3"; JP6 = "CE9"; JP7 = "CE10"; JP8 = "CE11"
JP9 = "CE4"; JP10 = "CE5"; JP11 = "CE12"; JP12 = "CE31"

JumperSpinBoxList = ("JP1", "JP2", "JP3", "JP4", "JP5", "JP6", "JP7", "JP8",
                     "JP9", "JP10", "JP11", "JP12", "JP13", "JP14", "J1P5", "JP16")
CompSpinBoxList = ("AWG1", "AWG2", "AINH", "BINH", "CINH")
#
# Cross point matrix functions
#
def ReadNetlist(nfp):
    if ".cir" in nfp:
        # Use weird LTspice .cir file encodeing !? two bytes per character...
        NetList = open(nfp, 'r', encoding='utf-16-le')
    else:
        # Use normal LTspice .net file encodeing one bytes per character...
        NetList = open(nfp, 'r', encoding='utf-8')
    lines = NetList.readlines()
    NetList.close()
    #print(lines)
    # create a list of strings for all subcircuit istance lines in netlist, ignore rest
    netlist_stripped = []
    for line in lines:
        # Select only the lines that start with XX
        # print(line)
        # line = line.encode('ascii')
        # if line[0:2] == 'XX':
        # if "TL" in line[0:4] or "BL" in line[0:4] or "TR" in line[0:4] or "BR" in line[0:4]:
        if "cross_point" in line:
            netlist_stripped.append(line.split())
    return netlist_stripped
#
def WhichChip(CompPin): # determine which cross point chip is used A-H

    ChipNum = 0
    # print("Which Chip ", CompPin)
    if isinstance(CompPin, int):
        return 0
    else:
        if "CA" in CompPin:
            ChipNum = 1
        if "CB" in CompPin:
            ChipNum = 2
        if "CC" in CompPin:
            ChipNum = 3
        if "CD" in CompPin:
            ChipNum = 4
        if "CE" in CompPin:
            ChipNum = 5
        return ChipNum
##
def ConfigCrossPoint():
    global ser, FileString, NumConn, ErrConn
    
    netlist = FileString.get()
    ComponentList = ReadNetlist(netlist) # list of all subcircuit instances found
    CompNum = len(ComponentList) # number of subcircuits
    index = 0
    connects = 0
    Errors = 0
    ErrorString = ""
    ser.write(b'x\n') # Reset all cross point switches to open
    time.sleep(0.01)
    while index < CompNum:
        CompPins = ComponentList[index]
        index = index + 1
        if "JP" in CompPins[1]:
            Jumper = CompPins[1] # First net is Jumper bus
            JmpNum = int(Jumper.replace("JP","")) - 1 # extract number 0-15
            try:
                XPin = eval(CompPins[2]) # is Second net a component BB pin
                xpin = CompPins[2]
                xpin = xpin.replace("X","")
            except:
                # for case where synbol instance name is the BB pin 
                xpin = CompPins[0]
                xpin = xpin.replace("X","")
                XPin = eval(xpin)
            #
            if XPin == 0: # cross point connected to node 0?
                xpin = CompPins[0]
                xpin = xpin.replace("X","")
                XPin = eval(xpin)
                # print(XPin,xpin)
            if "L" in xpin:
                if xpin != "TL17":
                    if JmpNum > 7:
                        ErrorString = "Jumper out of range in " + str(CompPins)
                        print(ErrorString)
                        Errors = Errors + 1
                        continue
                else: # BB pin TL17 can connect to any of JP1-4 and JP13-16
                    if JmpNum > 3 and JmpNum < 12:
                        ErrorString = "Jumper out of range in " + str(CompPins)
                        print(ErrorString)
                        Errors = Errors + 1
                        continue
                    if JmpNum > 7:
                        JmpNum = JmpNum - 8
                    # print(xpin, XPin, JmpNum)
            elif "R" in xpin:
                if xpin != "TR1":
                    if JmpNum < 7 or JmpNum > 15:
                        ErrorString = "Jumper out of range in " + str(CompPins)
                        print(ErrorString)
                        Errors = Errors + 1
                        continue
                    JmpNum = JmpNum - 8
                else: # BB pin TR1 can connect to any of JP1-4 and JP13-16
                    if JmpNum > 3 and JmpNum < 12:
                        ErrorString = "Jumper out of range in " + str(CompPins)
                        print(ErrorString)
                        Errors = Errors + 1
                        continue
                    if JmpNum > 7:
                        JmpNum = JmpNum - 8
            #
            ChipNum = WhichChip(XPin) # Find which switch chip 1-5
            if ChipNum == 5 and JmpNum > 7:
                JmpNum = JmpNum - 8
            if ChipNum > 0:
                CmpNum = only_numerics(XPin) # extract number 0-15
                CommStr = ("X " + str(JmpNum) + " " + str(CmpNum) + " " + str(ChipNum) + " 1")
                # print(CommStr)
                SendStr = CommStr + '\n'
                SendByt = SendStr.encode('utf-8')
                ser.write(SendByt)
                connects = connects + 1
            else:
                ErrorString = "Error Unknown switch chip number for? " + str(xpin)
                print(ErrorString)
                # print(CompPins)
                # print(XPin,xpin)
                Errors = Errors + 1
    NumConn.config(text = "Number of connections = " + str(connects) + " Errors = " + str(Errors))
    if Errors > 0:
        ErrConn.config(text = ErrorString )
    #print("Number of connections ", connects)
##
def ResetMatrix():
    global ser
    
    ser.write(b'x\n') # Reset all cross point switches to open
##
def BrowsNetFile():
    global FileString, NetList
    
    NetList = askopenfilename(defaultextension = ".cir", filetypes=[("Net List files", ".cir .net")])
    FileString.delete(0,"end")
    FileString.insert(0,NetList)
##
def ManualReturn(event):

    ManualMartix()
##
def ManualMartix():
    global ser, CompString, JumperString, OnOffString, NumConn

    Errors = 0
    Jumper = JumperString.get()
    JmpNum = int(Jumper.replace("JP","")) - 1 # extract number 0-15
    CompPin = CompString.get()
    if "JP" in Jumper:
        if "L" in CompPin:
            if CompPin != "TL17":
                if JmpNum > 7:
                    print("Jumper out of range in " , CompPin)
                    Errors = Errors + 1
            else: # BB pin TL17 can connect to any of JP1-4 and JP13-16
                if JmpNum > 3 and JmpNum < 12:
                    print("Jumper out of range in " , CompPin)
                    Errors = Errors + 1
                if JmpNum > 7:
                    JmpNum = JmpNum - 8
                # print(xpin, XPin, JmpNum)
        elif "R" in CompPin:
            if CompPin != "TR1":
                if JmpNum < 7 or JmpNum > 15:
                    print("Jumper out of range in " , CompPins)
                    Errors = Errors + 1
                JmpNum = JmpNum - 8
            else: # BB pin TR1 can connect to any of JP1-4 and JP13-16
                if JmpNum > 3 and JmpNum < 12:
                    print("Jumper out of range in " , CompPins)
                    Errors = Errors + 1
                if JmpNum > 7:
                    JmpNum = JmpNum - 8
        #
    #print(Jumper, CompPin)
    if Errors > 0:
        NumConn.config(text = "Error: Jumper out of range! " + str(CompPin) + " " + str(Jumper))
        return
    Xpin = eval(CompPin)
    # print(Xpin, CompPin)
    OnOff = int(OnOffString.get())
    ChipNum = WhichChip(Xpin) # Second net is Component pin
    if ChipNum == 5 and JmpNum > 7:
        JmpNum = JmpNum - 8
    if ChipNum > 0:
        CmpNum = only_numerics(Xpin) # extract number 0-7
        CommStr = ("X " + str(JmpNum) + " " + str(CmpNum) + " " + str(ChipNum) + " " + str(OnOff))
        # print(CommStr)
        SendStr = CommStr + '\n'
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
##
def MakeMatrixScreen():
    global matrixwindow, MatrixStatus, FileString, NumConn, RevDate, SWRev
    global CompString, JumperString, OnOffString, cpcl1, jpcl1
    global FrameBG, BorderSize, ErrConn
    global DCSr1String, DCSr2String, JumperSpinBoxList, CompSpinBoxList
    
    if MatrixStatus.get() == 0:
        MatrixStatus.set(1)
        #
        matrixwindow = Toplevel()
        matrixwindow.title("Cross Point Interface " + SWRev + RevDate)
        matrixwindow.resizable(FALSE,FALSE)
        matrixwindow.geometry('+0+300')
        matrixwindow.configure(background=FrameBG, borderwidth=BorderSize)
        matrixwindow.protocol("WM_DELETE_WINDOW", DestroyMatrixScreen)
        #
        toplab = Label(matrixwindow,text="Cross Point Interface ", style="A12B.TLabel")
        toplab.grid(row=0, column=0, columnspan=4, sticky=W)
        mcl1 = Label(matrixwindow,text="Netlist File")
        mcl1.grid(row=1, column=0, sticky=W)
        FileString = Entry(matrixwindow, width=50)
        FileString.bind("<Return>", ConfigCrossPoint)
        FileString.grid(row=2, column=0, columnspan=4, sticky=W)
        FileString.delete(0,"end")
        FileString.insert(0,"")
        NumConn = Label(matrixwindow,text="Number of Connections ")
        NumConn.grid(row=3, column=0, columnspan=4, sticky=W)
        ErrConn = Label(matrixwindow,text=" ")
        ErrConn.grid(row=4, column=0, columnspan=4, sticky=W)
        Browsebutton = Button(matrixwindow, text="Browse", style="W8.TButton", command=BrowsNetFile)
        Browsebutton.grid(row=5, column=0, sticky=W, pady=8)
        #
        Sendbutton = Button(matrixwindow, text="Send", style="W8.TButton", command=ConfigCrossPoint)
        Sendbutton.grid(row=5, column=1, sticky=W, pady=8)
        # 
        resetmxbutton = Button(matrixwindow, text="Reset", style="W8.TButton", command=ResetMatrix)
        resetmxbutton.grid(row=5, column=2, sticky=W, pady=7)
        #
        cpcl1 = Label(matrixwindow,text="Comp Pin")
        cpcl1.grid(row=6, column=0, sticky=W)
        jpcl1 = Label(matrixwindow,text="Jumper")
        jpcl1.grid(row=6, column=1, sticky=W)
        oncl1 = Label(matrixwindow,text="On/Off")
        oncl1.grid(row=6, column=2, sticky=W)
        #
        CompString = Spinbox(matrixwindow, width=6, cursor='double_arrow', values=CompSpinBoxList)
        #Entry(matrixwindow, width=7)
        CompString.bind("<Return>", ManualReturn)
        CompString.grid(row=7, column=0, columnspan=1, sticky=W)
        CompString.delete(0,"end")
        CompString.insert(0,"AWG1")
        JumperString = Spinbox(matrixwindow, width=6, cursor='double_arrow', values=JumperSpinBoxList)
        #Entry(matrixwindow, width=7)
        JumperString.bind("<Return>", ManualReturn)
        JumperString.grid(row=7, column=1, columnspan=1, sticky=W)
        JumperString.delete(0,"end")
        JumperString.insert(0,"JP1")
        OnOffString = Entry(matrixwindow, width=2)
        OnOffString.bind("<Return>", ManualReturn)
        OnOffString.grid(row=7, column=2, columnspan=1, sticky=W)
        OnOffString.bind('<MouseWheel>', onTextScroll)# with Windows OS
        OnOffString.bind("<Button-4>", onTextScroll)# with Linux OS
        OnOffString.bind("<Button-5>", onTextScroll)
        OnOffString.delete(0,"end")
        OnOffString.insert(0,"0")
        Setbutton = Button(matrixwindow, text="Set", style="W8.TButton", command=ManualMartix)
        Setbutton.grid(row=7, column=3, sticky=W, pady=8)
        # DC source controls
        DCSr = Label(matrixwindow,text="DC Sources")
        DCSr.grid(row=8, column=0, sticky=W)
        DCSr1 = Label(matrixwindow,text="AWG1 DC:")
        DCSr1.grid(row=9, column=0, sticky=W)
        DCSr1String = Entry(matrixwindow, width=7)
        DCSr1String.bind("<Return>", DCSr1Return)
        DCSr1String.bind('<MouseWheel>', onDCSr1Scroll)# with Windows OS
        DCSr1String.bind("<Button-4>", onDCSr1Scroll)# with Linux OS
        DCSr1String.bind("<Button-5>", onDCSr1Scroll)
        DCSr1String.bind('<Key>', onTextKey)
        DCSr1String.grid(row=9, column=1, columnspan=1, sticky=W)
        DCSr1String.delete(0,"end")
        DCSr1String.insert(0,"0.0")
        DCSr2 = Label(matrixwindow,text="AWG2 DC:")
        DCSr2.grid(row=10, column=0, sticky=W)
        DCSr2String = Entry(matrixwindow, width=7)
        DCSr2String.bind("<Return>", DCSr2Return)
        DCSr2String.bind('<MouseWheel>', onDCSr2Scroll)# with Windows OS
        DCSr2String.bind("<Button-4>", onDCSr2Scroll)# with Linux OS
        DCSr2String.bind("<Button-5>", onDCSr2Scroll)
        DCSr2String.bind('<Key>', onTextKey)
        DCSr2String.grid(row=10, column=1, columnspan=1, sticky=W)
        DCSr2String.delete(0,"end")
        DCSr2String.insert(0,"0.0")
##  
def DestroyMatrixScreen():
    global matrixwindow, MatrixStatus
    
    MatrixStatus.set(0)
    matrixwindow.destroy()
#
def DCSr1Return(temp):
    global ser, DCSr1String, AWGBuffLen, AWGADCvalue

    try:
        AWGADCvalue = float(eval(DCSr1String.get()))
    except:
        AWGADCvalue = 0.0
    AWG3 = numpy.full(AWGBuffLen, 1.0)
    AWGASendWave(AWG3)
    ser.write(b'Go\n') # default with both AWG off
#
def DCSr2Return(temp):
    global DCSr2String, AWGBuffLen, AWGBDCvalue

    try:
        AWGBDCvalue = float(eval(DCSr2String.get()))
    except:
        AWGBDCvalue = 0.0
    AWG3 = numpy.full(AWGBuffLen, 1.0)
    AWGBSendWave(AWG3)
    ser.write(b'go\n')
#
def onDCSr1Scroll(event):

    onTextScroll(event)
    DCSr1Return(event)
##
def onDCSr2Scroll(event):

    onTextScroll(event)
    DCSr2Return(event)
##
# AWG Stuff
#
def SetDCSr1_Ampl(Ampl): # used to toggle on / off AWG output
    global ser

    if Ampl == 0:
        ser.write(b'Gx\n')
    else:
        ser.write(b'Go\n')
#
def SetDCSr2_Ampl(Ampl): # used to toggle on / off AWG output
    global ser
    
    if Ampl == 0:
        ser.write(b'gx\n')
    else:
        AwgAOnOffBt.config(text='ON', style="Run.TButton")
        ser.write(b'go\n')
#
def AWGASendWave(AWG3):
    global ser, AWGARecLength, AWGBuffLen, AWGRes
    global AWGADCvalue, AWGPeakToPeak
    # Expect array values normalized from -1 to 1
    # scale values to send to 0 to 255 8 bits
    AWG3 = numpy.array(AWG3) * 0.5 # scale by 1/2
    # Get Low and High voltage levels
    MinCode = 0
    if MinCode < 0:
        MinCode = 0
    if MinCode > AWGRes:
        MinCode = AWGRes
    MaxCode = int((AWGADCvalue / AWGPeakToPeak) * AWGRes)
    if MaxCode < 0:
        MaxCode = 0
    if MaxCode > AWGRes:
        MaxCode = AWGRes
    # print("MaxCode = ", MaxCode, "MinCode = ", MinCode)
    # Scale to high and low voltage values
    Gain = MaxCode - MinCode
    Offset = int((MaxCode + MinCode)/2)
    AWG3 = (AWG3 * Gain) + Offset
    n = 0
    AWG1 = []
    while n < len(AWG3):
        AWG1.append(int(AWG3[n]))
        n = n + 1
    AWG1 = numpy.array(AWG1)
    #
    AWGARecLength = len(AWG1)
    if AWGARecLength > AWGBuffLen:
        AWGARecLength = AWGBuffLen
    if len(AWG1) < AWGBuffLen:
        # ser.write(b'B1024\n') # send AWG Buffer Length
        SendStr = 'N' + str(len(AWG1)) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    else:
        SendStr = 'N' + str(AWGBuffLen) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    #    
    #AWG1 = AWG1.tobytes()
    index = 0
    while index < AWGARecLength:
        data = AWG1[index]
        # send buffer index and waveform sample data
        SendStr = 'L' + str(index) + 'D' + str(data) + '\n'
        # print(SendStr)
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        index = index + 1
#
##    
def AWGBSendWave(AWG3):
    global ser, AWGBLastWave, AWGBRecLength, AWGBuffLen, AWGRes
    global AWGBDCvalue, AWGPeakToPeak
    # Expect array values normalized from -1 to 1
    # AWG3 = numpy.roll(AWG3, -68)
    AWGBLastWave = numpy.array(AWG3)
    AWG3 = numpy.array(AWG3) * 0.5 # scale by 1/2
    # Get Low and High voltage levels
    MinCode = 0
    if MinCode < 0:
        MinCode = 0
    if MinCode > AWGRes:
        MinCode = AWGRes
    MaxCode = int((AWGBDCvalue / AWGPeakToPeak) * AWGRes)
    if MaxCode < 0:
        MaxCode = 0
    if MaxCode > AWGRes:
        MaxCode = AWGRes
    #
    Gain = MaxCode - MinCode
    Offset = int((MaxCode + MinCode)/2)
    AWG3 = (AWG3 * Gain) + Offset
    n = 0
    AWG1 = []
    while n < len(AWG3):
        AWG1.append(int(AWG3[n]))
        n = n + 1
    AWG1 = numpy.array(AWG1)
    #
    AWGBRecLength = len(AWG1)
    if AWGBRecLength > AWGBuffLen:
        AWGBRecLength = AWGBuffLen
    if len(AWG1) < AWGBuffLen:
        SendStr = 'M' + str(len(AWG1)) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    else:
        SendStr = 'M' + str(AWGBuffLen) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    #    
    #AWG1 = AWG1.tobytes()
    index = 0
    while index < AWGBRecLength:
        data = AWG1[index]
        #
        SendStr = 'l' + str(index) + 'D' + str(data) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        index = index + 1
##
## Hardware specific Fucntion to close and exit ALICE
def Bcloseexit():
    global RUNstatus, Closed, core, ana_out, dev, ser, ConfigFileName
    
    RUNstatus.set(0)
    Closed = 1
    # 
    try:
        ser.write(b'Gx\n') # Turn off AWG
        ser.write(b'gx\n') # turn off PWM
        ser.write(b'x\n') # Reset all cross point switches to open
        # try to write last config file, Don't crash if running in Write protected space
        BSaveConfig(ConfigFileName)
        ser.close()
        try:
            dev.reset() # May need to be changed for specific hardware port
        except:
            print("dev reset didn't work")
        # exit
    except:
        donothing()

    root.destroy()
    exit()
#
#
def only_numerics(seq):
    seq_type= type(seq)
    return seq_type().join(filter(seq_type.isdigit, seq))
#
#
# USB communications with MP72 instrument
#
def send_nr(cmd):
    global dev
    # address taken from results of print(dev):   ENDPOINT 0x1: Bulk OUT
    dev.write(0x01,cmd) #0x01 or 0x03 ?
#
def send(cmd):
    global dev
    # address taken from results of print(dev):   ENDPOINT 0x1: Bulk OUT
    dev.write(0x01,cmd) #0x01 or 0x03 ?
    # address taken from results of print(dev):   ENDPOINT 0x81: Bulk IN
    result = (dev.read(0x81,100000,1000))
    # print(result)
    return result

def get_id():
    global dev
    # returns a character string <Manufacturer>,<model>,<serial number>,X.XX.XX
    return str(send('*IDN?').tobytes().decode('utf-8'))
#
def get_data(ch, yscale, yoffset):
    global dev
    # first 4 bytes indicate the number of data bytes following
    rawdata = send(':DATA:WAVE:SCREen:CH{}?'.format(ch))
    length = int().from_bytes(rawdata[0:2],'little',signed=False)
    data = [[],[]] # array of datapoints, [0] is value, [1] is errorbar if available (when 600 points are returned)
    if (length == 300):
        for idx in range(4,len(rawdata),1):
            # take 1 bytes and convert these to signed integer
            point = int().from_bytes([rawdata[idx]],'little',signed=True);
            data[0].append(yscale*(point-yoffset)/25)  # vertical scale is 25/div
            data[1].append(0)  # no errorbar
    else:
        for idx in range(4,len(rawdata),2):
            # take 2 bytes and convert these to signed integer for upper and lower value
            lower = int().from_bytes([rawdata[idx]],'little',signed=True)
            upper = int().from_bytes([rawdata[idx+1]],'little',signed=True)
            data[0].append(yscale*(lower+upper-2*yoffset)/50)  # average of the two datapoints
            data[1].append(yscale*(upper-lower)/50)  # errorbar is delta between upper and lower
    #
    return data
#
def get_header():
    global dev
    # first 4 bytes indicate the number of data bytes following
    header = send(':DATA:WAVE:SCREen:HEAD?')
    # print(header)
    header = header[4:].tobytes().decode('utf-8')
    return header
#
#
def Get_Data():
    global xscale, VBuffA, VBuffB, TRACESread, Header, EnableInterpFilter
    global CH1yscale, CH1yoffset, CH2yscale, CH2yoffset, SHOWsamples
    global Interp4Filter, InOffA, InOffB, InGainA, InGainB, InterpRate

    # Get the header and process it
    Header = yaml.safe_load(get_header())
    CH1yscale = float(Header["CHANNEL"][0]["PROBE"][0:-1]) * float(Header["CHANNEL"][0]["SCALE"][0:-2]) / divfactor.get(Header["CHANNEL"][0]["SCALE"][-2],1)
    CH1yoffset = int(Header["CHANNEL"][0]["OFFSET"])
    CH2yscale = float(Header["CHANNEL"][1]["PROBE"][0:-1]) * float(Header["CHANNEL"][1]["SCALE"][0:-2]) / divfactor.get(Header["CHANNEL"][1]["SCALE"][-2],1)
    CH2yoffset = int(Header["CHANNEL"][1]["OFFSET"])
    xscale = float(Header["TIMEBASE"]["SCALE"][0:-2]) / divfactor.get(Header["TIMEBASE"]["SCALE"][-2],1)

# Get data from instrument
    VBuff1 = get_data(1, CH1yscale, CH1yoffset)
    VBuff2 = get_data(2, CH2yscale, CH2yoffset)
##    TriggerStatus = send(":TRIGger: STATus?")
##    print(TriggerStatus)
##    if TriggerStatus == "TRIG" :
##        Is_Triggered = 1
##    else:
##        Is_Triggered = 0
#
    NoiseCH1 = numpy.array(VBuff1[1])
    NoiseCH2 = numpy.array(VBuff1[1])
    VBuff1 = numpy.array(VBuff1[0])
    VBuff2 = numpy.array(VBuff2[0])
    # Interpolate by InterpRate
    VBuffA = [] # Clear the A array 
    VBuffB = [] # Clear the B array
    index = 0
    while index < len(VBuff1): # build arrays
        pointer = 0
        while pointer < InterpRate:
            VBuffA.append(VBuff1[index])
            VBuffB.append(VBuff2[index])
            pointer = pointer + 1
        index = index + 1
    if EnableInterpFilter.get() == 1:
        VBuffA = numpy.pad(VBuffA, (InterpRate, 0), "edge")
        VBuffA = numpy.convolve(VBuffA, Interp4Filter )
        VBuffA = numpy.roll(VBuffA, -2)
        VBuffB = numpy.pad(VBuffB, (InterpRate, 0), "edge")
        VBuffB = numpy.convolve(VBuffB, Interp4Filter )
        VBuffB = numpy.roll(VBuffB, -4)
    VBuffA = numpy.array(VBuffA)
    VBuffB = numpy.array(VBuffB)
    # do external Gain / Offset calculations?
    VBuffA = (VBuffA - InOffA) * InGainA
    VBuffB = (VBuffB - InOffB) * InGainB
    TRACESread = 2
    SHOWsamples = len(VBuffA)
#
## try to connect to MP720781 Scope Meter
#
def ConnectDevice():
    global SerComPort, XpID, dev, cfg, untf, DevID, MaxSamples, AWGSAMPLErate, SAMPLErate
    global bcon, FWRevOne, HWRevOne, Header, InterpRate, ser
    global CH1Probe, CH2Probe, CH1VRange, CH2VRange, TimeDiv, TimeDivStr
    global CHAsb, CHBsb, TMsb, EnableInterpFilter
    global TgInput, TgEdge, TRIGGERlevel, TRIGGERentry

    if DevID == "No Device" or DevID == "MP72":
        #
        # Setup MP72 instrument
        dev = usb.core.find(idVendor=0x5345, idProduct=0x1234, backend=be1 )

        if dev is None:
            raise ValueError('Device not found')
            exit()
        print( 'number of configurations: ',dev.bNumConfigurations)
        cfg=dev[0]
        print( "number of interfaces of config 0: ",cfg.bNumInterfaces)
        intf=cfg[0,0]
        print( "number of end points: ",intf.bNumEndpoints)
        # usb.util.claim_interface(dev, intf)
        dev.set_configuration()
        #dev.write(0x01,'*IDN?')
        #print(dev.read(0x81,100000,1000))
        Device = get_id()
        print("DevID = ", Device)
        IDN = Device.split(',')
        DevID = IDN[2]
        print("Serial#: ", DevID)
        FWRevOne = IDN[3]
        print("Software Rev: ", FWRevOne) 
        HWRevOne = IDN[1]
        print("Model#: ", HWRevOne)
        #
        Header = yaml.safe_load(get_header())
        CH1Probe = Header["CHANNEL"][0]["PROBE"]
        CH1VRange = Header["CHANNEL"][0]["SCALE"]
        CH2Probe = Header["CHANNEL"][1]["PROBE"]
        CH2VRange = Header["CHANNEL"][1]["SCALE"]
        TimeDivStr = Header["TIMEBASE"]["SCALE"]
        TiggerLevel = Header["Trig"]["Items"]["Level"]
        TriggerEdge = Header["Trig"]["Items"]["Edge"]
        TriggerChannel = Header["Trig"]["Items"]["Channel"]
#
        TimeDiv = UnitConvert(TimeDivStr)
        TimeSpan = (Tdiv.get() * TimeDiv)# in Seconds
        SAMPLErate = (300 / TimeSpan)*4 # interpolate samples by 4x
        if TriggerChannel == "CH1":
            TgInput.set(1)
        else:
            TgInput.set(2)
        if TriggerEdge == "RISE":
            TgEdge.set(0)
        else:
            TgEdge.set(1)
        # print(dev)
        # bcon.configure(text="Conn", style="GConn.TButton")
        EnableInterpFilter.set(1)
        # Now try to connect to Cross Point board
        if XpID == "No Device" or XpID == "Pi Pico Cross Point Mini":
            #
            if SerComPort == 'Auto':
                ports = serial.tools.list_ports.comports()
                for port in ports: # ports:
                    # looking for this ID: USB\VID_2E8A&PID_000A
                    if "VID:PID=2E8A:000A" in port[2]:
                        print("Found: ", port[0])
                        SerComPort = port[0]
            # Setup instrument connection
                        print("Trying to open ", SerComPort)
                        try:
                            ser = serial.Serial(SerComPort)  # open serial port
                            ser.baudrate = 2000000 # Dummy number USB runs at max supported speed
            # Check if hardware ID string matched target?
                            ser.write(b'I\n') # request board ID
                            time.sleep(0.005)
                            IDstring = str(ser.readline())
                            ID = IDstring.replace("b'","")
                            ID = ID.replace("\\\\","")
                            ID = ID.replace("r","")
                            ID = ID.replace("n","")
                            ID = ID.replace("\\","")
                            ID = ID.replace("'","")
                            print("ID string ", ID)
                            if ID == "Pi Pico Cross Point Mini Red" :
                                break
                        except:
                            print("Port already in use?", SerComPort)
            else:
                print("Trying to open ", SerComPort)
                try:
                    ser = serial.Serial(SerComPort)  # open serial port
                    ser.baudrate = 2000000 # Dummy number USB runs at max supported speed
    # Check if hardware ID string matched target?
                    ser.write(b'I\n') # request board ID
                    time.sleep(0.005)
                    IDstring = str(ser.readline())
                    ID = IDstring.replace("b'","")
                    ID = ID.replace("\\\\","")
                    ID = ID.replace("r","")
                    ID = ID.replace("n","")
                    ID = ID.replace("\\","")
                    ID = ID.replace("'","")
                    print("ID string ", ID)
                    # if ID == "Pi Pico Scope 3.0" :
                        # break
                except:
                    print("Port already in use?", SerComPort)
            if ser is None:
                print('Device not found!')
                Bcloseexit()
                #exit()
            #
            ser.write(b'V\n') # Read Bacl VDD (.3.) supply voltage
            time.sleep(0.005)
            VDDstring = str(ser.readline())
            # print("VDD string ", VDDstring)
            if "V=" in VDDstring: #
                VDD = VDDstring.replace("b'V=","")
                VDD = VDD.replace("\\\\","")
                VDD = VDD.replace("r","")
                VDD = VDD.replace("n","")
                VDD = VDD.replace("\\","")
                VDD = VDD.replace("'","")
                Vsys = (int(VDD) * LSBsize) * 3.0 # 1/3 voltage divider
                print("Board Vsys = ", Vsys)
            #
            ser.write(b't3\n') # send Scope sample time in uSec
            time.sleep(0.005)
            print("set dt: 3 uSec")
            MaxSampleRate = SAMPLErate = 333333*InterpRate
            #
            SendStr = 'T' + str(ATmin) + '\n'
            # print(SendStr)
            SendByt = SendStr.encode('utf-8')
            # ser.write(b'T8\n') # send AWG sample time in uSec
            time.sleep(0.005)
            print("set at: ", ATmin , " uSec")
            AWGSampleRate = MaxAWGSampleRate = 1.0 / (ATmin / 1000000)
            #
            ser.write(b'Gx\n') # default with both AWG off
            ser.write(b'gx\n') 
            ## send Scope Buffer Length
            SendStr = 'b' + str(MinSamples) + '\n'
            # print(SendStr)
            SendByt = SendStr.encode('utf-8')
            ser.write(SendByt)
            # ser.write(b'b1024\n')  
            time.sleep(0.005)
            print("set Scope Samples: ", MinSamples)
            #
            #
            ser.write(b'N1024\n') # send AWG A Buffer Length
            ser.write(b'M1024\n') # send AWG B Buffer Length 
            time.sleep(0.005)
            print("set AWG Samples: 1024")
            #
            # ser.write(b'p500000\n')
            ser.write(b'R0\n') # default with AWG reset off
            ser.write(b'r0\n') # default with AWG pointer at loc 0
            #
            ser.write(b'Sx\n') # turn off AWG A by default
            MaxSamples = 4096 # assume 4X interpolation
    #
            ResetMatrix() # Reset all cross point switches to open
            time.sleep(0.01)
            # make cross point control screen
            MakeMatrixScreen()
            return(True) # return a logical true if sucessful!
        else:
            return(False)
        return(True) # return a logical true if sucessful!
    else:
        return(False)
#
# AWG Stuff
#
def SetAwgAmpl():
    global AWGAAmplEntry
    
    # send_nr(":FUNCtion:LOW " + ' {0:.3f} '.format(float(AWGAAmplEntry.get())))
    AMPLNum = abs(float(AWGAOffsetEntry.get()) - float(AWGAAmplEntry.get()))
    send_nr(":FUNCtion:AMPLitude " + ' {0:.3f} '.format(AMPLNum))
#
def SetAwgOffset():
    global AWGAOffsetEntry

    # send_nr(":FUNCtion:HIGHt " + ' {0:.3f} '.format(float(AWGAOffsetEntry.get())))
    OFFSNum = (float(AWGAOffsetEntry.get()) + float(AWGAAmplEntry.get())) / 2.0
    send_nr(":FUNCtion:OFFSet " + ' {0:.3f} '.format(OFFSNum))
#
def SetAwgFrequency():
    global AWGAFreqEntry

    FreqNum = UnitConvert(AWGAFreqEntry.get())
    send_nr(":FUNCtion:FREQuency " + str(FreqNum)) # ' {0:.1f} '.format(float(AWGAFreqEntry.get())))
#
def SetAwgSymmetry():
    global V

    send_nr(":FUNCtion:RAMP:SYMMetry " + str(int(AWGASymmetryEntry.get())))
#
def SetAwgDutyCycle():
    global AWGADutyCycleEntry

    send_nr(":FUNCtion:PULSe:DTYCycle " + str(int(AWGADutyCycleEntry.get())))
#
def SetAwgWidth():
    global AWGAWidthEntry

    WidthNum = UnitConvert(AWGAWidthEntry.get())
    send_nr(":FUNCtion:PULSe:WIDTh " + str(WidthNum))
#
def SetAwgA_Ampl(Ampl):

    if Ampl == 0:
        send_nr(":CHANnel OFF")
    else:
        send_nr(":CHANnel ON")
#
#
## Make the current selected AWG waveform
#
# Shape list SINE(1)|SQUare(2)|RAMP(3)|PULSe(4)|AmpALT(11)|AttALT(12)|StairDn(5)|StairUD(7) |
#  StairUp(6)|Besselj(8)|Bessely(9)|Sinc(10)
AwgString1 = "Sine"
AwgString2 = "Square"
AwgString3 = "Triangle"
AwgString4 = "Pulse"
AwgString5 = "Stair Down"
AwgString6 = "Stair Up"
AwgString7 = "Stair Up-Down"
AwgString8 = "Sinc"
AwgString9 = "Bessel J"
AwgString10 = "Bessel Y"
AwgString11 = "AmpALT"
AwgString12 = "AttALT"
#
def MakeAWGwaves(): # make awg waveforms in case something changed
    global AWGAShape, AWGAShapeLabel, EnableScopeOnly
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGASymmetryEntry, AWGADutyCycleEntry
    global AwgString1, AwgString2, AwgString3, AwgString4, AwgString5, AwgString6
    global AwgString7, AwgString8, AwgString9, AwgString10, AwgString11, AwgString12
    global AwgString13, AwgString14, AwgString15, AwgString16

    if AWGAShape.get()==1:
        send_nr(":FUNCtion SINE")
        AWGAShapeLabel.config(text = AwgString1) # change displayed value
    elif AWGAShape.get()==2:
        send_nr(":FUNCtion SQUare")
        AWGAShapeLabel.config(text = AwgString2) # change displayed value
    elif AWGAShape.get()==3:
        send_nr(":FUNCtion RAMP")
        AWGAShapeLabel.config(text = AwgString3) # change displayed value
    elif AWGAShape.get()==4:
        send_nr(":FUNCtion PULSe")
        AWGAShapeLabel.config(text = AwgString4) # change displayed value
    elif AWGAShape.get()==5:
        send_nr(":FUNCtion StairDn")
        AWGAShapeLabel.config(text = AwgString5) # change displayed value
    elif AWGAShape.get()==6:
        send_nr(":FUNCtion StairUp")
        AWGAShapeLabel.config(text = AwgString6) # change displayed value
    elif AWGAShape.get()==7:
        send_nr(":FUNCtion StairUD")
        AWGAShapeLabel.config(text = AwgString7) # change displayed value
    elif AWGAShape.get()==8:
        send_nr(":FUNCtion Sinc")
        AWGAShapeLabel.config(text = AwgString8) # change displayed value
    elif AWGAShape.get()==9:
        send_nr(":FUNCtion Besselj")
        AWGAShapeLabel.config(text = AwgString9) # change displayed value
    elif AWGAShape.get()==10:
        send_nr(":FUNCtion Bessely")
        AWGAShapeLabel.config(text = AwgString10) # change displayed value
    elif AWGAShape.get()==11:
        send_nr(":FUNCtion AmpALT")
        AWGAShapeLabel.config(text = AwgString11) # change displayed value
    elif AWGAShape.get()==12:
        send_nr(":FUNCtion AttALT")
        AWGAShapeLabel.config(text = AwgString12) # change displayed value
    else:
        AWGAShapeLabel.config(text = "Other Shape") # change displayed value
#
    SetAwgFrequency()
    SetAwgAmpl()
    SetAwgOffset()
    time.sleep(0.1)
#
# Trigger Stuff
#
def BSetTriggerSource():
    global TgInput

    if TgInput.get() == 1:
        send_nr(":TRIGger:SINGle:SOURce CH1")
    if TgInput.get() == 2:
        send_nr(":TRIGger:SINGle:SOURce CH2")
#
def BSetTrigEdge():
    global TgEdge
    
    if TgEdge.get() == 0:
        send_nr(":TRIGger:SINGle:EDGe RISE")
    else:
        send_nr(":TRIGger:SINGle:EDGe FALL")
#
def BTriggerMode(): 
    global TgInput, ana_str

    if (TgInput.get() == 0):
         #no trigger
        send_nr(":TRIGger:SINGle:SWEep AUTO")
    elif (TgInput.get() == 1):
         #trigger source set to detector of analog in channels
         #
        send_nr(":TRIGger:SINGle:SWEep NORMal")
    elif (TgInput.get() == 2):
        # trigger source set to detector of analog in channels
        # 
        send_nr(":TRIGger:SINGle:SWEep SINGle")
## evalute trigger level entry string to a numerical value and set new trigger level     
def SendTriggerLevel():
    global TRIGGERlevel, TRIGGERentry, RUNstatus

    # evalute entry string to a numerical value
    # send(":TRIGger:SINGle:EDGe:LEVel 1.0")
    send_nr(":TRIGger:SINGle:EDGe:LEVel "+ str(TRIGGERentry.get()))
    TRIGGERlevel = UnitConvert(TRIGGERentry.get())
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
# Set Internal / External triggering 
def BTrigIntExt(): # Dummy Routine because hardware does not support external triggering
    global TgSource, TriggerInt

    donothing()
    
# Set Horz possition from entry widget
def SetHorzPoss():
    global HozPoss, HozPossentry, RUNstatus, TimeDiv

    # get time scale
    HorzValue = UnitConvert(HozPossentry.get())
    HozOffset = int(TimeDiv/HorzValue)
    send_nr(":HORizontal:OFFset " + str(HozOffset))
    
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
#
def SetTriggerPoss():
    global HozPossentry, TgInput, TMsb, TimeDiv

    # get time scale
    HorzValue = UnitConvert(HozPossentry.get())
    HozOffset = int(TimeDiv/HorzValue)
    send_nr(":HORizontal:OFFset " + str(HozOffset))
    # prevent divide by zero error
## Set Hor time scale from entry widget
def SetSampleRate():
    global TimeDiv, TMsb, RUNstatus, Tdiv
    global TimeSpan, SAMPLErate, TIMEperDiv
    
    send_nr(":HORIzontal:SCALe " + TMsb.get())
    TimeSpan = (Tdiv.get() * TimeDiv)# in Seconds
    SAMPLErate = (300 / TimeSpan)*4 # interpolate samples by 4x 
#    
def HCHAlevel():
    global CHAsb, RUNstatus, CH1vpdvLevel
    
    send_nr(":CH1:SCALe " + str(CHAsb.get()))

def HCHBlevel():
    global CHBsb, RUNstatus, CH2vpdvLevel
    
    send_nr(":CH2:SCALe " + str(CHBsb.get()))  
        
def HOffsetA(event):
    global CHAOffset, CHAVPosEntry, CH1vpdvLevel, RUNstatus

    NumberOfDiv = int(CHAOffset/CH1vpdvLevel)
    send_nr(":CH1:OFFSet " + str(NumberOfDiv))

def HOffsetB(event):
    global CHBOffset, CHBVPosEntry, CH2vpdvLevel, RUNstatus

    NumberOfDiv = int(CHBOffset/CH2vpdvLevel)
    send_nr(":CH2:OFFSet " + str(NumberOfDiv))
#
#
def CouplCHA():
    global CHAcoupl

    send_nr(":CH1:COUPling " + CHAcoupl.get())
#
def CouplCHB():
    global CHBcoupl

    send_nr(":CH2:COUPling " + CHBcoupl.get())
#
