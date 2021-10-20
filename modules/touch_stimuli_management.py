
from psychopy import data


class TouchStimuli:

    def __init__(self, _items, nb_repeat, _correctText):
        self.correctText = _correctText

        stimList = []
        for cue in _items:
            stimList.append({'cue': cue})
        self.trials = data.TrialHandler(stimList, nb_repeat)
        self.trials.data.addDataType('response')

    def shuffle_items (self):
        pass






