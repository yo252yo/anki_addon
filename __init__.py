# -*- coding: utf-8 -*-
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

from .dumps import Dumps
from .anki import Anki
from .counters import Counters
from .transformer import Transformer

Counters.resetCounters()

def doLogging():
    Dumps.logStats('D:/Japanese/jap_anki/logs/log_counts.txt')
    Dumps.logKanjis('D:/Japanese/jap_anki/dumps/anki_kanjis_ivl.txt')
    Dumps.logCounters('D:/Japanese/jap_anki/logs/log.txt')


def doRoutine():
  mw.onSync()
  mw.progress.start(immediate=True)
  Counters.resetCounters()
  Transformer.importInBothFiles()
  Anki.resetDecks()
  mw.progress.finish()
  mw.onSync()
  doLogging()
  Counters.show()
  Counters.sanityCheck()

def doRoutineVerbose():
    Transformer.VERBOSE = True
    showInfo("Sync")
    mw.onSync()
    showInfo("Counters")
    Counters.resetCounters()
    showInfo("Import")
    Transformer.importInBothFiles()
    showInfo("Reset decks")
    Anki.resetDecks()
    showInfo("Sync2")
    mw.onSync()
    showInfo("logging")
    doLogging()
    Counters.show()
    Counters.sanityCheck()

def addActionMenu(text, function):
    action = QAction(text, mw)
    action.triggered.connect(function)
    mw.form.menuTools.addAction(action)

addActionMenu("==> Do everything", doRoutine)
addActionMenu("==> Do everything (verbose)", doRoutineVerbose)
addActionMenu("> Import files", Transformer.importInBothFiles)
addActionMenu("> Reset decks", Anki.resetDecks)
addActionMenu("> Force logging", doLogging)
