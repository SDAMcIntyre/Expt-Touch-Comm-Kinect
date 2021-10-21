from psychopy import data, core, event, gui, visual


class UserInterfaceExpt:

    def __init__(self, screen_ID, screen_res):
        self.outlineColour = [-1, -1, -1]
        self.textColour = [-1, -1, -1]
        self.startMessage = 'Press Space to start.'
        self.continueMessage = 'Press space for the next cue.'
        self.touchMessage = 'Follow the audio cue.'
        self.finishedMessage = 'The session has finished. Thank you!'

        self.toucherWin = visual.Window(fullscr=False,
                                        allowGUI=False,
                                        screen=screen_ID,
                                        size=screen_res)
        self.toucherMessage = visual.TextStim(self.toucherWin,
                                              text='',
                                              height=0.15,
                                              color=self.textColour,
                                              units='norm',
                                              pos=(0, -0))
        self.fwd = ['a', 'down']
        self.bwd = ['b', 'up']
        self.conf = ['c', 'return']
        self.escape = ['escape']

    def display(self, message):
        self.toucherMessage.text = message
        self.toucherMessage.autoDraw = True
        event.clearEvents()
        self.toucherWin.flip()

    def display_start(self):
        self.display(self.startMessage)

        return self

    def display_continue(self):
        self.display(self.continueMessage)

        return self

    def display_touch(self):
        self.display(self.touchMessage)

        return self

    def display_finish(self):
        self.display(self.finishedMessage)

        return self

    # def getSelection(win,buttonList,timeout,clock)
    # @output: returns the selected option and time when validation is made.
    # @input :
    #   . win: psychopy.visual.Window object (user interface)
    #   . buttonList:
    #   . timeout: int variable (ttw before selection disappears)
    #   . clock: psychopy.core.Clock object (overall experiment duration)
    def getSelection(self, win, buttonList, timeout, clock):

        confirmed = False
        aborted = False
        buttonSelected = -1
        response = -1
        t = -1
        countDown = core.CountdownTimer(timeout)
        # countDown.add(timeout)

        while not aborted and not confirmed and countDown.getTime() > 0:
            for (key, t) in event.getKeys(self.fwd + self.bwd + self.conf + self.escape, timeStamped=clock):
                if key in self.fwd:
                    buttonList[buttonSelected].opacity = 1
                    buttonSelected = (buttonSelected + 1) % len(buttonList)
                    buttonList[buttonSelected].opacity = 0.3
                if key in self.bwd:
                    buttonList[buttonSelected].opacity = 1
                    if buttonSelected < 0:
                        buttonSelected = buttonSelected % len(buttonList)
                    else:
                        buttonSelected = (buttonSelected - 1) % len(buttonList)
                    buttonList[buttonSelected].opacity = 0.3
                if key in self.conf and buttonSelected >= 0:
                    buttonList[buttonSelected].opacity = 1
                    response = buttonSelected
                    confirmed = True
                if key in self.escape:
                    buttonList[buttonSelected].opacity = 1
                    response = -2
                    aborted = True
                win.flip()
        if countDown.getTime() <= 0: t = clock.getTime()
        buttonList[buttonSelected].opacity = 1
        win.flip()

        return response, t

    def end(self):
        self.display_finish()
        core.wait(2)  # display the end message for 2 seconds
        self.toucherWin.close()

        return self



def ui_get_initialData(exptInfo):
    dlg = gui.DlgFromDict(exptInfo, title='Experiment details', fixed=['08. Date and time'])

    # update the time when the user pressed enter:
    exptInfo['09. Date and time'] = data.getDateStr(format='%Y-%m-%d_%H-%M-%S')
    if dlg.OK:
        pass  # continue
    else:
        core.quit()  # the user hit cancel so exit

    return exptInfo
