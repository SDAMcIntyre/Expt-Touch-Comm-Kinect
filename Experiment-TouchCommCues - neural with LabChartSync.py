import psychopy
psychopy.useVersion('1.83.04')
from psychopy import visual, core, event, data, gui, parallel
import numpy as np
import random, os, pygame, serial, time
from touchcomm import *

os.chdir(os.path.dirname(os.path.realpath(__file__)))

# -- GET INPUT FROM THE EXPERIMENTER --

exptInfo = {'01. Participant Code':'PA',
            '02. Number of repeats':3,
            '03. Press to continue':False,
            '04. Screen':0,
            '05. Screen resolution':'800,600', #'1280,720',
            '06. Arduino serial port':'COM3',
            '07. Folder for saving data':'data'}
exptInfo['08. Date and time']= data.getDateStr(format='%Y-%m-%d_%H-%M-%S') ##add the current time

dlg = gui.DlgFromDict(exptInfo, title='Experiment details', fixed=['08. Date and time'])
if dlg.OK:
    pass ## continue
else:
    core.quit() ## the user hit cancel so exit

toucherScreenRes = [int(i) for i in exptInfo['05. Screen resolution'].split(',')]

# ----


# -- SETUP STIMULUS RANDOMISATION AND CONTROL --

items = ['attention','gratitude','love','sadness','happiness','calming']

stimList = []
for cue in items: stimList.append({'cue':cue})
trials = data.TrialHandler(stimList, exptInfo['02. Number of repeats'])
trials.data.addDataType('response')
correctText = ['incorrect','correct']

# ----

# -- MAKE FOLDER/FILES TO SAVE DATA --

dataFolder = './'+exptInfo['07. Folder for saving data']+'/'
if not os.path.exists(dataFolder):
    os.makedirs(dataFolder)

fileName = dataFolder + 'touch-comm-MNG_' + exptInfo['08. Date and time'] +'_neural_P' + exptInfo['01. Participant Code']
infoFile = open(fileName+'_info.csv', 'w') 
for k,v in exptInfo.items(): infoFile.write(k + ',' + str(v) + '\n')
infoFile.close()
dataFile = open(fileName+'_communication-data.csv', 'w')
dataFile.write('trial,cued\n')
logFile = open(fileName+'_log.csv', 'w')
logFile.write('time,event\n')

# ----

# -- SETUP INTERFACE --

outlineColour = [-1,-1,-1]
textColour = [-1,-1,-1]
startMessage = 'Press Space to start.'
continueMessage = 'Press space for the next cue.'
touchMessage = 'Follow the audio cue.'
finishedMessage = 'The session has finished. Thank you!'

toucherWin = visual.Window(fullscr = False, 
                            allowGUI = False, 
                            screen = exptInfo['04. Screen'],
                            size = toucherScreenRes)

toucherMessage = visual.TextStim(toucherWin,
                                    text = '',
                                    height = 0.15,
                                    color = textColour,
                                    units = 'norm',
                                    pos = (0,-0))


# -----

# -- SETUP AUDIO --

pygame.mixer.pre_init() 
pygame.mixer.init()
thisCue = pygame.mixer.Sound('./sounds/attention - short.wav')
goStopCue = pygame.mixer.Sound('./sounds/go-stop.wav')
# durations within the audio file:
silentLead = 0.064
countDownDuration = 3.0
stopDuration = 0.434

# ----


# -- make serial connection to arduino --

arduino = serial.Serial(exptInfo['06. Arduino serial port'],9600,timeout = 0.05)
ping(arduino,True)

# --


# -- RUN THE EXPERIMENT --

exptClock=core.Clock()
exptClock.reset()

# wait for start trigger
toucherMessage.text = startMessage
toucherMessage.autoDraw = True
event.clearEvents()
toucherWin.flip()
startTriggerReceived = False
while not startTriggerReceived:
    toucherWin.flip()
    for (key,keyTime) in event.getKeys(['space','escape'], timeStamped=exptClock):
        if key in ['escape']:
            logEvent(keyTime,'experiment aborted',logFile)
            dataFile.close(); logFile.close(); core.quit()
        if key in ['space']:
            exptClock.add(keyTime)
            logEvent(0,'experiment started',logFile)
            startTriggerReceived = True

# start the experiment
for thisTrial in trials:
    
    # get the cue for this trial
    thisCue = pygame.mixer.Sound('./sounds/{} - short.wav' .format(thisTrial['cue']))
    
    # wait for experimenter
    if trials.thisN == 0 or not exptInfo['03. Press to continue']:
        continuePressed = True
        core.wait(2)
    else:
        continuePressed = False
        toucherMessage.text = continueMessage
        toucherMessage.autoDraw = True
        event.clearEvents()
        toucherWin.flip()
    while not continuePressed:
        toucherWin.flip()
        for (key,keyTime) in event.getKeys(['space','escape'], timeStamped=exptClock):
            if key in ['escape']:
                logEvent(keyTime,'experiment aborted',logFile)
                dataFile.close(); logFile.close(); core.quit()
            if key in ['space']:
                logEvent(keyTime,'experimenter pressed for cue',logFile)
                continuePressed = True
    
    # cue toucher to perform touch
    toucherMessage.text = touchMessage
    event.clearEvents()
    toucherWin.flip()
    logEvent(exptClock.getTime(),'toucher cue {}' .format(thisTrial['cue']),logFile)
    soundCh = thisCue.play()
    while soundCh.get_busy():
        for (key,keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            soundCh.stop()
            logEvent(keyTime,'experiment aborted',logFile)
            dataFile.close(); logFile.close(); core.quit()
    
    signalNo = items.index(thisTrial['cue'])
    send_signal(arduino,signalNo,True);
    countDownStartTime = exptClock.getTime()
    soundCh = goStopCue.play()
    logEvent(countDownStartTime + silentLead,'countdown to touch',logFile)
    logEvent(countDownStartTime + silentLead + countDownDuration,'start touching',logFile)
    while soundCh.get_busy():
        for (key,keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            soundCh.stop()
            logEvent(keyTime,'experiment aborted',logFile)
            dataFile.close(); logFile.close(); core.quit()
    logEvent(exptClock.getTime() - stopDuration,'stop touching',logFile)
    
    
    dataFile.write('{},{}\n' .format(trials.thisN+1,thisTrial['cue']))
    logEvent(exptClock.getTime(),'{} of {} complete' .format(trials.thisN+1, trials.nTotal),logFile)

# -----

# prompt at the end of the experiment
toucherMessage.text = finishedMessage
event.clearEvents()
toucherMessage.draw()
logEvent(exptClock.getTime(),'experiment finished',logFile)
toucherWin.flip()
core.wait(2)
dataFile.close(); logFile.close()
toucherWin.close()
core.quit()
