import subprocess
import time
import signal
import psutil
import ctypes

from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE


def test_new_console(scriptPath, args):

    process = subprocess.Popen([scriptPath, args],
                               stdin=PIPE, bufsize=1, universal_newlines=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
    # creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

    time.sleep(10)
    process.wait()


if __name__ == '__main__':

    scriptPath = r'C:\Program Files\Azure Kinect SDK v1.2.0\tools\k4arecorder.exe'

    if 1:
        output = r'C:\Program Files\Azure Kinect SDK v1.2.0\tools\test2.mkv'
    else:
        output = ['test2.mkv', '-l 1']

    test_new_console(scriptPath, output)







def garbage():
    time.sleep(10)

    #p = psutil.Process(process.pid)
    #p.terminate()  #or p.kill()
    #process.communicate(b"0x03")
    #process.send_signal(signal.CTRL_C_EVENT)


    time.sleep(2)
    process.communicate()
    process.wait()
    process.terminate()

    #ctypes.windll.kernel32.TerminateProcess(int(process._handle), -1)

    #process.sendcontrol('c')
    #process.close()
