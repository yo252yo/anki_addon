# -*- coding: utf-8 -*-
from aqt import AnkiQt, mw
from aqt.qt import *
#from aqt.qt import QMessageBox
from aqt.utils import showInfo
from anki.hooks import wrap

from .dumps import Dumps
from .anki import Anki
from .counters import Counters
from .cardmaker import CardMaker
from .studyImporter import StudyImporter
from .kanjiImporter import KanjiImporter

Counters.resetCounters()

def doLogging():
    Dumps.logStats('D:/Japanese/jap_anki/logs/log_counts.txt')
    Dumps.logCounters('D:/Japanese/jap_anki/logs/log.txt')
    Dumps.logKanjis('D:/Japanese/jap_anki/dumps/anki_kanjis_ivl.txt')
    Dumps.logKeywords('D:/Japanese/jap_anki/dumps/keywords.txt')


def doRoutine():
  mw.onSync()
  Counters.resetCounters()
  Anki.changeDeckCanWrite()
  StudyImporter.importInBothFiles()
  KanjiImporter.importKanjis()
  Anki.rescheduleLatestKanjis()
  KanjiImporter.importKanjisSim()
  Anki.resetDecks()
  CardMaker.updateAllDetails()
  CardMaker.refreshDetailsForLastKanji()
  mw.onSync()
  doLogging()
  Counters.show()
  Counters.sanityCheck()

def doRoutineVerbose():
    StudyImporter.VERBOSE = True
    CardMaker.VERBOSE = True
    showInfo(">>> Sync")
    mw.onSync()
    showInfo(">>> Counters")
    Counters.resetCounters()
    showInfo(">>> Adjust can write")
    Anki.changeDeckCanWrite()
    showInfo(">>> Import study files")
    StudyImporter.importInBothFiles()
    showInfo(">>> Import kanjis")
    KanjiImporter.importKanjis()
    showInfo(">>> Reschedule latest kanjis")
    Anki.rescheduleLatestKanjis()
    showInfo(">>> Import kanjis sim")
    KanjiImporter.importKanjisSim()
    showInfo(">>> Reset decks")
    Anki.resetDecks()
    showInfo(">>> Update details")
    CardMaker.updateAllDetails()
    showInfo(">>> Refresh details for last kanji")
    CardMaker.refreshDetailsForLastKanji()
    showInfo(">>> Sync2")
    mw.onSync()
    showInfo(">>> logging")
    doLogging()
    Counters.show()
    Counters.sanityCheck()

def addActionMenu(text, function, menu=mw.form.menuTools):
    action = QAction(text, mw)
    action.triggered.connect(function)
    menu.addAction(action)


debugMenu = QMenu('YoAnki', mw)
mw.form.menuTools.addMenu(debugMenu)

addActionMenu("=> Full routine", doRoutine, debugMenu)
addActionMenu("=> Full routine (verbose)", doRoutineVerbose, debugMenu)
debugMenu.addSeparator()
addActionMenu("Import study files", StudyImporter.importInBothFiles, debugMenu)
addActionMenu("Import kanjis", KanjiImporter.importKanjis, debugMenu)
addActionMenu("Import kanjis sim", KanjiImporter.importKanjisSim, debugMenu)
debugMenu.addSeparator()
addActionMenu("Reset decks", Anki.resetDecks, debugMenu)
addActionMenu("CanWrite", Anki.changeDeckCanWrite, debugMenu)
addActionMenu("Reschedule latest kanjis", Anki.rescheduleLatestKanjis, debugMenu)
addActionMenu("Force logging", doLogging, debugMenu)
addActionMenu("Sync", mw.onSync, debugMenu)
debugMenu.addSeparator()
addActionMenu("Update all Propernouns Details", CardMaker.updateDetailsOfProperNouns, debugMenu)
addActionMenu("Populate missing Details", CardMaker.populateMissingDeatils, debugMenu)
addActionMenu("Update Some Details", CardMaker.updateDetailsPrompt, debugMenu)
addActionMenu("Update All Details", CardMaker.updateAllDetails, debugMenu)
addActionMenu("Details for last kanji", CardMaker.refreshDetailsForLastKanji, debugMenu)
addActionMenu("Update All Known Kanjis Details", CardMaker.refreshDetailsForAllKanjis, debugMenu)


def onClose(self, evt, _old):
    response = QMessageBox.question(mw,"yoankiclose", "Do you want to do the routine before closing?", QMessageBox.Yes | QMessageBox.No)
    if response == QMessageBox.Yes:
        doRoutine()

    _old(self, evt)

AnkiQt.closeEvent = wrap(AnkiQt.closeEvent, onClose, "around")
