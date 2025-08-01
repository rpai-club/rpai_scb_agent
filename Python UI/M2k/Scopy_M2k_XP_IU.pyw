#
# Hardware specific interface functions
# For ADALM2000 aka M2k and Red M2k XPoint breadboards (8-1-2025)
# Written using Python version 3.10, Windows OS 
#
#
import __future__
import math
import time
#
try:
    import libm2k
    libm2k_found = True
except:
    root.update()
    showwarning("WARNING","libm2k not installed?!")
    root.destroy()
    exit()
#
import csv
import wave
import os
import sys
import struct
import subprocess
from time import gmtime, strftime
#
if sys.version_info[0] == 3:
    print ("Python 3.x")    
    import urllib.request, urllib.error, urllib.parse
    import tkinter
    from tkinter.font import *
    from tkinter import *
    from tkinter.ttk import *
    from tkinter.filedialog import askopenfilename
    from tkinter.filedialog import asksaveasfilename
    from tkinter.simpledialog import askstring
    from tkinter.messagebox import *
    from tkinter.colorchooser import askcolor
#
#
import webbrowser
#
# check which operating system
import platform
#
RevDate = "29 July 2025"
SWRev = "1.0 "
#
# small bit map of triangle logo for window icon
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""

root=Tk()
root.title("Scopy-M2k Cross Point Interfce " + SWRev + RevDate)
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, '-default', img)
print("Windowing System is " + str(root.tk.call('tk', 'windowingsystem')))
# Place holder for hardware functions file name:
# HardwareFile = "Alice_Interface_Level.py"
# ConfigFileName = "alice-last-config.cfg"
# ConfigFileName = "alice-last-config.cfg"
#
# adjust for your specific hardware by changing these values
#
FontSize = 8
BorderSize = 1
MouseX = MouseY = -10
MouseCAV = MouseCBV = MouseCCV = MouseCDV = -10
MouseFocus = 1
## Colors that can be modified Use function to reset to "factory" colors
def ResetColors():
    global COLORtext, COLORcanvas, COLORtrigger, COLORsignalband, COLORframes, COLORgrid, COLORzeroline, COLORdial
    global COLORtrace1, COLORtraceR1, COLORtrace2, COLORtraceR2, COLORtrace3, COLORtraceR3, COLORtrace4, COLORtraceR4
    global COLORtrace5, COLORtraceR5, COLORtrace6, COLORtraceR6, COLORtrace7, COLORtraceR7, COLORtrace8, COLORtraceR8
    
    COLORtext = "#ffffff"     # 100% white
    COLORtrigger = "#ff0000"  # 100% red
    COLORsignalband = "#ff0000" # 100% red
    COLORframes = "#000080"   # Color = "#rrggbb" rr=red gg=green bb=blue, Hexadecimal values 00 - ff
    COLORcanvas = "#000000"   # 100% black
    COLORgrid = "#808080"     # 50% Gray
    COLORzeroline = "#0000ff" # 100% blue
    COLORtrace1 = "#00ff00"   # 100% green
    COLORtrace2 = "#ff8000"   # 100% orange
    COLORtrace3 = "#00ffff"   # 100% cyan
    COLORtrace4 = "#ffff00"   # 100% yellow
    COLORtrace5 = "#ff00ff"   # 100% magenta
    COLORtrace6 = "#C80000"   # 90% red
    COLORtrace7 = "#8080ff"   # 100% purple
    COLORtrace8 = "#C8C8C8"     # 75% Gray
    COLORtraceR1 = "#008000"   # 50% green
    COLORtraceR2 = "#905000"   # 50% orange
    COLORtraceR3 = "#008080"   # 50% cyan
    COLORtraceR4 = "#808000"   # 50% yellow
    COLORtraceR5 = "#800080"   # 50% magenta
    COLORtraceR6 = "#800000"   # 80% red
    COLORtraceR7 = "#4040a0"  # 80% purple
    COLORtraceR8 = "#808080"  # 50% Gray
    COLORdial = "#404040"     # 25% Gray
#
ResetColors()
COLORwhite = "#ffffff" # 100% white
COLORblack = "#000000" # 100% black
ButtonGreen = "#00ff00"   # 100% green
ButtonRed = "#ff0000" # 100% red
GUITheme = "Light"
ButtonOrder = 0
SBoxarrow = 11
Closed = 0
ColorMode = IntVar()
# # Can be Light or Dark or Blue or LtBlue or Custom where:
FrameBG = "#d7d7d7" # Background color for frame
ButtonText = "#000000" # Button Text color
# Widget relief can be RAISED, GROOVE, RIDGE, and FLAT
ButRelief = RAISED
LabRelief = FLAT
FrameRelief = RIDGE
LocalLanguage = "English"
#
Wait = 0.001
PlusUSEnab = IntVar()
PlusUSEnab.set(1)
NegUSEnab = IntVar()
NegUSEnab.set(1)
RUNstatus = IntVar() # 0 stopped, 1 start, 2 running, 3 stop and restart, 4 stop
# 
#('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
# 'aqua' built-in native Mac OS X only; Native Mac OS X
windowingsystem = root.tk.call('tk', 'windowingsystem')
ScreenWidth = root.winfo_screenwidth()
ScreenHeight = root.winfo_screenheight()
# print(str(ScreenWidth) + "X" + str(ScreenHeight))
if (root.tk.call('tk', 'windowingsystem')=='aqua'):
    Style_String = 'aqua'
    # On Macs, allow the dock icon to deiconify.
    root.createcommand('::tk::mac::ReopenApplication', root.deiconify)
    root.createcommand('::tk::mac::Quit', root.destroy)# Bcloseexit)
    # On Macs, set up menu bar to be minimal.
    root.option_add('*tearOff', False)
    if sys.version_info[0] == 2:
        menubar = tKinter.Menu(root)
        appmenu = tKinter.Menu(menubar, name='apple')
    else:
        menubar = tkinter.Menu(root)
        appmenu = tkinter.Menu(menubar, name='apple')
    # menubar = tk.Menu(root)
    # appmenu = tk.Menu(menubar, name='apple')
    menubar.add_cascade(menu=appmenu)
    # appmenu.add_command(label='Exit', command=Bcloseexit)
    root['menu'] = menubar
else:
    Style_String = 'alt'
#
root.style = Style()
try:
    root.style.theme_use(Style_String)
except:
    root.style.theme_use('default')
if MouseFocus == 1:
    root.tk_focusFollowsMouse()
#
if sys.version_info[0] == 2:
    default_font = tkFont.nametofont("TkDefaultFont")
if sys.version_info[0] == 3:
    default_font = tkinter.font.nametofont("TkDefaultFont")
try:
    default_font.config(size=FontSize) # or .configure ?
except:
    print("Warning! Default Font Size was not set")
#
# shaded round button widgets
round_red = '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'
round_green = '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'
round_orange = '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'

if sys.version_info[0] == 3:
    RoundRedBtn = PhotoImage(data=round_red)
    RoundGrnBtn = PhotoImage(data=round_green)
    RoundOrBtn = PhotoImage(data=round_orange)
#
## Tool Tip Ballon help stuff
class CreateToolTip(object):
    ## create a tooltip for a given widget
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 100   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None
    ## Action when mouse enters
    def enter(self, event=None):
        self.schedule()
    ## Action when mouse leaves
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()
    ## Sehedule Action
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)
    ## Un-schedule Action
    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)
    ## Display Tip Text
    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                    background="#ffffe0", foreground="#000000",
                    relief='solid', borderwidth=1,
                    wraplength = self.wraplength)
        label.pack(ipadx=1)
    ## Hide Tip Action
    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()
    ## Re Configure text string
    def configure(self, text):
        self.text = text
#
# Converts a numeric string with "M" e6 or "k" e3 or "m" e-3 or "u" e-6
# to floating point number so calculations can be done on the user inputs
def UnitConvert(Value):
    
    Value = str.strip(Value,'V')
    Value = str.strip(Value,'s')
    if 'K' in Value:
        Value = str.strip(Value,'K') #
        Value = float(Value) * math.pow(10,3)
    elif 'k' in Value:
        Value = str.strip(Value,'k') #
        Value = float(Value) * math.pow(10,3)
    elif 'm' in Value:
        Value = str.strip(Value,'m') #
        Value = float(Value) * math.pow(10,-3)
    elif 'M' in Value:
        Value = str.strip(Value,'M') #
        Value = float(Value) * math.pow(10,6)
    elif 'u' in Value:
        Value = str.strip(Value,'u') #
        Value = float(Value) * math.pow(10,-6)
    elif 'n' in Value:
        Value = str.strip(Value,'n') #
        Value = float(Value) * math.pow(10,-9)
    else:
        Value = float(Value)
    return Value
# Take just integer part of digits
def UnitIntConvert(Value):
    
    Value = str.strip(Value,'V')
    Value = str.strip(Value,'s')
    if 'K' in Value:
        Value = str.strip(Value,'K') #
        Value = int(Value) * 1000
    elif 'k' in Value:
        Value = str.strip(Value,'k') #
        Value = int(Value) * 1000
    elif 'm' in Value:
        Value = str.strip(Value,'m') #
        Value = int(Value) * 0.001
    elif 'M' in Value:
        Value = str.strip(Value,'M') #
        Value = int(Value) * 1000000
    elif 'u' in Value:
        Value = str.strip(Value,'u') #
        Value = int(Value) * 0.000001
    elif 'n' in Value:
        Value = str.strip(Value,'n') #
        Value = int(Value) * 0.000000001
    else:
        Value = int(Value)
    return Value
## Nop
def donothing():
    global RUNstatus
## Another Nop
def DoNothing(event):
    global RUNstatus
#
# =========== Start widgets routines =============================
#

DevID = "M2k"

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
            NetList = open(nfp, 'r', encoding='utf-8') # encoding='utf-16-le'
        except:
            NetList = open(nfp, 'r', encoding='utf-16-le')
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
    global frame1, MatrixStatus, FileString, NumConn, RevDate, SWRev
    global CompString, JumperString, OnOffString, cpcl1, jpcl1
    global FrameBG, BorderSize, ErrConn
    global DCSr1String, DCSr2String, JumperSpinBoxList, CompSpinBoxList

    #
    #matrixwindow = Toplevel()
    #matrixwindow.title("Cross Point Interface " + SWRev + RevDate)
    #matrixwindow.geometry('+0+300')
    #matrixwindow.configure(background=FrameBG, borderwidth=BorderSize)
    #matrixwindow.protocol("WM_DELETE_WINDOW", DestroyMatrixScreen)
    #
    toplab = Label(frame1,text="Cross Point Interface ", style="A12B.TLabel")
    toplab.grid(row=0, column=0, columnspan=4, sticky=W)
    mcl1 = Label(frame1,text="Netlist File")
    mcl1.grid(row=1, column=0, sticky=W)
    FileString = Entry(frame1, width=50)
    FileString.bind("<Return>", ConfigCrossPoint)
    FileString.grid(row=2, column=0, columnspan=4, sticky=W)
    FileString.delete(0,"end")
    FileString.insert(0,"")
    NumConn = Label(frame1,text="Number of Connections ")
    NumConn.grid(row=3, column=0, columnspan=4, sticky=W)
    ErrConn = Label(frame1,text=" ")
    ErrConn.grid(row=4, column=0, columnspan=4, sticky=W)
    Browsebutton = Button(frame1, text="Browse", style="W8.TButton", command=BrowsNetFile)
    Browsebutton.grid(row=5, column=0, sticky=W, pady=8)
    #
    Sendbutton = Button(frame1, text="Send", style="W8.TButton", command=ConfigCrossPoint)
    Sendbutton.grid(row=5, column=1, sticky=W, pady=8)
    # 
    resetmxbutton = Button(frame1, text="Reset", style="W8.TButton", command=ResetMatrix)
    resetmxbutton.grid(row=5, column=2, sticky=W, pady=7)
    #
    cpcl1 = Label(frame1,text="Comp Pin")
    cpcl1.grid(row=6, column=0, sticky=W)
    jpcl1 = Label(frame1,text="Jumper")
    jpcl1.grid(row=6, column=1, sticky=W)
    oncl1 = Label(frame1,text="On/Off")
    oncl1.grid(row=6, column=2, sticky=W)
    #
    CompString = Spinbox(frame1, width=6, cursor='double_arrow', values=CompSpinBoxList)
    #Entry(frame1, width=7)
    CompString.bind("<Return>", ManualReturn)
    CompString.grid(row=7, column=0, columnspan=1, sticky=W)
    CompString.delete(0,"end")
    CompString.insert(0,"AWG1")
    JumperString = Spinbox(frame1, width=6, cursor='double_arrow', values=JumperSpinBoxList)
    #Entry(frame1, width=7)
    JumperString.bind("<Return>", ManualReturn)
    JumperString.grid(row=7, column=1, columnspan=1, sticky=W)
    JumperString.delete(0,"end")
    JumperString.insert(0,"JP1")
    OnOffString = Entry(frame1, width=2)
    OnOffString.bind("<Return>", ManualReturn)
    OnOffString.grid(row=7, column=2, columnspan=1, sticky=W)
    OnOffString.bind('<MouseWheel>', onTextScroll)# with Windows OS
    OnOffString.bind("<Button-4>", onTextScroll)# with Linux OS
    OnOffString.bind("<Button-5>", onTextScroll)
    OnOffString.delete(0,"end")
    OnOffString.insert(0,"0")
    Setbutton = Button(frame1, text="Set", style="W8.TButton", command=ManualMartix)
    Setbutton.grid(row=7, column=3, sticky=W, pady=8)
##  
def DestroyMatrixScreen():
    global frame1, MatrixStatus
    
    MatrixStatus.set(0)
    frame1.destroy()
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
            #aout.enableChannel(0, False)
            #aout.enableChannel(1, False)
            libm2k.contextClose(ctx) # deviceClose(ctx)
        except:
            print("closing anyway")
            # exit
    except:
        donothing()

    root.destroy()
    exit()
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
        # bcon.configure(text="Conn",  style="GConn.TButton")
        DevID = ctx.getContextAttributeValue('hw_serial')
        print(DevID)
        HWRev = ctx.getContextAttributeValue('hw_model')
        if "M2k" in HWRev:
            DevID = "M2k"
        print(HWRev)
        FWRev = ctx.getContextAttributeValue('fw_version')
        print(FWRev)
    
    # User power supply
        UserPS = ctx.getPowerSupply()

    # Digital Input / OutPut channels
        dig=ctx.getDigital()

        # dig.setSampleRateIn(10000)
        DigIOSetUp()
        # print(dev)
        # bcon.configure(text="Conn", style="GConn.TButton")
        # make cross point control screen
        MakeMatrixScreen()
        PlaceUSPower()
        time.sleep(0.01)
        BPlusOnOff() # Power up matrix chips
        BNegOnOff()
        time.sleep(0.01)
        ResetMatrix() # Reset all cross point switches to open
    #
        return(True) # return a logical true if sucessful!
    else:
        return(False)
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
##
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
def onTextScroll(event):   # Use mouse wheel to scroll entry values, august 7
    button = event.widget
    cursor_position = button.index(INSERT) # get current cursor position
    Pos = cursor_position
    OldVal = button.get() # get current entry string
    OldValfl = float(OldVal) # and its value
    NewVal = OldValfl
    Len = len(OldVal)
    Dot = OldVal.find (".")  # find decimal point position
    Decimals = Len - Dot - 1
    if Dot == -1 : # no point
        Decimals = 0             
        Step = 10**(Len - Pos)
    elif Pos <= Dot : # no point left of position
        Step = 10**(Dot - Pos)
    else:
        Step = 10**(Dot - Pos + 1)
    # respond to Linux or Windows wheel event
    if event.num == 5 or event.delta == -120:
        NewVal = OldValfl - Step
    if event.num == 4 or event.delta == 120:
        NewVal = OldValfl + Step
    FormatStr = "{0:." + str(Decimals) + "f}"
    NewStr = FormatStr.format(NewVal)
    NewDot = NewStr.find (".") 
    NewPos = Pos + NewDot - Dot
    if Decimals == 0 :
        NewLen = len(NewStr)
        NewPos = Pos + NewLen - Len
    button.delete(0, END) # remove old entry
    button.insert(0, NewStr) # insert new entry
    button.icursor(NewPos) # resets the insertion cursor
#
# Use Arr0w keys to inc dec entry values
#
def onTextKey(event):
    button = event.widget
    cursor_position = button.index(INSERT) # get current cursor position
    Pos = cursor_position
    OldVal = button.get() # get current entry string
    OldValfl = float(OldVal) # and its value
    Len = len(OldVal)
    Dot = OldVal.find (".")  # find decimal point position
    Decimals = Len - Dot - 1
    if Dot == -1 : # no point
        Decimals = 0             
        Step = 10**(Len - Pos)
    elif Pos <= Dot : # no point left of position
        Step = 10**(Dot - Pos)
    else:
        Step = 10**(Dot - Pos + 1)
    if platform.system() == "Windows":
        if event.keycode == 38: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 40: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return
    elif platform.system() == "Linux":
        if event.keycode == 111: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 116: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return
    elif platform.system() == "Darwin":
        if event.keycode == 0x7D: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 0x7E: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return
    else:
        return
#
    FormatStr = "{0:." + str(Decimals) + "f}"
    NewStr = FormatStr.format(NewVal)
    NewDot = NewStr.find (".") 
    NewPos = Pos + NewDot - Dot
    if Decimals == 0 :
        NewLen = len(NewStr)
        NewPos = Pos + NewLen - Len
    button.delete(0, END) # remove old entry
    button.insert(0, NewStr) # insert new entry
    button.icursor(NewPos) # resets the insertion cursor
#
def onSpinBoxScroll(event):
    spbox = event.widget
    if sys.version_info[0] == 3 and sys.version_info[1] > 6: # Spin Boxes do this automatically in Python > 3.6 apparently
        return
    if event.num == 4 or event.delta > 0: # if event.delta > 0: # increment digit
        spbox.invoke('buttonup')
    if event.num == 5 or event.delta < 0:
        spbox.invoke('buttondown')
##
def scrollPlusUS(temp):

    onTextScroll(temp)
    SetPosUS()
#
def scrollNegUS(temp):

    onTextScroll(temp)
    SetNegUS()
#
# ========================= Main routine ====================================
#
if GUITheme == "Light": # Can be Light or Dark or Blue or LtBlue
    FrameBG = "#d7d7d7"
    ButtonText = "#000000"
    COLORwhite = "#ffffff" # 100% white
    COLORblack = "#000000" # 100% black
if GUITheme == "Medium": #
    FrameBG = "#a8a8a8" #
    ButtonText = "#000000"
    COLORwhite = "#eeeeee" # white
    COLORblack = "#000000" # 100% black
elif GUITheme == "Dark":
    FrameBG = "#484848"
    ButtonText = "#ffffff"
    COLORwhite = "#000000" # 100% black
    COLORblack = "#ffffff" # 100% white
elif GUITheme == "Blue":
    FrameBG = "#242468"
    ButtonText = "#d0d0ff"
elif GUITheme == "LtBlue":
    FrameBG = "#c0e8ff"
    ButtonText = "#000040"
EntryText = "#000000"
BoxColor = "#0000ff" # 100% blue
if GUITheme == "Sun Valley Dark":
    if sv_ttk_found:
        sv_ttk.use_dark_theme()
        # sv_ttk.set_theme("dark") # ("light") or ("dark")
        #print("Setting ttk theme as dark")
        FrameBG = "#282828"
        ButtonText = "#cccccc"
        EntryText = "#cccccc"
        COLORwhite = "#000000" # 100% black
        COLORblack = "#d7d7d7" # Gray
    # 
elif GUITheme == "Sun Valley Light":
    if sv_ttk_found:
        sv_ttk.use_light_theme()
        # sv_ttk.set_theme("light") # ("light") or ("dark")
        #print("Setting ttk theme as dark")
    # 
root.style.configure("TFrame", background=FrameBG, borderwidth=BorderSize)
root.style.configure("TLabelframe", background=FrameBG)
root.style.configure("TLabel", foreground=ButtonText, background=FrameBG, relief=LabRelief)
root.style.configure("TEntry", foreground=EntryText, background=FrameBG, relief=ButRelief) #cursor='sb_v_double_arrow'
root.style.configure("TCheckbutton", foreground=ButtonText, background=FrameBG, indicatorcolor=FrameBG)
root.style.configure("TRadiobutton", foreground=ButtonText, background=FrameBG, indicatorcolor=FrameBG)
root.style.configure("TButton", foreground=ButtonText, background=FrameBG, highlightcolor=FrameBG, relief=ButRelief)
# define custom buttons and labels
root.style.configure("TSpinbox", arrowsize=SBoxarrow) # 11 only changes things in Python 3
root.style.configure("W3.TButton", width=3, relief=ButRelief)
root.style.configure("W4.TButton", width=4, relief=ButRelief)
root.style.configure("W5.TButton", width=5, relief=ButRelief)
root.style.configure("W6.TButton", width=6, relief=ButRelief)
root.style.configure("W7.TButton", width=7, relief=ButRelief)
root.style.configure("W8.TButton", width=8, relief=ButRelief)
root.style.configure("W9.TButton", width=9, relief=ButRelief)
root.style.configure("W10.TButton", width=10, relief=ButRelief)
root.style.configure("W11.TButton", width=11, relief=ButRelief)
root.style.configure("W16.TButton", width=16, relief=ButRelief)
root.style.configure("W17.TButton", width=17, relief=ButRelief)
root.style.configure("Stop.TButton", background=ButtonRed, foreground=COLORblack, width=4, relief=ButRelief)
root.style.configure("Run.TButton", background=ButtonGreen, foreground=COLORblack, width=4, relief=ButRelief)
root.style.configure("Pwr.TButton", background=ButtonGreen, foreground=COLORblack, width=8, relief=ButRelief)
root.style.configure("PwrOff.TButton", background=ButtonRed, foreground=COLORblack, width=8, relief=ButRelief)
root.style.configure("Roll.TButton", background=ButtonGreen, foreground=COLORblack, width=7, relief=ButRelief)
root.style.configure("RollOff.TButton", background=ButtonRed, foreground=COLORblack, width=8, relief=ButRelief)
root.style.configure("RConn.TButton", background=ButtonRed, foreground=COLORblack, width=5, relief=ButRelief)
root.style.configure("GConn.TButton", background=ButtonGreen, foreground=COLORblack, width=5, relief=ButRelief)
root.style.configure("Rtrace1.TButton", background=COLORtrace1, foreground=COLORblack, width=7, relief=RAISED)
root.style.configure("Strace1.TButton", background=COLORtrace1, foreground=COLORblack, width=7, relief=SUNKEN)
root.style.configure("Ctrace1.TButton", background=COLORtrace1, foreground=COLORblack, relief=ButRelief)
root.style.configure("Rtrace2.TButton", background=COLORtrace2, foreground=COLORblack, width=7, relief=RAISED)
root.style.configure("Strace2.TButton", background=COLORtrace2, foreground=COLORblack, width=7, relief=SUNKEN)
root.style.configure("Ctrace2.TButton", background=COLORtrace2, foreground=COLORblack, relief=ButRelief)
root.style.configure("Rtrace3.TButton", background=COLORtrace3, foreground=COLORblack, width=7, relief=RAISED)
root.style.configure("Strace3.TButton", background=COLORtrace3, foreground=COLORblack, width=7, relief=SUNKEN)
root.style.configure("Ctrace3.TButton", background=COLORtrace3, foreground=COLORblack, relief=ButRelief)
root.style.configure("Rtrace4.TButton", background=COLORtrace4, foreground=COLORblack, width=7, relief=RAISED)
root.style.configure("Strace4.TButton", background=COLORtrace4, foreground=COLORblack, width=7, relief=SUNKEN)
root.style.configure("Ctrace4.TButton", background=COLORtrace4, foreground=COLORblack, relief=ButRelief)
root.style.configure("Rtrace5.TButton", background=COLORtrace5, foreground=COLORblack, width=7, relief=RAISED)
root.style.configure("Rtrace6.TButton", background=COLORtrace6, foreground=COLORblack, width=7, relief=RAISED)
root.style.configure("Rtrace6.TButton", background=COLORtrace6, foreground=COLORblack, width=7, relief=RAISED)
root.style.configure("Rtrace7.TButton", background=COLORtrace7, foreground=COLORblack, width=7, relief=RAISED)
root.style.configure("Strace7.TButton", background=COLORtrace7, foreground=COLORblack, width=7, relief=SUNKEN)
root.style.configure("T1W16.TButton", background=COLORtrace1, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("T2W16.TButton", background=COLORtrace2, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("T3W16.TButton", background=COLORtrace3, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("T4W16.TButton", background=COLORtrace4, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("T5W16.TButton", background=COLORtrace5, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("T6W16.TButton", background=COLORtrace6, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("T7W16.TButton", background=COLORtrace7, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("TR1W16.TButton", background=COLORtraceR1, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("TR2W16.TButton", background=COLORtraceR2, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("TR3W16.TButton", background=COLORtraceR3, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("TR4W16.TButton", background=COLORtraceR4, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("TR5W16.TButton", background=COLORtraceR5, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("TR6W16.TButton", background=COLORtraceR6, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("TR7W16.TButton", background=COLORtraceR7, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("TGW16.TButton", background=COLORtrigger, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("ZLW16.TButton", background=COLORzeroline, foreground=COLORblack, width=16, relief=ButRelief)
root.style.configure("RGray.TButton", background="#808080", foreground=COLORblack, width=7, relief=RAISED)
root.style.configure("SGray.TButton", background="#808080", foreground=COLORblack, width=7, relief=SUNKEN)
#
root.style.configure("A10T5.TLabelframe.Label", background=FrameBG, foreground=COLORtraceR5, font=('Arial', 10, 'bold'))
root.style.configure("A10T5.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
root.style.configure("A10T6.TLabelframe.Label", background=FrameBG, foreground=COLORtrace6, font=('Arial', 10, 'bold'))
root.style.configure("A10T6.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
root.style.configure("A10T7.TLabelframe.Label", background=FrameBG, foreground=COLORtrace7, font=('Arial', 10, 'bold'))
root.style.configure("A10T7.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
#
root.style.configure("A10R1.TLabelframe.Label", background=FrameBG, foreground=COLORtraceR1, font=('Arial', 10, 'bold'))
root.style.configure("A10R1.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
root.style.configure("A10R2.TLabelframe.Label", background=FrameBG, foreground=COLORtraceR2, font=('Arial', 10, 'bold'))
root.style.configure("A10R2.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
root.style.configure("A10R6.TLabelframe.Label", background=FrameBG, foreground=COLORtraceR7, font=('Arial', 10, 'bold'))
root.style.configure("A10R6.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
root.style.configure("A10.TLabelframe.Label", background=FrameBG, font=('Arial', 10, 'bold'))
root.style.configure("A10.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
root.style.configure("A10B.TLabel", foreground=ButtonText, font="Arial 10 bold") # Black text
root.style.configure("A10R.TLabel", foreground=ButtonRed, font="Arial 10 bold") # Red text
root.style.configure("A10G.TLabel", foreground=ButtonGreen, font="Arial 10 bold") # Red text
root.style.configure("A12B.TLabel", foreground=ButtonText, font="Arial 12 bold") # Black text
root.style.configure("A16B.TLabel", foreground=ButtonText, font="Arial 16 bold") # Black text
root.style.configure("Stop.TRadiobutton", background=ButtonRed, indicatorcolor=FrameBG)
root.style.configure("Run.TRadiobutton", background=ButtonGreen, indicatorcolor=FrameBG)
root.style.configure("Disab.TCheckbutton", foreground=ButtonText, background=FrameBG, indicatorcolor=ButtonRed)
root.style.configure("Enab.TCheckbutton", foreground=ButtonText, background=FrameBG, indicatorcolor=ButtonGreen)
root.style.configure("Strace1.TCheckbutton", background=COLORtrace1, foreground=COLORblack, indicatorcolor=COLORwhite)
root.style.configure("Strace2.TCheckbutton", background=COLORtrace2, foreground=COLORblack, indicatorcolor=COLORwhite)
root.style.configure("Strace3.TCheckbutton", background=COLORtrace3, foreground=COLORblack, indicatorcolor=COLORwhite)
root.style.configure("Strace4.TCheckbutton", background=COLORtrace4, foreground=COLORblack, indicatorcolor=COLORwhite)
root.style.configure("Strace5.TCheckbutton", background=COLORtrace5, foreground=COLORblack, indicatorcolor=COLORwhite)
root.style.configure("Strace6.TCheckbutton", background=COLORtrace6, foreground=COLORblack, indicatorcolor=COLORwhite)
root.style.configure("Strace7.TCheckbutton", background=COLORtrace7, foreground=COLORblack, indicatorcolor=COLORwhite)
root.style.configure("WPhase.TRadiobutton", width=5, foreground=COLORblack, background="white", indicatorcolor=("red", "green"))
root.style.configure("GPhase.TRadiobutton", width=5, foreground=COLORblack, background="gray", indicatorcolor=("red", "green"))
# Custom left and right arrows
root.style.layout('Left1.TButton',[
                ('Button.focus', {'children': [
                    ('Button.leftarrow', None),
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'sticky': 'nswe'}
                         )]} )]} )] )

root.style.layout('Left2.TButton',[
                ('Button.focus', {'children': [
                    ('Button.leftarrow', None),
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'sticky': 'nswe'}
                         )]} )]} )] )

root.style.layout('Right1.TButton',[
                ('Button.focus', {'children': [
                    ('Button.rightarrow', None),
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'sticky': 'nswe'}
                         )]} )]} )] )

root.style.layout('Right2.TButton',[
                ('Button.focus', {'children': [
                    ('Button.rightarrow', None),
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'sticky': 'nswe'}
                         )]} )]} )] )

root.style.configure('Left1.TButton',font=('',FontSize,'bold'), width=7, arrowcolor='black', background='white', relief=LabRelief)
root.style.configure('Right1.TButton',font=('',FontSize,'bold'), width=7, arrowcolor='black', background='white', relief=LabRelief)
root.style.configure('Left2.TButton',font=('',FontSize,'bold'), width=6, arrowcolor='black')
root.style.configure('Right2.TButton',font=('',FontSize,'bold'), width=6, arrowcolor='black')
# 
# Create frames
frame2r = Frame(root, borderwidth=BorderSize, relief=FrameRelief)
frame2r.pack(side=RIGHT, fill=BOTH, expand=NO)

frame1 = Frame(root, borderwidth=BorderSize, relief=FrameRelief)
frame1.pack(side=TOP, fill=BOTH, expand=NO)

frame2 = Frame(root, borderwidth=BorderSize, relief=FrameRelief)
frame2.pack(side=TOP, fill=BOTH, expand=YES)

frame3 = Frame(root, borderwidth=BorderSize, relief=FrameRelief)
frame3.pack(side=TOP, fill=BOTH, expand=NO)

frame4 = Frame(root, borderwidth=BorderSize, relief=FrameRelief)
frame4.pack(side=TOP, fill=BOTH, expand=NO)

## Main Loop
#
def Analog_In():
    global RUNstatus

    while (Closed == 0):       # Main loop
        time.sleep(0.1)
        # Do input probe Calibration CH1VGain, CH2VGain, CH1VOffset, CH2VOffset
        # RUNstatus = 1 : Open Acquisition
        root.update_idletasks()
        root.update()
##
root.geometry('+300+0')
root.protocol("WM_DELETE_WINDOW", Bcloseexit)
# ===== Initalize device ======
# Try to connect to hardware
Sucess = ConnectDevice()
#
# ================ Call main routine ===============================
#
root.update() # Activate updated screens
# Start sampling
#
Analog_In()
