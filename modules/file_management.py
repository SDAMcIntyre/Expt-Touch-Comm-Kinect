
import os


class FileManager:

    def __init__(self, _dataFolder, _datetime, experimentName, _participant_ID):
        self.dataFolder = './' + _dataFolder + '/'
        if not os.path.exists(self.dataFolder):
            os.makedirs(self.dataFolder)

        # initialise files
        self.fileName_core = self.dataFolder + experimentName + '_' + _datetime + '_neural_P' + _participant_ID
        try:
            self.dataFile = open(self.fileName_core + '_communication-data.csv', 'w')
            self.dataFile.write('trial,cued\n')
        except IOError:
            input("Could not open" + self.fileName_core + '_communication-data.csv' + " file!")

        try:
            self.logFile = open(self.fileName_core + '_log.csv', 'w')
            self.logFile.write('time,event\n')
        except IOError:
            input("Could not open" + self.fileName_core + '_log.csv' + " file!")

    def generate_infoFile(self, exptInfo):
        infoFile = None
        try:
            infoFile = open(self.fileName_core + '_info.csv', 'w')
        except IOError:
            input("Could not open" + self.fileName_core + '_info.csv' + " file!")

        for k, v in exptInfo.items():
            infoFile.write(k + ',' + str(v) + '\n')
        infoFile.close()

        return self

    # def logEvent(time,event,logFile)
    # @brief: Write event with its time into logFile.
    def logEvent(self, time, event):
        self.logFile.write('{},{}\n'.format(time, event))
        print('LOG: {} {}'.format(time, event))

        return self

    def dataWrite(self, trial_id, trialCue):
        self.dataFile.write('{},{}\n'.format(trial_id, trialCue))

        return self

    def abort(self, keyTime):
        self.logEvent(keyTime, 'experiment aborted')
        self.dataFile.close()
        self.logFile.close()

        return self

    def end(self, time):
        self.logEvent(time, 'experiment finished')
        self.dataFile.close()
        self.logFile.close()
