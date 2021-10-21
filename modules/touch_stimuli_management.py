
from psychopy import data


class TouchStimuli:

    def __init__(self, _items, nb_repeat, _correctText):
        self.correctText = _correctText

        stimList = []
        for cue in _items:
            stimList.append({'cue': cue})
        self.trials = data.TrialHandler(stimList, nb_repeat)
        self.trials.data.addDataType('response')

        # number of pulse appearing in the trigger signal for each cue
        self.cue2pulse = {}
        item_id = 1
        for cue in _items:
            self.cue2pulse[cue] = item_id
            item_id += 1

    def get_nb_pulse(self, cue):
        return self.cue2pulse[cue]

    def shuffle_items(self):
        pass






