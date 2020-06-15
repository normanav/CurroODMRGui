import pyvisa
import time
import os
import numpy as np
import math
from struct import unpack
from collections import namedtuple
from spinapi_py_wrapper import *
path_name = "Z:/Zhipan/ODMR_system/codes/waveform/"
if not os.path.exists(path_name):
    os.makedirs(path_name)


PBchannel = namedtuple('PBchannel',['channelNumber','startTimes','pulseDurations'])
T_CLOCK = 10/3* ns
CYCLE = 5*T_CLOCK

class pbSequence:
    def __init__(self, T_L):
        self.tl = time_floor(T_L* ns)
        self.Laser_D = time_floor(424 * ns)
        self.Laser_R = time_floor(336 * ns)
        self.MW_D = time_floor(88 * ns)
        self.T_trigger = time_floor(1* us)
        return
    
    def testrun(self):
        Tl = self.tl* CYCLE
        T_trigger = self.T_trigger* CYCLE
        L_delay = (self.Laser_D + self.Laser_R)* CYCLE
        T_wait = Tl/10
        AOMchannel = PBchannel(1, [T_wait],[Tl])
        STARTtrigchannel = PBchannel(8, [0],[T_trigger])
        DAQchannel = PBchannel(4, [T_wait + L_delay + Tl/2],[T_trigger])
        return [AOMchannel, STARTtrigchannel, DAQchannel]
    
    def Rabi(self, t_mw, readout_D = 50*ns):
        Tl = self.tl* CYCLE
        T_trigger = self.T_trigger* CYCLE
        L_delay = (self.Laser_D + self.Laser_R)* CYCLE
        MW_delay = self.MW_D* CYCLE
        R_delay = time_floor(readout_D)* CYCLE
        T_startdelay = 1*us ## 60 cycles
        T_mw = time_floor(t_mw)* CYCLE
        
        T_first = MW_delay + T_mw + T_startdelay
        
        AOMchannel = PBchannel(1, [T_first, T_first*2 + Tl],[Tl, Tl])
        MWchannel = PBchannel(2, [T_startdelay],[T_trigger])
        DAQchannel = PBchannel(4, [T_first + L_delay + R_delay, T_first*2 + Tl + L_delay + R_delay],[T_trigger, T_trigger])
        STARTtrigchannel = PBchannel(8, [0],[T_trigger])
        return [AOMchannel, MWchannel, DAQchannel, STARTtrigchannel]
    
    def Ramsey(self, t_90, t_wait, readout_D = 50*ns):
        Tl = self.tl* CYCLE
        T_trigger = self.T_trigger* CYCLE
        L_delay = (self.Laser_D + self.Laser_R)* CYCLE
        MW_delay = self.MW_D* CYCLE
        R_delay = time_floor(readout_D)* CYCLE
        T_startdelay = 1*us ## 60 cycles
        T_mw = time_floor(t_90*2 + t_wait)* CYCLE
        
        T_first = MW_delay + T_mw + T_startdelay
        
        AOMchannel = PBchannel(1, [T_first, T_first*2 + Tl],[Tl, Tl])
        MWchannel = PBchannel(2, [T_startdelay],[T_trigger])
        DAQchannel = PBchannel(4, [T_first + L_delay + R_delay, T_first*2 + Tl + L_delay + R_delay],[T_trigger, T_trigger])
        STARTtrigchannel = PBchannel(8, [0],[T_trigger])
        return [AOMchannel, MWchannel, DAQchannel, STARTtrigchannel]

    def nCPMG(self, t_90, t_halftau, num, acqt = None, readout_D = 50*ns):
        if acqt is None:
            acqt = t_halftau
        Tl = self.tl* CYCLE
        T_trigger = self.T_trigger* CYCLE
        L_delay = (self.Laser_D + self.Laser_R)* CYCLE
        MW_delay = self.MW_D* CYCLE
        R_delay = time_floor(readout_D)* CYCLE
        T_startdelay = 1*us ## 60 cycles
        T_mw = time_floor((t_halftau*(2*num - 1) + acqt + 2*t_90*(num + 1))* ns)* CYCLE
        
        T_first = MW_delay + T_mw + T_startdelay
        
        AOMchannel = PBchannel(1, [T_first, T_first*2 + Tl],[Tl, Tl])
        MWchannel = PBchannel(2, [T_startdelay],[T_trigger])
        DAQchannel = PBchannel(4, [T_first + L_delay + R_delay, T_first*2 + Tl + L_delay + R_delay],[T_trigger, T_trigger])
        STARTtrigchannel = PBchannel(8, [0],[T_trigger])
        return [AOMchannel, MWchannel, DAQchannel, STARTtrigchannel]


    def nXY8(self, t_90, t_halftau, t_delay, num, acqt = None, readout_D = 50*ns):
        if acqt is None:
            acqt = t_halftau
        Tl = self.tl* CYCLE
        T_trigger = self.T_trigger* CYCLE
        L_delay = (self.Laser_D + self.Laser_R)* CYCLE
        MW_delay = self.MW_D* CYCLE
        R_delay = time_floor(readout_D)* CYCLE
        T_startdelay = 1*us ## 60 cycles
        T_mw = time_floor((t_halftau*(2*8*num - 1) + acqt + 2*t_90*(8*num + 1))* ns)* CYCLE
        
        T_first = MW_delay + T_mw + T_startdelay
        
        AOMchannel = PBchannel(1, [T_first, T_first*2 + Tl],[Tl, Tl])
        MWchannel = PBchannel(2, [T_startdelay],[T_trigger])
        DAQchannel = PBchannel(4, [T_first + L_delay + R_delay, T_first*2 + Tl + L_delay + R_delay],[T_trigger, T_trigger])
        STARTtrigchannel = PBchannel(8, [0],[T_trigger])
        return [AOMchannel, MWchannel, DAQchannel, STARTtrigchannel]

    def CASR_nXY8(self, t_90, t_halftau, t_delay, num, readout_D = 50*ns):
        ## t_delay is the time between 0 and MW trigger
        Tl = self.tl* CYCLE
        T_trigger = self.T_trigger* CYCLE
        L_delay = (self.Laser_D + self.Laser_R)* CYCLE
        MW_delay = self.MW_D* CYCLE
        R_delay = time_floor(readout_D)* CYCLE

        
        T_delay = time_floor(t_delay*ns)* CYCLE
        T_mw = time_floor((t_halftau*2*8*num + 2*t_90*(8*num + 1))* ns)* CYCLE

        T_first = MW_delay + T_mw + T_delay

        T_SR = 2*(T_first + Tl)

        Ndt = T_D_generator(T_SR)

        T_delay = T_delay + Ndt/2* CYCLE
        
        T_first = T_first + Ndt/2* CYCLE

        AOMchannel = PBchannel(1, [T_first, T_first*2 + Tl],[Tl, Tl])
        MWchannel = PBchannel(2, [T_delay],[T_trigger])
        DAQchannel = PBchannel(4, [T_first + L_delay + R_delay, T_first*2 + Tl + L_delay + R_delay],[T_trigger, T_trigger])
        STARTtrigchannel = PBchannel(8, [0],[T_trigger])
        return [AOMchannel, MWchannel, DAQchannel, STARTtrigchannel]



    def CASR_nXY8_no_calibration(self, t_90, t_halftau, t_delay, num, readout_D = 50*ns):
        ## t_delay is the time between DAC trigger and MW trigger
        Tl = self.tl* CYCLE
        T_trigger = self.T_trigger* CYCLE
        L_delay = (self.Laser_D + self.Laser_R)* CYCLE
        MW_delay = self.MW_D* CYCLE
        R_delay = time_floor(readout_D)* CYCLE
        
        T_delay = time_floor(t_delay*ns)* CYCLE
        T_mw = time_floor((t_halftau*2*8*num + 2*t_90*(8*num + 1))* ns)* CYCLE

        T_first = MW_delay + T_mw + T_delay

        T_SR = T_first + Tl

        Ndt = T_D_generator(T_SR)

        T_delay = T_delay + Ndt* CYCLE
        
        T_first = T_first + Ndt* CYCLE

        STARTtrigchannel = PBchannel(8, [0],[T_trigger])
        MWchannel = PBchannel(2, [T_delay],[T_trigger])
        AOMchannel = PBchannel(1, [T_first],[Tl])
        DAQchannel = PBchannel(4, [T_first + L_delay + R_delay],[T_trigger])
        return [AOMchannel, MWchannel, DAQchannel, STARTtrigchannel]

    def sequenceEventCataloguer(self, channels):
        #Catalogs sequence events in terms of consecutive rising edges on the channels provided. Returns a dictionary, channelBitMasks, whose keys are event (rising/falling edge) times and values are the channelBitMask which indicate which channels are on at that time.
        eventCatalog ={}
        #dictionary where the keys are rising/falling edge times and the values are the channel bit masks which turn on/off at that time
        for channel in channels:
            channelMask = channel.channelNumber
            endTimes = [startTime + pulseDuration for startTime, pulseDuration in zip(channel.startTimes,channel.pulseDurations)]
        ##what? sum every element in the list
            for eventTime in channel.startTimes+endTimes:
                eventChannelMask = channelMask
                if eventTime in eventCatalog.keys():
                    eventChannelMask = eventCatalog[eventTime]^channelMask 
                    #I'm XORing instead of ORing here in case someone has a zero-length pulse in the sequence. In that case, the XOR ensures that the channel does not turn on at the pulse start/end time. If we did an OR here, it would turn on and only turn off at the next event (which would have been a rising edge), so this would have given unexpected behaviour.
                eventCatalog[eventTime]=eventChannelMask
        channelBitMasks = {}
        currentBitMask=0
        channelBitMasks[0]=currentBitMask
        for event in sorted(eventCatalog.keys()):
            channelBitMasks[event]=currentBitMask^eventCatalog[event]
            currentBitMask = channelBitMasks[event]
        return channelBitMasks

    def programSequence(self, channelBitMasks):
        eventTimes = list(channelBitMasks.keys())
        ##print(eventTimes)
        numEvents = len(eventTimes)
        eventDurations =list(np.zeros(numEvents-1))
        ##print(eventDurations)
        numInstructions = numEvents-1
        for i in range(0,numInstructions):
            eventDurations[i] = eventTimes[i+1]-eventTimes[i]
        ##print(eventDurations)
        instructionArray = []
        bitMasks = list(channelBitMasks.values())
        start = [0]
        for i in range(0,numInstructions):
            if i==(numEvents-2):
                instructionArray.extend([[bitMasks[i] + 0xF00000, Inst.BRANCH, start[0], eventDurations[i]]])
            instructionArray.extend([[bitMasks[i] + 0xF00000, Inst.CONTINUE, 0, eventDurations[i]]])
    ##    instructionArray.extend([[0xF00000, Inst.BRANCH, start[0], 70 * us]])
    ##    print(instructionArray)
    
        #Program Pulseblaster
        pb_core_clock(300.0)
        pb_start_programming(PULSE_PROGRAM)
        startDone = False
        for i in range(0, len(instructionArray)):
            if startDone:
                pb_inst_pbonly(instructionArray[i][0],instructionArray[i][1],instructionArray[i][2],instructionArray[i][3])
    
            else:
                start[0] = pb_inst_pbonly(instructionArray[0][0],instructionArray[0][1],instructionArray[0][2],instructionArray[0][3])
                startDone = True
        pb_stop_programming()
        print("loading successful!!!")
        return instructionArray

    def plotSequence(self, instructions, channels):
        scalingFactor = 0.8
        t_ns = [0,0]
        pulses ={}
        tDone = False
        channelPulses=[]
        channelMasks = []
        for channel in channels:
            channelMasks.append(channel.channelNumber)
        for channelMask in channelMasks:
            pulses[channelMask]=[0,channelMask&instructions[0][0]]
            for i in range(0, len(instructions)):
                currentPulseLength = instructions[i][3]
                if not tDone:
                    previousEdgeTime = t_ns[-1]
                    nextEdgeTime = previousEdgeTime + currentPulseLength
                    t_ns.append(nextEdgeTime)
                    t_ns.append(nextEdgeTime)
                    if i == (len(instructions)-1):
                        tDone = True
                if i==len(instructions)-1:
                    pulses[channelMask].append(channelMask&instructions[i][0])
                    pulses[channelMask].append(channelMask&instructions[i][0])
                else:
                    pulses[channelMask].append(channelMask&instructions[i][0])
                    pulses[channelMask].append(channelMask&instructions[i+1][0])
            t_us = np.divide(t_ns,1e3)
            channelPulses.append(list(np.add(math.log(channelMask,2),np.multiply(list(pulses[channelMask]), \
            scalingFactor/channelMask))))
        dataArray = [t_us]
        for channelP in channelPulses:
            dataArray.append(channelP)
        dataArray = np.transpose(np.array(dataArray))
        np.savetxt(path_name + 'seq_diagram.txt' ,dataArray, delimiter=', ', comments='')
        print("Sequence diagram saved!!!")
        return


def time_floor(time):
    num = int(round(time/CYCLE, 1))
    print("{} cycle generated".format(num))
    return num

def T_D_generator(T_SR):
    current_num = int(round(T_SR/CYCLE,1))
    residue = np.mod(current_num, 20) ## mod 20 is because fixed AC frequency@3MHz. period is 20 cycles
    if residue != 0:
        NN = 20 - residue
        print("{} more cycles needed".format(NN))
        return NN
    else:
        return 0
    
