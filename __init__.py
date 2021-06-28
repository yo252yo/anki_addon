# -*- coding: utf-8 -*-
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

from .dumps import Dumps
from .anki import Anki
from .counters import Counters
from .cardmaker import CardMaker
from .importer import Importer

Counters.resetCounters()

def doLogging():
    Dumps.logStats('D:/Japanese/jap_anki/logs/log_counts.txt')
    Dumps.logKanjis('D:/Japanese/jap_anki/dumps/anki_kanjis_ivl.txt')
    Dumps.logCounters('D:/Japanese/jap_anki/logs/log.txt')


def doRoutine():
  mw.progress.start(immediate=True)
  mw.onSync()
  Counters.resetCounters()
  Importer.importInBothFiles()
  Anki.resetDecks()
  CardMaker.refreshAllDetails()
  mw.onSync()
  mw.progress.finish()
  doLogging()
  Counters.show()
  Counters.sanityCheck()

def doRoutineVerbose():
    Importer.VERBOSE = True
    CardMaker.VERBOSE = True
    showInfo("Sync")
    mw.onSync()
    showInfo("Counters")
    Counters.resetCounters()
    showInfo("Import")
    Importer.importInBothFiles()
    showInfo("Reset decks")
    Anki.resetDecks()
    showInfo("Refresh details")
    CardMaker.refreshAllDetails()
    showInfo("Sync2")
    mw.onSync()
    showInfo("logging")
    doLogging()
    Counters.show()
    Counters.sanityCheck()

def addActionMenu(text, function, menu=mw.form.menuTools):
    action = QAction(text, mw)
    action.triggered.connect(function)
    menu.addAction(action)


debugMenu = QMenu('Debug', mw)
mw.form.menuTools.addMenu(debugMenu)

addActionMenu("=> Full routine", doRoutine)

addActionMenu("=> Full routine (verbose)", doRoutineVerbose, debugMenu)
debugMenu.addSeparator()
addActionMenu("Import files", Importer.importInBothFiles, debugMenu)
addActionMenu("Reset decks", Anki.resetDecks)
addActionMenu("Force logging", doLogging, debugMenu)
addActionMenu("Sync", mw.onSync, debugMenu)
debugMenu.addSeparator()
addActionMenu("Update all Propernouns Details", CardMaker.updateDetailsOfProperNouns, debugMenu)
addActionMenu("Populate missing Details", CardMaker.populateMissingDeatils, debugMenu)
addActionMenu("Update All Details", CardMaker.refreshAllDetails, debugMenu)
