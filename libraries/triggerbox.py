import serial
import os
import sys
import time
import serial
import serial.tools.list_ports
# working with bytes https://www.devdungeon.com/content/working-binary-data-python 
# https://stackoverflow.com/questions/53214304/python-pyserial-auto-detect-com-ports
BAUDRATE = 9600
# BAUDRATE = 1200

class TriggerBox():
    def __init__(self):      
        # start character for all trigger box commands, according to documentation
        self.startCharacter = 'S'.encode('utf-8')
        
        # auto-detect trigger box on serial port
        print('Connecting to trigger box...')
        connected = False
        ports = serial.tools.list_ports.comports(include_links=False)
        for port in ports :
            print('Checking port '+ port.device)
            try:
                ser = serial.Serial(port.device)
                if ser.isOpen():
                    print("closing",port.device)
                    ser.close()
                self.ser = serial.Serial(port.device, BAUDRATE, timeout=0.5)
                # self.ser = serial.Serial('COM8', BAUDRATE, timeout=0.5)
                self.ser.flushInput()
                self.ser.flushOutput()
                testwrite = self.make_digital_signal(channel = 1, message = 'T', duration = 0)
                self.ser.write(testwrite)
                testmessage = self.ser.readline().decode('utf-8')
                print("Response:", testmessage[-1])
                if testmessage[-1] == 'T':
                    connected = True
                    print('Triggerbox connected to ' + ser.name)
                    break
            except:
                print("Problem with",port.device)
        if not connected: print('Could not find trigger box. Is it plugged in?')
    
    def make_digital_signal(self, channel, message, duration):
        '''
        channel = the digital channel to send the signal on (1: USB back to this computer, 2: DSUB-9)
        message = the byte to send, 0-255 or a single character
        duration = 10 - 655350 ms in 10 ms steps; 0 means infinite
        '''
        # construct a command according to trigger box documentation
        commandNumber = 1
        ms_div10 = int(duration/10)
        time_bytes = ms_div10.to_bytes(2, byteorder='big', signed=True)
        command = bytearray(self.startCharacter)
        for i in [commandNumber, channel, message]:
            if type(i) == int:
                command.extend(i.to_bytes(1,'big', signed=True))
            elif type(i) == str:
                command.extend(i.encode('utf-8'))
        command.extend(time_bytes)

        # return the command without sending it
        return(command)
    
    def make_analog_signal(self, channel, voltage, duration):
        '''
        channel = the analog BNC channel to send the signal on (3-7)
        voltage = 0 - 5 V in 0.1 V steps
        duration = 10 - 655350 ms in 10 ms steps; 0 means infinite
        '''
        # construct a command according to trigger box documentation
        commandNumber = 2
        outputLevel = int(voltage*10)
        ms_div10 = int(duration/10)
        time_bytes = ms_div10.to_bytes(2, byteorder='big', signed=True)
        command = bytearray(self.startCharacter)
        for i in [commandNumber, channel, outputLevel]:
            command.extend(i.to_bytes(1,'big', signed=True))
        command.extend(time_bytes)

        # return the command without sending it
        return(command)

    def make_winsc_signal(self):
        commandNumber = 4
        command = bytearray(self.startCharacter)
        for i in [commandNumber,0,0,0,0]:
            command.extend(i.to_bytes(1,'big', signed=True))
        # return the command without sending it
        return(command)
        
    def make_cancel_signal(self, channel):
        '''
        cancel a previously activated trigger on a given channel (1-7)
        '''
        # construct a command according to trigger box documentation
        commandNumber = 3
        command = bytearray(self.startCharacter)
        for i in [commandNumber, channel, 0, 0, 0]:
            command.extend(i.to_bytes(1,'big', signed=True))       

        # return the command without sending it
        return(command)
        