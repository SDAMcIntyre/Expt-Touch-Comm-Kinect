import time

from libraries.triggerbox import TriggerBox
from psychopy import core

# Interact with arduino connected through USB port


class ArduinoComm:

    def __init__(self):
        self.trigger = TriggerBox()
        self.pulse_duration = 70 # in ms
        self.pulse = self.trigger.make_analog_signal(channel=3, voltage=5, duration=self.pulse_duration)  # in ms
        self.running = self.trigger.make_analog_signal(channel=3, voltage=5, duration=0)  # infinite
        self.stop = self.trigger.make_cancel_signal(channel=3)  # stop ch 3
        self.timer = core.Clock()

        self.trigger.ser.write(self.stop)

    def send_pulses(self, nb_pulse):

        for current_pulse in range(nb_pulse):
            self.timer.reset()
            self.trigger.ser.write(self.pulse)
            while self.timer.getTime() < self.pulse_duration/1000*2:
                pass

        #time.sleep(0.175)  # Sleep for 70 milliseconds

        self.trigger.ser.write(self.running)

        return self

    def stop_recording(self):
        self.trigger.ser.write(self.stop)

        return self





