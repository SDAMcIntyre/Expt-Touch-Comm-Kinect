import time

import serial

from libraries.triggerbox import TriggerBox

# Interact with arduino connected through USB port


class ArduinoComm:

    def __init__(self):
        self.trigger = TriggerBox()
        self.pulse = self.trigger.make_analog_signal(channel=3, voltage=5, duration=20)  # in ms
        self.running = self.trigger.make_analog_signal(channel=3, voltage=5, duration=0)  # infinite
        self.stop = self.trigger.make_analog_signal(channel=3, voltage=0, duration=0)  # infinite

        self.trigger.ser.write(self.stop)

    def send_pulses(self, nb_pulse):

        for current_pulse in range(1, nb_pulse):
            self.trigger.ser.write(self.pulse)
            time.sleep(0.040)  # Sleep for 20 milliseconds

        self.trigger.ser.write(self.running)

        return self

    def stop_recording(self):
        self.trigger.ser.write(self.stop)

        return self





