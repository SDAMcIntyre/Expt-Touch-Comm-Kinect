
import os

from psychopy import core, data, event

from libraries.triggerbox import TriggerBox

from modules.arduino_comm import ArduinoComm
from modules.kinect_comm import KinectComm
from modules.audio_management import AudioManager
from modules.ui_management import UserInterfaceExpt, ui_get_initialData
from modules.file_management import FileManager
from modules.touch_stimuli_management import TouchStimuli

os.chdir(os.path.dirname(os.path.realpath(__file__)))

# -- GET INPUT FROM THE EXPERIMENTER --
exptInfo = {'01. Participant Code': 'ST01',
            '02. Number of repeats': 30,
            '03. Press to continue': False,
            '04. Screen': 0,
            '05. Screen resolution': '800,600',
            '06. Arduino serial port': 'COM3',
            '07. Folder for saving data': 'data',
            '08. Date and time': data.getDateStr(format='%Y-%m-%d_%H-%M-%S')}
exptInfo = ui_get_initialData(exptInfo)

# -- SETUP STIMULUS RANDOMISATION AND CONTROL --
items = ['attention', 'gratitude', 'love', 'sadness', 'happiness', 'calming']
nb_repeat = exptInfo['02. Number of repeats']
correctText = ['incorrect', 'correct']
stimuli = TouchStimuli(items, nb_repeat, correctText)

# -- MAKE FOLDER/FILES TO SAVE DATA --
dataFolder = exptInfo['07. Folder for saving data']
datetime = exptInfo['08. Date and time']
participant_id = exptInfo['01. Participant Code']
experimentName = 'touch-comm-MNG'
fm = FileManager(dataFolder, datetime, experimentName, participant_id)
fm.generate_infoFile(exptInfo)

# -- SETUP INTERFACE --
toucherScreenRes = [int(i) for i in exptInfo['05. Screen resolution'].split(',')]
ui = UserInterfaceExpt(exptInfo['04. Screen'], toucherScreenRes)

# -- SETUP AUDIO --
folderName = "sounds"
am = AudioManager(folderName)

# -- SETUP TRIGGER BOX CONNECTION --
#tb = TriggerBox(exptInfo['06. Arduino serial port'])

# -- SETUP KINECT CONNECTION --
kinectFilesName = exptInfo['08. Date and time'] + '_' + exptInfo['01. Participant Code'] + '_'
scriptPath = r'C:\Program Files\Azure Kinect SDK v1.2.0\tools'
outputDirectory = r'C:\Program Files\Azure Kinect SDK v1.2.0\tools\data'
#outputDirectory = r'D:\data'
kinect = KinectComm(scriptPath, outputDirectory)



# -- RUN THE EXPERIMENT --
exptClock = core.Clock()
exptClock.reset()
ui.display_start()

# wait for the experimenter to start the experiment
startTriggerReceived = False
while not startTriggerReceived:
    for (key, keyTime) in event.getKeys(['space', 'escape'], timeStamped=exptClock):
        if key in ['escape']:
            fm.abort(keyTime)
            core.quit()
        if key in ['space']:
            exptClock.add(keyTime)
            fm.logEvent(0, 'experiment started')
            startTriggerReceived = True


# run the trials
for thisTrial in stimuli.trials:

    # get the cue for this trial
    thisTrialCue = thisTrial['cue']
    thisTrialN = stimuli.trials.thisN
    # set the corresponding sound
    am.setSound(thisTrialCue)

    # wait for experimenter to start the sequence (safety step)
    if thisTrialN == 0 or not exptInfo['03. Press to continue']:
        continuePressed = True
        core.wait(2)
    else:
        continuePressed = False
        ui.display_continue()

    while not continuePressed:
        for (key, keyTime) in event.getKeys(['space', 'escape'], timeStamped=exptClock):
            if key in ['escape']:
                fm.abort(keyTime)
                core.quit()
            if key in ['space']:
                fm.logEvent(keyTime, 'experimenter pressed for cue')
                continuePressed = True

    # cue toucher to perform touch
    ui.display_touch()
    fm.logEvent(exptClock.getTime(), 'toucher cue {}'.format(thisTrialCue))
    soundCh = am.play()
    while soundCh.get_busy():
        for (key, keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            soundCh.stop()
            fm.abort(keyTime)
            core.quit()

    # start to execute the arduino task
    signalNo = items.index(thisTrialCue)
    #arduino.send_signal(signalNo, True)

    # start to record with the kinect
    kinect.start_recording(kinectFilesName + str(thisTrialN) + '_' + thisTrialCue)

    countDownStartTime = exptClock.getTime()
    soundCh = am.playStopCue()
    fm.logEvent(countDownStartTime + am.silentLead, 'countdown to touch')
    fm.logEvent(countDownStartTime + am.silentLead + am.countDownDuration, 'start touching')
    while soundCh.get_busy():
        for (key, keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            soundCh.stop()
            fm.abort(keyTime)
            core.quit()
    fm.logEvent(exptClock.getTime() - am.stopDuration, 'stop touching')
    fm.dataWrite(thisTrialN + 1, thisTrialCue)
    fm.logEvent(exptClock.getTime(), '{} of {} complete'.format(thisTrialN + 1, stimuli.trials.nTotal))

    kinect.stop_recording()

# end of the experiment
fm.end(exptClock.getTime())
ui.end()
core.quit()