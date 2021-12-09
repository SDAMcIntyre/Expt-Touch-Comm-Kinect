import os
import time

from psychopy import core, data, event

from modules.arduino_comm import ArduinoComm
from modules.kinect_comm import KinectComm
from modules.audio_management import AudioManager
from modules.ui_management import UserInterfaceExpt, ui_get_initialData
from modules.file_management import FileManager
from modules.touch_stimuli_management import TouchStimuli

os.chdir(os.path.dirname(os.path.realpath(__file__)))

# -- GET INPUT FROM THE EXPERIMENTER --
exptInfo = {'01. Participant Code': 'ST10',
            '02. Unit Number': '0',
            '03. Number of repeats': 30,
            '04. Press to continue': False,
            '05. Screen': 0,
            '06. Screen resolution': '800,600',
            '07. Folder for saving data': 'data',
            '08. Date and time': data.getDateStr(format='%Y-%m-%d_%H-%M-%S')}
exptInfo = ui_get_initialData(exptInfo)

# -- SETUP STIMULUS RANDOMISATION AND CONTROL --
items = ['attention', 'gratitude', 'love', 'sadness', 'happiness', 'calming']
#items_nbPulse = [1, 2, 3, 4, 5, 6]
nb_repeat = exptInfo['03. Number of repeats']
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
toucherScreenRes = [int(i) for i in exptInfo['06. Screen resolution'].split(',')]
ui = UserInterfaceExpt(exptInfo['05. Screen'], toucherScreenRes)

# -- SETUP AUDIO --
folderName = "sounds"
am = AudioManager(folderName)

# -- SETUP TRIGGER BOX CONNECTION --
ac = ArduinoComm()

# -- SETUP KINECT CONNECTION --
scriptPath = r'C:\Program Files\Azure Kinect SDK v1.2.0\tools'
outputDirectory = r'C:\Program Files\Azure Kinect SDK v1.2.0\tools\data'
# outputDirectory = r'D:\data'
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
            ac.trigger.ser.write(ac.trigger.make_cancel_signal(3))
            ac.trigger.ser.close()
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
    thisTrialNbPulse = stimuli.get_nb_pulse(thisTrialCue)

    # set the corresponding sound
    am.setSound(thisTrialCue)

    # wait for experimenter to start the sequence (safety step)
    if thisTrialN == 0 or not exptInfo['04. Press to continue']:
        continuePressed = True
        core.wait(2)
    else:
        continuePressed = False
        ui.display_continue()

    while not continuePressed:
        for (key, keyTime) in event.getKeys(['space', 'escape'], timeStamped=exptClock):
            if key in ['escape']:
                fm.abort(keyTime)
                ac.trigger.ser.write(ac.trigger.make_cancel_signal(3))
                ac.trigger.ser.close()
                core.quit()
            if key in ['space']:
                fm.logEvent(keyTime, 'experimenter pressed for cue')
                continuePressed = True

    # start to record with the kinect
    kinectFilesName = (data.getDateStr(format='%Y-%m-%d_%H-%M-%S') + '_' +
                       exptInfo['01. Participant Code'] + '_' +
                       'unit' + exptInfo['02. Unit Number'] + '_' +
                       str(thisTrialN+1) + '_' + thisTrialCue)
    kinect_ct = time.time()
    kinect.start_recording(kinectFilesName)
    kinect_ct = (time.time() - kinect_ct)*1000
    fm.logEvent(exptClock.getTime(), 'start kinect consumes (ms): {}'.format(kinect_ct))
    core.wait(0.2) # 200 ms pause

    # cue toucher to perform touch
    ui.display_touch()
    fm.logEvent(exptClock.getTime(), 'toucher cue {}'.format(thisTrialCue))
    soundCh = am.play()
    while soundCh.get_busy():
        for (key, keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            soundCh.stop()
            fm.abort(keyTime)
            ac.trigger.ser.write(ac.trigger.make_cancel_signal(3))
            ac.trigger.ser.close()
            core.quit()

    countDownStartTime = exptClock.getTime()
    soundCh = am.playStopCue()
    # start to execute the arduino task
    ac.send_pulses(thisTrialNbPulse)

    fm.logEvent(countDownStartTime + am.silentLead, 'countdown to touch')
    fm.logEvent(countDownStartTime + am.silentLead + am.countDownDuration, 'start touching')

    while soundCh.get_busy():
        for (key, keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            soundCh.stop()
            fm.abort(keyTime)
            ac.trigger.ser.write(ac.trigger.make_cancel_signal(3))
            ac.trigger.ser.close()
            core.quit()
    fm.logEvent(exptClock.getTime() - am.stopDuration, 'stop touching')
    fm.dataWrite(thisTrialN + 1, thisTrialCue, thisTrialNbPulse)
    fm.logEvent(exptClock.getTime(), '{} of {} complete'.format(thisTrialN + 1, stimuli.trials.nTotal))

    # start to execute the arduino task
    ac.stop_recording()
    # ac.trigger.ser.write(ac.pulse)

    # stop recording
    kinect.stop_recording()


# end of the experiment
fm.end(exptClock.getTime())
ui.end()
ac.trigger.ser.write(ac.trigger.make_cancel_signal(3))
ac.trigger.ser.close()
core.quit()
