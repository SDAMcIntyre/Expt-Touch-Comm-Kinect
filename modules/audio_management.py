
import pygame


class AudioManager:
    # durations within the audio file:
    silentLead = 0.064
    countDownDuration = 3.0
    stopDuration = 0.434

    def __init__(self, folderName):
        pygame.mixer.pre_init()
        pygame.mixer.init()

        self.soundFileName_base = './' + folderName + '/'
        self.currentCue = pygame.mixer.Sound('./' + folderName + '/attention - short.wav')
        self.goStopCue = pygame.mixer.Sound('./' + folderName + '/go-stop.wav')


    def get_soundFileName(self, _type):
        return self.soundFileName_base + _type + ' - short.wav'

    def setSound(self, trialCue):
        self.currentCue = pygame.mixer.Sound(self.get_soundFileName(trialCue))

        return self

    def play(self):
        return self.currentCue.play()

    def playStopCue(self):
        return self.goStopCue.play()