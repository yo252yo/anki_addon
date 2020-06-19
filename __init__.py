# -*- coding: utf-8 -*-
from aqt import mw
from aqt.qt import *

from .logs import Logs
from .anki import Anki
from .counters import Counters
from .output import Output

Counters.resetCounters()


def doRoutine():
  mw.onSync()
  mw.progress.start(immediate=True)
  Counters.resetCounters()
  Output.importInReview()
  Output.importInNew()
  Logs.logStats()
  Logs.logKanjis()
  Anki.resetDecks()
  mw.progress.finish()
  mw.onSync()
  Counters.printCounters()

def addActionMenu(text, function):
    action = QAction(text, mw)
    action.triggered.connect(function)
    mw.form.menuTools.addAction(action)

addActionMenu("=> Do everything", doRoutine)
addActionMenu("Import in_new.txt words", Output.importInNew)
addActionMenu("Import in_review.txt words", Output.importInReview)
addActionMenu("Import output", Output.importOutputFileToDeck)
addActionMenu("Reset decks", Anki.resetDecks)

addActionMenu("Log Stats", Logs.logStats)
addActionMenu("Log Kanjis", Logs.logKanjis)
