# -*- coding: utf-8 -*-
from aqt import mw
from aqt.qt import *

from .dumps import Dumps
from .anki import Anki
from .counters import Counters
from .output import Output

Counters.resetCounters()

def doLogging():
    Dumps.logStats('D:/Japanese/jap_anki/logs/log_counts.txt')
    Dumps.logKanjis('D:/Japanese/jap_anki/dumps/kanjis_ivl.txt')
    Dumps.logCounters('D:/Japanese/jap_anki/logs/log.txt')


def doRoutine():
  mw.onSync()
  mw.progress.start(immediate=True)
  Counters.resetCounters()
  Output.importInReview()
  Output.importInNew()
  Anki.resetDecks()
  mw.progress.finish()
  mw.onSync()
  doLogging()
  Counters.show()
  Counters.sanityCheck()

def addActionMenu(text, function):
    action = QAction(text, mw)
    action.triggered.connect(function)
    mw.form.menuTools.addAction(action)

addActionMenu("==> Do everything", doRoutine)
addActionMenu("> Import in_review.txt", Output.importInReview)
addActionMenu("> Import in_new.txt", Output.importInNew)
addActionMenu("> Reset decks", Anki.resetDecks)
addActionMenu("> Force logging", doLogging)
