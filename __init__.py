# -*- coding: utf-8 -*-
from aqt import mw
from aqt.qt import *

from .dumps import Dumps
from .anki import Anki
from .counters import Counters
from .transformer import Transformer

Counters.resetCounters()

def doLogging():
    Dumps.logStats('D:/Japanese/jap_anki/logs/log_counts.txt')
    Dumps.logKanjis('D:/Japanese/jap_anki/dumps/kanjis_ivl.txt')
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

def addActionMenu(text, function):
    action = QAction(text, mw)
    action.triggered.connect(function)
    mw.form.menuTools.addAction(action)

addActionMenu("==> Do everything", doRoutine)
addActionMenu("> Import files", Transformer.importInBothFiles)
addActionMenu("> Reset decks", Anki.resetDecks)
addActionMenu("> Force logging", doLogging)
