#
# Hardware specific interface functions
# For ADALM2000 aka M2k and Red M2k XPoint breadboards (8-1-2025)
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
    import libm2k
    libm2k_found = True
except:
    root.update()
    showwarning("WARNING","libm2k not installed?!")
    root.destroy()
    exit()
#
ConfigFileName = "alice-last-config.cfg"
Tdiv.set(10)
ZeroGrid.set(0)
TimeDiv = 0.002

#
# adjust for your specific hardware by changing these values
DevID = "M2k"
TimeSpan = 0.001
CHANNELS = 2 # Number of supported Analog input channels
AWGChannels = 2 # Number of supported Analog output channels
PWMChannels = 0 # Number of supported PWM output channels
DigChannels = 0 # Number of supported Dig channels
LogicChannels = 0 # Number of supported Logic Analyzer channels
EnablePGAGain = 0 # 1
EnableOhmMeter = 0
EnableDmmMeter = 0
EnableDigIO = 0
UseSoftwareTrigger = 1 # use software triggering for now
AllowFlashFirmware = 0
SaveDig = 0
InterpRate = 1
MaxSamples = 8192
SMPfft = MaxSamples # Set FFT size based on fixed acquisition record length
MatrixStatus = IntVar()
MatrixStatus.set(0)
AWGBuffLen = 1024
AWGPeakToPeak = 10.0 # Iternal reference voltage for MCP4822
AWGRes = 4095 # For 8 bits, 4095 for 12 bits, 1023 for 10 bits
ATmin = 8 # set minimum DAC update rate to 8 uSec
MaxAWGSampleRate = 750000 # set to 1 / 8 uSec
AWGSampleRate = MaxAWGSampleRate
TriggerChannel = "CH1"
TriggerEdge = "RISE"
Wait = 0.001
PlusUSEnab = IntVar()
PlusUSEnab.set(1)
NegUSEnab = IntVar()
NegUSEnab.set(1)
## Time list in s/div
TMpdiv = ("0.1us","0.2us","0.5us","1us","2us","5us", "10us", "20us", "50us", "100us", "200us", "500us", "1.0ms", "2.0ms", "5.0ms",
          "10ms", "20ms", "50ms", "100ms", "200ms", "500ms", "1.0s", "2.0s", "5.0s")
#
OldCH1pdvRange = CH1pdvRange = 1.0
OldCH2pdvRange = CH2pdvRange = 1.0
#
AWGAwaveform = numpy.ones(1024)
AWGBwaveform = numpy.ones(1024)
#
# Breadboard pin maping for Mimi Red 2 SMD layout
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

AINH = "CE6"; BINH = "CE7"; CINH = "CE8"
AWG1 = "CE14"; AWG2 = "CE15"
JP5 = "CE3"; JP6 = "CE9"; JP7 = "CE10"; JP8 = "CE11"
JP9 = "CE4"; JP10 = "CE5"; JP11 = "CE12"; JP12 = "CE13"
# Change these serial pins to match board layout
CSA = 7; CSB = 6; CSE = 5; CSC = 4; CSD = 3; RST = 2; DATA = 1; CLK = 0
#
JumperSpinBoxList = ("JP1", "JP2", "JP3", "JP4", "JP5", "JP6", "JP7", "JP8",
                     "JP9", "JP10", "JP11", "JP12", "JP13", "JP14", "JP15", "JP16")
CompSpinBoxList = ("AWG1", "AWG2", "AINH", "BINH", "CINH")
#
# Cross point matrix functions
#
def ReadNetlist(nfp):
    if ".cir" in nfp:
        # Use weird LTspice .cir file encodeing !? two bytes per character...
        try:
            NetList = open(nfp, 'r', encoding='utf-16-le')
        except:
            NetList = open(nfp, 'r', encoding='utf-8')
    else:
        # Use normal LTspice .net file encodeing one bytes per character...
        NetList = open(nfp, 'r', encoding='utf-8')
    lines = NetList.readlines()
    NetList.close()
    # print(lines)
    # create a list of strings for all subcircuit istance lines in netlist, ignore rest
    netlist_stripped = []
    for line in lines:
        # Select only the lines that contain "cross_point"
        # print(line)
        # line = line.encode('ascii')
        # if "TL" in line[0:4] or "BL" in line[0:4] or "TR" in line[0:4] or "BR" in line[0:4]:
        if "cross_point" in line:
            netlist_stripped.append(line.split())
    return netlist_stripped
#
def WhichChip(CompPin): # determine which cross point chip is used A-E

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
    global FileString, NumConn, ErrConn
    
    netlist = FileString.get()
    ComponentList = ReadNetlist(netlist) # list of all subcircuit instances found
    CompNum = len(ComponentList) # number of subcircuits
    index = 0
    connects = 0
    Errors = 0
    ErrorString = ""
    ResetMatrix() # Reset all cross point switches to open
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
                xpin = xpin.replace(chr(167),"")# remove §
            except:
                # for case where synbol instance name is the BB pin 
                xpin = CompPins[0]
                xpin = xpin.replace("X","")
                xpin = xpin.replace(chr(167),"")# remove §
                XPin = eval(xpin)
            #
            if XPin == 0: # cross point connected to node 0?
                xpin = CompPins[0]
                xpin = xpin.replace("X","")
                xpin = xpin.replace(chr(167),"")# remove §
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
                CmpNum = int(only_numerics(XPin)) # extract number 0-15
                SendToMatrix(JmpNum, CmpNum, ChipNum, 1)
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
#
def ResetMatrix():
    global CSA, CSB, CSC, CSD, CSE, CLK, RST, DATA
    # Reset all cross point switches to off
    dig.setValueRaw(RST, 1) # Toggel Reset pin High
    # Wait
    dig.setValueRaw(RST, 0) # Toggel Reset pin Low
    time.sleep(0.001) # Reset all cross point switches to open
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
    global CompString, JumperString, OnOffString, NumConn

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
        CmpNum = int(only_numerics(Xpin)) # extract number 0-7
        SendToMatrix(JmpNum, CmpNum, ChipNum, OnOff)

##
def DigIOSetUp():
    global CSA, CSB, CSC, CSD, CSE, CLK, RST, DATA
    # Configure Digital pins 0-7 as Outputs
    
    dig.setDirection(CSA, libm2k.DIO_OUTPUT)
    dig.enableChannel(CSA, True)
    dig.setValueRaw(CSA, 0) # CSA input idles Low
    dig.setDirection(CSB, libm2k.DIO_OUTPUT)
    dig.enableChannel(CSB, True)
    dig.setValueRaw(CSB, 0) # CSB input idles Low
    dig.setDirection(CSC, libm2k.DIO_OUTPUT)
    dig.enableChannel(CSC, True)
    dig.setValueRaw(CSC, 0) # CSC input idles Low
    dig.setDirection(CSD, libm2k.DIO_OUTPUT)
    dig.enableChannel(CSD, True)
    dig.setValueRaw(CSD, 0) # CSD input idles Low
    dig.setDirection(CSE, libm2k.DIO_OUTPUT)
    dig.enableChannel(CSE, True)
    dig.setValueRaw(CSE, 0) # CSE input idles Low
    dig.setDirection(CLK, libm2k.DIO_OUTPUT)
    dig.enableChannel(CLK, True)
    dig.setValueRaw(CLK, 1) # CLK input idles High
    dig.setDirection(RST, libm2k.DIO_OUTPUT)
    dig.enableChannel(RST, True)
    dig.setValueRaw(RST, 0) # RST input idles Low
    dig.setDirection(DATA, libm2k.DIO_OUTPUT)
    dig.enableChannel(DATA, True)
    dig.setValueRaw(DATA, 0) # DATA input idles Low
#
def SendToMatrix(xadr, yadr, cadr, swon):
    global CSA, CSB, CSC, CSD, CSE, CLK, RST, DATA
    # set cross point switch at address x , y, on chip () to on / off
    if(xadr>7):
        xadr=7
    if(yadr>15):
        yadr=15
    if(cadr>5):
        cadr=5
    if(cadr==1):
        dadr=CSA
    if(cadr==2):
        dadr=CSB
    if(cadr==3):
        dadr=CSC
    if(cadr==4):
        dadr=CSD
    if(cadr==5):
        dadr=CSE
    # Send x y address to chip(s)
    dig.setValueRaw(CLK, 1) # CLK input idles High
    # Send first data bit
    if(xadr & 0b100):
        dig.setValueRaw(DATA, 1) # adr is High
    else:
        dig.setValueRaw(DATA, 0) # adr is Low
    dig.setValueRaw(CLK, 0) # CLK Low
    dig.setValueRaw(CLK, 1) # CLK High
    # Send Second data bit
    if(xadr & 0b010):
        dig.setValueRaw(DATA, 1) # adr is High
    else:
        dig.setValueRaw(DATA, 0) # adr is Low
    dig.setValueRaw(CLK, 0) # CLK Low
    dig.setValueRaw(CLK, 1) # CLK High
    # Send third data bit
    if(xadr & 0b001):
        dig.setValueRaw(DATA, 1) # adr is High
    else:
        dig.setValueRaw(DATA, 0) # adr is Low
    dig.setValueRaw(CLK, 0) # CLK Low
    dig.setValueRaw(CLK, 1) # CLK High
    # Now Yaddr
    # Send first data bit
    if(yadr & 0b1000):
        dig.setValueRaw(DATA, 1) # adr is High
    else:
        dig.setValueRaw(DATA, 0) # adr is Low
    dig.setValueRaw(CLK, 0) # CLK Low
    dig.setValueRaw(CLK, 1) # CLK High
    # Send Second data bit
    if(yadr & 0b0100):
        dig.setValueRaw(DATA, 1) # adr is High
    else:
        dig.setValueRaw(DATA, 0) # adr is Low
    dig.setValueRaw(CLK, 0) # CLK Low
    dig.setValueRaw(CLK, 1) # CLK High
    # Send Third data bit
    if(yadr & 0b0010):
        dig.setValueRaw(DATA, 1) # adr is High
    else:
        dig.setValueRaw(DATA, 0) # adr is Low
    dig.setValueRaw(CLK, 0) # CLK Low
    dig.setValueRaw(CLK, 1) # CLK High
    # Send fourth data bit
    if(yadr & 0b0001):
        dig.setValueRaw(DATA, 1) # adr is High
    else:
        dig.setValueRaw(DATA, 0) # adr is Low
    dig.setValueRaw(CLK, 0) # CLK Low
    dig.setValueRaw(CLK, 1) # CLK High
    # Set switch at address on or off
    if(swon == 1):
        dig.setValueRaw(DATA, 1) # Data is High switch on
    else:
        dig.setValueRaw(DATA, 0) # Data is Low switch off
    # Now Strobe which chip
    dig.setValueRaw(dadr, 1) # STB High
    dig.setValueRaw(dadr, 0) # STB Low
    dig.setValueRaw(DATA, 0) # Data idles Low
#
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
##  
def DestroyMatrixScreen():
    global matrixwindow, MatrixStatus
    
    MatrixStatus.set(0)
    matrixwindow.destroy()
#
# M2k Data capture Stuff
#
# Set Scope Sample Rate based on Horz Time Scale
#
def SetSampleRate():
    global TimeSpan, MaxSampleRate, SHOWsamples, InterpRate, Tdiv, GRW
    global TrigSource, TriggerEdge, TriggerInt, SAMPLErate, TimeDiv, ser

    OldShowSamples = SHOWsamples
    TimeDiv = UnitConvert(TMsb.get())
    # see if time base hase changed and adjust gain corrections
    TryRate = (GRW)/(10*TimeDiv)
    #print("TimeDiv = ", TimeDiv)
    #print("TryRate = ", TryRate)
    #print("SAMPLErate = ", SAMPLErate)
    if TryRate <= 1000:
        NewSAMPLErate = 1000
    elif TryRate > 1000 and TryRate <= 10000:
        NewSAMPLErate = 10000
    elif TryRate > 10000 and TryRate <= 100000:
        NewSAMPLErate = 100000
    elif TryRate > 100000 and TryRate <= 1000000:
        NewSAMPLErate = 1000000
    elif TryRate > 1000000 and TryRate <= 10000000:
        NewSAMPLErate = 10000000
    elif TryRate > 10000000:
        NewSAMPLErate = 100000000
    if NewSAMPLErate != SAMPLErate:
        SAMPLErate = NewSAMPLErate
        #print("Set SAMPLErate = ", SAMPLErate)
        ain.setSampleRate(SAMPLErate)
#
def Get_Data():
    global ain, aout, ctx, trig, Wait, TimeDiv, SHOWsamples
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global TgInput, VBuffA, VBuffB # , VBuffC, VBuffD, VBuffG
    global D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on, COLORtrace8
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    global TRIGGERentry, TRIGGERsample, SaveDig, CHANNELS, TRACESread
    global OldCH1pdvRange, OldCH2pdvRange, CH1pdvRange, CH2pdvRange
    global CHAsb, CHBsb

    # Get data from M2k
##    if hldn+hozpos > MaxSamples-twoscreens:
##        hldn = MaxSamples-twoscreens-hozpos
##        HoldOffentry.delete(0,END)
##        HoldOffentry.insert(0, hldn*1000/SAMPLErate)
    #
    if SAMPLErate == 1000:
        SHOWsamples = 4096
    elif SAMPLErate == 10000:
        SHOWsamples = 8192
    else:
        SHOWsamples = 8192 # twoscreens + hldn + hozpos
    if SHOWsamples > MaxSamples: # or a Max of 16,384 samples
        SHOWsamples = MaxSamples
    if SHOWsamples < MinSamples: # or a Min of 1000 samples
        SHOWsamples = MinSamples
    #
    twoscreens = int(SAMPLErate * 20.0 * TimeDiv / 1000.0) # number of samples to acquire, 2 screen widths
    onescreen = int(twoscreens/2)
    #
    # get the vertical ranges
    try:
        CH1pdvRange = UnitConvert(CHAsb.get()) # float(eval(CHAsb.get()))
    except:
        CHAsb.delete(0,END)
        CHAsb.insert(0, CH1pdvRange)
    try:
        CH2pdvRange = UnitConvert(CHBsb.get()) # float(eval(CHBsb.get()))
    except:
        CHBsb.delete(0,END)
        CHBsb.insert(0, CH2pdvRange)
    if CH1pdvRange < 1.0:
        if OldCH1pdvRange != CH1pdvRange:
            ain.setRange(0,-2.5,2.5)
    else:
        if OldCH1pdvRange != CH1pdvRange:
            ain.setRange(0,-25,25)
    if CH2pdvRange < 1.0:
        if OldCH2pdvRange != CH2pdvRange:
            ain.setRange(1,-2.5,2.5)
    else:
        if OldCH2pdvRange != CH2pdvRange:
            ain.setRange(1,-25,25)
    OldCH1pdvRange = CH1pdvRange
    OldCH2pdvRange = CH2pdvRange
    #
    try:
        ADsignal1 = ain.getSamples(SHOWsamples) # read the buffer
        #
        VBuffA = ADsignal1[0] # make the V Buff array for trace A
        VBuffB = ADsignal1[1] # make the V Buff array for trace B
        SHOWsamples = len(VBuffA)
        VBuffA = numpy.array(VBuffA)
        VBuffB = numpy.array(VBuffB)
        VBuffA = (VBuffA - InOffA) * InGainA
        VBuffB = (VBuffB - InOffB) * InGainB
        TRACESread = 2
    except:
        ain.flushBuffer()
        Is_Triggered = 0
        ADsignal1 = []
    time.sleep(Wait)
# 
def Get_Buffer():
    global Wait, ser, MaxSampleRate, InterpRate, SAMPLErate
    global ABuff, iterCount, SampleTime, MinSamples, TRACESread
    
    time.sleep(Wait)
#
## Hardware specific Fucntion to close and exit ALICE
def Bcloseexit():
    global RUNstatus, Closed, core, ana_out, dev, ser, ConfigFileName
    
    RUNstatus.set(0)
    Closed = 1
    # 
    try:
        # try to write last config file, Don't crash if running in Write protected space
        BSaveConfig(ConfigFileName)
        # close context and exit
        try:
            aout.enableChannel(0, False)
            aout.enableChannel(1, False)
            libm2k.contextClose(ctx) # deviceClose(ctx)
        except:
            print("closing anyway")
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
## try to connect to M2k
#
def ConnectDevice():
    global ctx, ain, aout, trig, DevID, bcon, FWRev, HWRev, UserPS, ProductName
    global ain, aout, trig, dig, AWGASampleRate, AWGBSampleRate
    global CH1Probe, CH2Probe, CH1VRange, CH2VRange, TimeDiv, TimeDivStr
    global CHAsb, CHBsb, TMsb, EnableInterpFilter, InterpRate
    global TgInput, TgEdge, TRIGGERlevel, TRIGGERentry, TriggerChannel, TriggerEdge

    if DevID == "No Device" or DevID == "M2k":
        #
        # Setup M2k instrument
        ctx=libm2k.m2kOpen('ip:m2k.local')
        # the uri can be something similar to: "ip:192.168.2.1" or "usb:1.6.5"
##        ProductName = ctx.getContextAttributeValue('usb,product')
##        # ProductName = ctx.getContextAttributeValue('product')
##        try:
##            ProductName = ctx.getContextAttributeValue('usb,product')
##        except:
##            print('No Device plugged IN!')
##            ProductName = "No Device"
##            bcon.configure(text="Recon", style="RConn.TButton")
##            return
##        if ProductName != 'M2k (ADALM-2000)':
##            print('M2K board not found!')
##            print(ProductName, " Found")
##            DevID = "No Device"
##            bcon.configure(text="Recon", style="RConn.TButton")
##            return
        bcon.configure(text="Conn",  style="GConn.TButton")
        DevID = ctx.getContextAttributeValue('hw_serial')
        print(DevID)
        HWRev = ctx.getContextAttributeValue('hw_model')
        if "M2k" in HWRev:
            DevID = "M2k"
        print(HWRev)
        FWRev = ctx.getContextAttributeValue('fw_version')
        print(FWRev)
    
    # define analog inputs and outputs
        ain=ctx.getAnalogIn()
        aout=ctx.getAnalogOut()
        trig=ain.getTrigger()
    #
        ain.reset()
        aout.reset()
    #
        ain.setKernelBuffersCount(1) # added line here
        ain.enableChannel(0,True)
        ain.enableChannel(1,True)
        ain.setSampleRate(100000)
        ain.setRange(0,-2,2)

    ##    trig.setAnalogSource(0) # Channel 0 as source
    ##    trig.setAnalogCondition(0,libm2k.RISING_EDGE_ANALOG) # RISING_EDGE)
    ##    trig.setAnalogLevel(0,0.5)  # Set trigger level at 0.5
    ##    trig.setAnalogDelay(0) # Trigger is centered
    ##    trig.setAnalogMode(1,libm2k.ANALOG)

        aout.setSampleRate(0, AWGSampleRate)
        aout.setSampleRate(1, AWGSampleRate)
        aout.enableChannel(0, True)
        aout.enableChannel(1, True)
    # User power supply
        UserPS = ctx.getPowerSupply()

    # Digital Input / OutPut channels
        dig=ctx.getDigital()

        dig.setSampleRateIn(10000)
        DigIOSetUp()

    # Digital patten generator output stuff
        dig.setSampleRateOut(10000)
        # make a temp digital pattern buffer
        # DigBuff0 = iio.Buffer(Dig_Out, 8192, True)
        #
        SAMPLErate = (2048 / TimeSpan)*2 # 2 screens of samples
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
        # make cross point control screen
        MakeMatrixScreen()
        PlaceUSPower()
        time.sleep(0.01)
        BPlusOnOff() # Power up matrix chips
        BNegOnOff()
        time.sleep(0.01)
        ResetMatrix() # Reset all cross point switches to open
    # do a self calibration
        adc_calib=ctx.calibrateADC()
        dac_calib=ctx.calibrateDAC()

        return(True) # return a logical true if sucessful!
    else:
        return(False)
#
# M2k AWG stuff
#
def SetAwgSampleRate():
    global AWGASampleRate, AWGBSampleRate, AWGSampleRate

    SetAwgASampleRate()
    SetAwgBSampleRate()
    AWGSampleRate = AWGASampleRate
    if AWGASampleRate >= AWGBSampleRate:
        AWGSampleRate = AWGASampleRate
    else:
        AWGSampleRate = AWGBSampleRate
#
def SetAwgASampleRate():
    global aout, AWGAFreqEntry, AWGAFreqvalue, AWGASampleRate

    try:
        AWGAFreqvalue = float(eval(AWGAFreqEntry.get()))
    except:
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)

    if AWGAFreqvalue > 25000000: # max freq is 25 MHz
        AWGAFreqvalue = 25000000
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)
    if AWGAFreqvalue <= 0: # Set negative frequency entry to 0
        AWGAFreqvalue = 1
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)
    if AWGAFreqvalue <= 10000: # 10 times 7500
        AWGASampleRate = 7500000
##    elif AWGAFreqvalue > 7500 and AWGAFreqvalue < 75000: # 10 times 75000
##        AWGASampleRate = 7500000
    elif AWGAFreqvalue > 10000 and AWGAFreqvalue < 25000000: # 10 times 750000
        AWGASampleRate = 75000000
    aout.setSampleRate(0, AWGASampleRate) # m2k_dac_a.attrs["sampling_frequency"].value = str(AWGASampleRate)
#    print(aout.getSampleRate(0))
#    print(aout.getOversamplingRatio(0))

def SetAwgBSampleRate():
    global aout, AWGBFreqEntry, AWGBFreqvalue, AWGBSampleRate, m2k_dac_b

    try:
        AWGBFreqvalue = float(eval(AWGBFreqEntry.get()))
    except:
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)

    if AWGBFreqvalue > 25000000: # max freq is 25 MHz
        AWGBFreqvalue = 25000000
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)
    if AWGBFreqvalue <= 0: # Set negative frequency entry to 0
        AWGBFreqvalue = 1
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)
    if AWGBFreqvalue <= 10000: # 10 times 7500
        AWGBSampleRate = 7500000
##    elif AWGBFreqvalue > 7500 and AWGBFreqvalue < 75000: # 10 times 75000
##        AWGBSampleRate = 7500000
    elif AWGBFreqvalue > 10000 and AWGBFreqvalue < 25000000: # 10 times 750000
        AWGBSampleRate = 75000000
    # aout.stop()
    aout.setSampleRate(1, AWGBSampleRate) # m2k_dac_b.attrs["sampling_frequency"].value = str(AWGBSampleRate)
#        
def AWGASendWave(AWG3):
    global AWGARecLength, AWGBuffLen, AWGAwaveform
    global AWGAAmplvalue, AWGAOffsetvalue, AWGPeakToPeak

    # Expect array values normalized from -1 to 1
    # scale values to minimum and max voltage
    AWG3 = numpy.array(AWG3) * 0.5 # scale by 1/2
    # Get Low and High voltage levels
    # Scale to high and low voltage values
    Gain = AWGAOffsetvalue - AWGAAmplvalue
    Offset = (AWGAOffsetvalue + AWGAAmplvalue)/2.0
    # print("Gain = ", Gain, "Offset = ", Offset)
    AWGAwaveform = numpy.array((AWG3 * Gain) + Offset)
#
##    
def AWGBSendWave(AWG3):
    global AWGBLastWave, AWGBRecLength, AWGBuffLen, AWGBwaveform
    global AWGBAmplvalue, AWGBOffsetvalue, AWGPeakToPeak
    # Expect array values normalized from -1 to 1
    # AWG3 = numpy.roll(AWG3, -68)
    AWGBLastWave = numpy.array(AWG3)
    AWG3 = numpy.array(AWG3) * 0.5 # scale by 1/2
    # Get Low and High voltage levels
    #
    Gain = AWGBOffsetvalue - AWGBAmplvalue
    Offset = (AWGBOffsetvalue + AWGBAmplvalue)/2.0
    AWGBwaveform = numpy.array((AWG3 * Gain) + Offset)
    
#
## Make the current selected AWG waveform
#
# Shape list SINE(1)|SQUare(2)|RAMP(3)|PULSe(4)|AmpALT(11)|AttALT(12)|StairDn(5)|StairUD(7) |
#  StairUp(6)|Besselj(8)|Bessely(9)|Sinc(10)
##AwgString1 = "Sine"
##AwgString2 = "Triangle"
##AwgString3 = "Ramp Up"
##AwgString4 = "Ramp Down"
##AwgString5 = "Stair Up"
##AwgString6 = "Stair Down"
##AwgString7 = "Stair Up-Down"
AwgString9 = "Cosine"
AwgString10 = "Full Wave Sine"
AwgString11 = "Half Wave Sine"
AwgString12 = "Fourier Series"
AwgString13 = "Schroeder Chirp"
AwgString14 = "Sine Power Pulse"
#
def MakeAWGwaves(): # make awg waveforms in case something changed
    global aout, AWGAAmplvalue, AWGAOffsetvalue
    global AWGAFreqvalue, AWGAPhasevalue, AWGAPhaseDelay
    global AWGADutyCyclevalue, AWGARepeatFlag
    global AWGAWave, AWGAMode, AWGAwaveform, AWGAIOMode
    global AWGSampleRate, AWG1Offset 
    global AWGAoffset, AWGBgain, AWGBoffset
    global AWGAModeLabel, DevID, HWRevOne
    global AWGAShape, AWGBwaveform
    global AWGBAmplvalue, AWGBOffsetvalue,  AWGAwaveform
    global AWGBFreqvalue, AWGBPhasevalue, AWGBPhaseDelay
    global AWGBDutyCyclevalue, FSweepMode, AWGBRepeatFlag, dac_b_pd
    global AWGSampleRate, AWG2Offset, AWGBWave, AWGBMode
    global ctx, m2k_AWG2pd, m2k_fabric, Buff0, Buff1, m2k_dac_a, m2k_dac_b
    global AWGBMode, AWGBIOMode, AWGBModeLabel
    global AWGBShape, AWGBbinform
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
    aout.setCyclic(True)
    # aout.stop()
#
    if AWGAShape.get()== 0:
        AWGAMakeDC()
        AWGAShapeLabel.config(text = "DC") # change displayed value
    elif AWGAShape.get()==1:
        AWGAMakeSine()
        AWGAShapeLabel.config(text = AwgString1) # change displayed value
    elif AWGAShape.get()==2:
        AWGAMakeSquare()
        AWGAShapeLabel.config(text = AwgString2) # change displayed value
    elif AWGAShape.get()==3:
        AWGAMakeTriangle()
        AWGAShapeLabel.config(text = AwgString3) # change displayed value
    elif AWGAShape.get()==4:
        AWGAMakePulse()
        AWGAShapeLabel.config(text = AwgString4) # change displayed value
    elif AWGAShape.get()==5:
        AWGAMakeRampDn()
        AWGAShapeLabel.config(text = AwgString5) # change displayed value
    elif AWGAShape.get()==6:
        AWGAMakeRampUp()
        AWGAShapeLabel.config(text = AwgString6) # change displayed value
    elif AWGAShape.get()==7:
        AWGAMakeStair()
        AWGAShapeLabel.config(text = AwgString7) # change displayed value
    elif AWGAShape.get()==8:
        AWGAMakeSinc()
        AWGAShapeLabel.config(text = AwgString8) # change displayed value
    elif AWGAShape.get()==9:
        AWGAMakeSine()
        AWGAShapeLabel.config(text = AwgString9) # change displayed value
    elif AWGAShape.get()==10:
        AWGAMakeFullWaveSine()
        AWGAShapeLabel.config(text = AwgString10) # change displayed value
    elif AWGAShape.get()==11:
        AWGAMakeHalfWaveSine()
        AWGAShapeLabel.config(text = AwgString11) # change displayed value
    elif AWGAShape.get()==12:
        AWGAMakeFourier()
        AWGAShapeLabel.config(text = AwgString12) # change displayed value
    elif AWGAShape.get()==13:
        SetAwgSampleRate()
        AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
        AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
        AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
        NrTones = int(eval(AWGADutyCycleEntry.get()))
        ampl = 3.0/NrTones
        if ampl > 0.25:
            ampl = 0.25
        AWGASendWave(SchroederPhase(MaxSamples, NrTones, ampl))
        AWGAShapeLabel.config(text = AwgString13) # change displayed value
    elif AWGAShape.get()==14:
        SetAwgSampleRate()
        AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
        AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
        AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
        Power = int(eval(AWGADutyCycleEntry.get()))
        Power = Power / 100.0
        ampl = 1
        AWGASendWave(SinePower(100, Power, 180, ampl))
        AWGAShapeLabel.config(text = AwgString14) # change displayed value
    else:
        AWGAShapeLabel.config(text = "Other Shape") # change displayed value
#
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    if BisCompA.get() == 1:
        SetBCompA()
#
    if AWGBShape.get() == 0:
        AWGBMakeDC()
        AWGBShapeLabel.config(text = "DC") # change displayed value
    elif AWGBShape.get() == 1:
        AWGBMakeSine()
        AWGBShapeLabel.config(text = AwgString1) # change displayed value
    elif AWGBShape.get() == 2:
        AWGBMakeSquare()
        AWGBShapeLabel.config(text = AwgString2) # change displayed value
    elif AWGBShape.get() == 3:
        AWGBMakeTriangle()
        AWGBShapeLabel.config(text = AwgString3) # change displayed value
    elif AWGBShape.get() == 4:
        AWGBMakePulse()
        AWGBShapeLabel.config(text = AwgString4) # change displayed value
    elif AWGBShape.get()==5:
        AWGBMakeRampDn()
        AWGBShapeLabel.config(text = AwgString5) # change displayed value
    elif AWGBShape.get()==6:
        AWGBMakeRampUp()
        AWGBShapeLabel.config(text = AwgString6) # change displayed value
    elif AWGBShape.get()==7:
        AWGBMakeStair()
        AWGBShapeLabel.config(text = AwgString7) # change displayed value
    elif AWGBShape.get()==8:
        AWGBMakeSinc()
        AWGBShapeLabel.config(text = AwgString8) # change displayed value
    elif AWGBShape.get()==9:
        AWGBMakeSine()
        AWGBShapeLabel.config(text = AwgString9) # change displayed value
    elif AWGBShape.get()==10:
        AWGBMakeFullWaveSine()
        AWGBShapeLabel.config(text = AwgString10) # change displayed value
    elif AWGBShape.get()==11:
        AWGBMakeHalfWaveSine()
        AWGBShapeLabel.config(text = AwgString11) # change displayed value
    elif AWGBShape.get()==12:
        AWGBMakeFourier()
        AWGBShapeLabel.config(text = AwgString12) # change displayed value
    elif AWGBShape.get()==13:
        SetAwgSampleRate()
        AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
        AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
        AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
        NrTones = int(eval(AWGBDutyCycleEntry.get()))
        ampl = 3.0/NrTones
        if ampl > 0.25:
            ampl = 0.25
        AWGBSendWave(SchroederPhase(MaxSamples, NrTones, ampl))
        AWGBShapeLabel.config(text = AwgString13) # change displayed value
    else:
        AWGBShapeLabel.config(text = "Other Shape") # change displayed value
#
    # aout.stop()
    # print(len(AWGAwaveform), len(AWGBwaveform))
    # buffer = [AWGAwaveform, AWGBwaveform]
    aout.setCyclic(True)
    aout.push([AWGAwaveform, AWGBwaveform])
    # 
    time.sleep(0.01)
    #aout.enableChannel(0, True)
    #aout.enableChannel(1, True)
    
def SetAwgA_Ampl(Ampl): # used to toggle on / off AWG output
    global aout, AwgBOnOffBt, AwgaOnOffLb, AwgbOnOffLb
    global AWGAwaveform, AWGBwaveform

    #AwgBOnOffBt.config(state=DISABLED)
    #AwgaOnOffLb.config(text="AWG Output ")
    #AwgbOnOffLb.config(text=" ")
    if Ampl == 0:
        #print("Power down AWG 1")
        aout.enableChannel(0, False)
    else:
        #print("power up AWG 1")
        aout.enableChannel(0, True)
    aout.push([AWGAwaveform, AWGBwaveform])
#
def SetAwgB_Ampl(Ampl): # used to toggle on / off AWG output
    global aout, AwgBOnOffBt, AwgAOnOffBt, AwgaOnOffLb, AwgbOnOffLb
    global AWGAwaveform, AWGBwaveform

    #AwgBOnOffBt.config(state=DISABLED)
    #AwgaOnOffLb.config(text="AWG Output ")
    #AwgbOnOffLb.config(text=" ")
    if Ampl == 0:
        #print("Power down AWG 2")
        aout.enableChannel(1, False)
    else:
        # AwgAOnOffBt.config(text='ON', style="Run.TButton")
        #print("power up AWG 2")
        aout.enableChannel(1, True)
    aout.push([AWGAwaveform, AWGBwaveform])
#
def HOffsetA():
    global CHAOffset, CHAVPosEntry

    try:
        CHAOffset = 0.0 - float(eval(CHAVPosEntry.get()))
        CHAOffset
        ain.setVerticalOffset(0,CHAOffset)
    except:
        CHAVPosEntry.delete(0,END)
        CHAVPosEntry.insert(0, CHAOffset)
#
def HOffsetB():
    global CHBOffset, CHBVPosEntry

    try:
        CHBOffset = 0.0 - float(eval(CHBVPosEntry.get()))
        ain.setVerticalOffset(1,CHBOffset)
    except:
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, CHBOffset)
#
# Hardware Specific Trigger functions
#
def SendTriggerLevel():
    global TRIGGERlevel, ser, RUNstatus, AWGPeakToPeak
    # Min and Max trigger level specific to hardware
    if TRIGGERlevel > 4.0:
        TRIGGERlevel = 4.0
        TRIGGERentry.delete(0,"end")
        TRIGGERentry.insert(0, ' {0:.2f} '.format(4.0))
    if TRIGGERlevel < 0.0:
        TRIGGERlevel = 0.0
        TRIGGERentry.delete(0,"end")
        TRIGGERentry.insert(0, ' {0:.2f} '.format(0.0))
# Adjust trigger level.
# representa a 8-bit number (0-255) sent to DAC

# Set Horz possition from entry widget
def SetHorzPoss():
    global HozPossentry, ser

    HzSteps = int(float(HozPossentry.get()))
    Hz_Value = 511-HzSteps
    if Hz_Value > 256:
        T_High = 1
        T_Low = Hz_Value - 256
    else:
        T_High = 0
        T_Low = Hz_Value
#
# Set Internal / External triggering bits
def BTrigIntExt():
    global trig, TriggerMethod, Is_Triggered, hozpos, TRIGGERsample
    global TgInput, TgEdge, TRIGGERlevel

    if TriggerMethod.get() == 1: # Using Hardware triggering
        TRIGGERsample = 0 # reset pointer to zero when using HW trigger
        Is_Triggered = 1
        trig.setAnalogDelay(hozpos)
        if TgInput.get() == 0:
            trig.setAnalogMode(0,libm2k.ALWAYS)
            trig.setAnalogMode(1,libm2k.ALWAYS)
        elif TgInput.get() == 1:
            trig.setAnalogMode(0,libm2k.ANALOG)
            trig.setAnalogMode(1,libm2k.ALWAYS)
            trig.setAnalogLevel(0,TRIGGERlevel)
        elif TgInput.get() == 3:
            trig.setAnalogMode(0,libm2k.ALWAYS)
            trig.setAnalogMode(1,libm2k.ANALOG)
            trig.setAnalogLevel(1,TRIGGERlevel)
        if TgEdge.get() == 0:
            trig.setAnalogCondition(0,libm2k.RISING_EDGE_ANALOG)
            trig.setAnalogCondition(1,libm2k.RISING_EDGE_ANALOG)
        else:
            trig.setAnalogCondition(0,libm2k.FALLING_EDGE_ANALOG) # RISING_EDGE)
            trig.setAnalogCondition(1,libm2k.FALLING_EDGE_ANALOG) # RISING_EDGE)
    else:
        trig.setAnalogMode(0,libm2k.ALWAYS)
        trig.setAnalogMode(1,libm2k.ALWAYS)
#
# Set Triggering source bits
def BSetTriggerSource():
    global TgInput, TrigSource, TriggerInt

    if TgInput.get() == 1:
        TrigSource = 0x00 # bit 4 0x00 = Channel A
    if TgInput.get() == 2:
        TrigSource = 0x10 # bit 4 0x10 = Channel B
    if TgInput.get() == 0:
        TriggerInt = 0x40 # bit 6 0x40 No Triggers (free-run)?
# Set Trigger edge bits
def BSetTrigEdge():
    global TgEdge, TriggerEdge
    
    if TgEdge.get() == 0:
        trig.setAnalogCondition(0,libm2k.RISING_EDGE_ANALOG)
        trig.setAnalogCondition(1,libm2k.RISING_EDGE_ANALOG)
#
def PlaceUSPower():
    global frame2r, plusUSEntry, negUSEntry, plusUSrb, negUSrb, plusUSlab, negUSlab
    
    # User Power supply controls
    userlab = Label(frame2r, text="External Power Supplies")
    userlab.pack(side=TOP)
    PlusUS = Frame( frame2r )
    PlusUS.pack(side=TOP)
    plusUSrb = Label(PlusUS, text="5.00")
    plusUSrb.pack(side=RIGHT)
    plusUSEntry = Entry(PlusUS, width=5)
    plusUSEntry.bind("<Return>", BplusUS)
    plusUSEntry.bind('<MouseWheel>', scrollPlusUS)
    plusUSEntry.bind('<Key>', onTextKey)
    plusUSEntry.pack(side=RIGHT)
    plusUSEntry.delete(0,"end")
    plusUSEntry.insert(0,5.0)
    plusUSlab = Checkbutton(PlusUS, text="+V", style="Disab.TCheckbutton", variable=PlusUSEnab, command=BPlusOnOff)
    plusUSlab.pack(side=RIGHT)
    #
    NegUS = Frame( frame2r )
    NegUS.pack(side=TOP)
    negUSrb = Label(NegUS, text=" -5.00")
    negUSrb.pack(side=RIGHT)
    negUSEntry = Entry(NegUS, width=5)
    negUSEntry.bind("<Return>", BnegUS)
    negUSEntry.bind('<MouseWheel>', scrollNegUS)
    negUSEntry.bind('<Key>', onTextKey)
    negUSEntry.pack(side=RIGHT)
    negUSEntry.delete(0,"end")
    negUSEntry.insert(0,-5.0)
    negUSlab = Checkbutton(NegUS, text="-V", style="Disab.TCheckbutton", variable=NegUSEnab, command=BNegOnOff)
    negUSlab.pack(side=RIGHT)
#
#
def BnegUS(temp):
    global negUSEntry, NegUS, ctx, ad5627

    SetNegUS()
#
def BplusUS(temp):
    global plusUSEntry, PlusUS, ctx, ad5627

    SetPosUS()
#
def BPlusOnOff():
    global PlusUSEnab, UserPS, ctx, plusUSlab

    if PlusUSEnab.get() > 0:
        UserPS.enableChannel(0,True) # power up positive user supply
        SetPosUS()
        plusUSlab.config( style="Enab.TCheckbutton")
    else:
        UserPS.enableChannel(0,False) # power down positive user supply
        plusUSlab.config( style="Disab.TCheckbutton")
#
def BNegOnOff():
    global NegUSEnab, UserPS, ctx, negUSlab

    if NegUSEnab.get() > 0:
        UserPS.enableChannel(1,True) # power up negative user supply
        SetNegUS()
        negUSlab.config( style="Enab.TCheckbutton")
    else:
        UserPS.enableChannel(1,False) # power down negative user supply
        negUSlab.config( style="Disab.TCheckbutton")
#
def SetNegUS():
    global negUSEntry, UserPS, NegVolts, ctx, NegUS_RB

    if NegUSEnab.get() > 0:
        UserPS.enableChannel(1,True) # power up negative user supply
    else:
        UserPS.enableChannel(1,False) # power down negative user supply
    try:
        NegVolts = float(negUSEntry.get())
        if NegVolts > 0 :
            NegVolts = 0.0
            negUSEntry.delete(0,END)
            negUSEntry.insert(0, NegVolts)
        if NegVolts < -5.0:
            NegVolts = -5.0
            negUSEntry.delete(0,END)
            negUSEntry.insert(0, NegVolts)
    except:
        negUSEntry.delete(0,END)
        negUSEntry.insert(0, NegVolts)
    UserPS.pushChannel(1,NegVolts)# set value to volts
# Read back scaled values for user power supplies seem to be 500 too big?
    negrb_val = UserPS.readChannel(1)
    negrb_str = ' {0:.3f} '.format(negrb_val * -1)
    negUSrb.configure(text=negrb_str)
#
def SetPosUS():
    global plusUSEntry, PlusVolts, UserPS, ctx, PlusUS_RB, plusUSrb
    
    if PlusUSEnab.get() > 0:
        UserPS.enableChannel(0,True) # power up positive user supply
    else:
        UserPS.enableChannel(0,False)
    try:
        PlusVolts = float(plusUSEntry.get())
        if PlusVolts < 0 :
            PlusVolts = 0.0
            plusUSEntry.delete(0,END)
            plusUSEntry.insert(0, PlusVolts)
        if PlusVolts > 5.0:
            PlusVolts = 5.0
            plusUSEntry.delete(0,END)
            plusUSEntry.insert(0, PlusVolts)
    except:
        plusUSEntry.delete(0,END)
        plusUSEntry.insert(0, PlusVolts)
    UserPS.pushChannel(0,PlusVolts) # set positve user supply voltage
# Read back scaled values for user power supplies seem to be 500 too big?
    posrb_val = UserPS.readChannel(0)
    posrb_str = ' {0:.3f} '.format(posrb_val)
    plusUSrb.configure(text=posrb_str)
#
def scrollPlusUS(temp):

    onTextScroll(temp)
    SetPosUS()
#
def scrollNegUS(temp):

    onTextScroll(temp)
    SetNegUS()
#
