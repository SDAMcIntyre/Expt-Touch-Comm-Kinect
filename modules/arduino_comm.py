
import serial

# Interact with arduino connected through USB port


class ArduinoComm:

    def __init__(self, _port):
        self.port = _port
        try:
            self.connArduino = serial.Serial(self.port, 9600, timeout=0.05)
            self.ping(True)
        except serial.SerialException:
            print("Port '{0}' not connected!".format(self.port))

    def ping(self, printMessages):
        arduinoSays = ''
        while not arduinoSays == 'ack':
            self.connArduino.write('ping'.encode('utf-8'))
            arduinoSays = self.connArduino.readline().decode('utf-8').strip()
            if printMessages and len(arduinoSays) > 0:
                print('arduino: {}' .format(arduinoSays))

        return arduinoSays

    def send_signal(self, signalNo, printMessages):
        arduinoSays = ''
        while not arduinoSays == 'signal':
            self.connArduino.write('signal'.encode('utf-8'))
            arduinoSays = self.connArduino.readline().decode('utf-8').strip()
            if printMessages and len(arduinoSays) > 0:
                print('arduino: {}' .format(arduinoSays))

        signalSent = False
        while not signalSent:
            self.connArduino.write(str(int(signalNo)).encode('utf-8'))
            arduinoSays = self.connArduino.readline().decode('utf-8').strip()
            if printMessages and len(arduinoSays) > 0:
                print('arduino: {}' .format(arduinoSays))
            if int(arduinoSays) == int(signalNo):
                signalSent = True

        return arduinoSays








