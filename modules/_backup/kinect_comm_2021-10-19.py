
import subprocess
from waiting import wait

# Interact with the Virginia's software


class KinectComm:

    def __init__(self, _location):
        scriptName = 'k4arecorder.exe'
        self.scripPath = _location + '\\' + scriptName
        self.process = None

    def start_recording(self, idVideo):
        videoName = idVideo + '.mkv'
        self.process = subprocess.Popen([self.scripPath, videoName],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        return self

    def stop_recording(self):
        self.process.sendcontrol('c')
        self.process.close()
        #self.process.terminate()
        #wait(self.is_stopped())

        return self

    def is_stopped(self):
        return self.process.poll() is None

    #import signal
    #self.p.send_signal(signal.CTRL_C_EVENT)





