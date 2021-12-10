
import subprocess
from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE
import keyboard
import time
from psychopy import data


# Interact with the Virginia's software


class KinectComm:

    def __init__(self, _locationScript, _outputDirectory):
        scriptName = 'k4arecorder.exe'
        self.scriptPath = _locationScript + '\\' + scriptName
        self.outputDir = _outputDirectory
        self.process = None

    def start_recording(self, idVideo):
        videoPath = self.outputDir + '\\' + idVideo + '.mkv'

        self.process = subprocess.Popen([self.scriptPath, videoPath],
                                        stdin=PIPE,
                                        stdout=PIPE,
                                        stderr=PIPE,
                                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        return self

    def stop_recording(self):

        time.sleep(2)
        keyboard.press_and_release('ctrl+c')
        self.process.wait()

        return self

    def is_stopped(self):
        return self.process.poll() is None

    # import signal
    # self.p.send_signal(signal.CTRL_C_EVENT)

    def record_trial(self, filename, duration):
        filename = (data.getDateStr(format='%Y-%m-%d_%H-%M-%S') + '_' + filename)
        self.start_recording(filename)
        time.sleep(duration)
        self.stop_recording()
        return self
