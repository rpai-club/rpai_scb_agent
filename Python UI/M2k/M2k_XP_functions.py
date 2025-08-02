#
# Hardware specific control functions
# For ADALM2000 aka M2k and Red M2k XPoint breadboards (7-15-2025)
# Written using Python version 3.10, Windows OS 
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
# Change these serial port pin numbers to match board layout
CSA = 7; CSB = 6; CSE = 5; CSC = 4; CSD = 3; RST = 2; DATA = 1; CLK = 0
#
# Cross point matrix functions
#
def ReadNetlist(nfp):
#
    try: # First check if net list is UTF-16-LE
        NetList = open(nfp, 'r', encoding='utf-16-le')     
        lines = NetList.readlines()
        print("Found file as UTF-16-LE")
    except: # If fails then must beUTF-8
        NetList.close()
        NetList = open(nfp, 'r', encoding='utf-8')
        lines = NetList.readlines()
        print("Found file as UTF-8")
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
##
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
##
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
##
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
        ctx=libm2k.m2kOpen()

        try:
            ProductName = ctx.getContextAttributeValue('usb,product')
        except:
            print('No Device plugged IN!')
            ProductName = "No Device"
            bcon.configure(text="Recon", style="RConn.TButton")
            return
        if ProductName != 'M2k (ADALM-2000)':
            print('M2K board not found!')
            print(ProductName, " Found")
            DevID = "No Device"
            bcon.configure(text="Recon", style="RConn.TButton")
            return
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
        # ctx.setTimeout(1000)
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
