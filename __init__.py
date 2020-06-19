# -*- coding: utf-8 -*-
from aqt import mw
from aqt.utils import showInfo
from aqt.deckbrowser import DeckBrowser
from aqt.qt import *
from anki.importing import TextImporter
from anki.utils import ids2str, splitFields
import json
import urllib
import codecs
import csv
import urllib.request
import urllib.parse
import re
import math
import datetime
import test

from .logs import Logs
from .anki import Anki
from .string import String
from .jisho import Jisho
from .file import File



# ============================================================================================
# Utils for printing
# ============================================================================================

def findRootWords(word):
  limitsize = 25
  kanjiword = String.kanjify(word)
  roots = {}
  for i in range(0, len(kanjiword)):
    for j in range(i, len(kanjiword)):
      subword = kanjiword[i:(j+1)]
      if len(subword) > 1 and len(subword) < len(kanjiword):
        ids = mw.col.findCards("Writing:" + subword)
        for id in ids:
          note = mw.col.getCard(id).note()
          allPronoun = note["Pronounciation"].split("<br />")
          allPronoun = allPronoun[0].split(" ")
          roots[subword] = "(" + allPronoun[0] + ") " + note["Translation"]
          if len(roots[subword]) > limitsize:
            roots[subword] = (roots[subword])[0:limitsize] + "..."

  return roots

# ============================================================================================
# Import .output file to deck
# ============================================================================================

def cleanupDuplicates():
    global COUNTERS
    ids = mw.col.findNotes("(mid:1432900443242 -Details:*$* -Details:) or (mid:1432882338168 $)")
    COUNTERS.increment("dupe_cleaned", value=len(ids))
    mw.col.remNotes(ids)

def importFileToModel(model_name, file):
    deck_id = mw.col.decks.id(":Expressions")
    mw.col.decks.select(deck_id)

    m = mw.col.models.byName(model_name)
    deck = mw.col.decks.get(deck_id)

    deck['mid'] = m['id']
    mw.col.decks.save(deck)
    m['did'] = deck_id

    importer = TextImporter(mw.col, file)
    importer.allowHTML = True
    importer.initMapping()
    importer.run()


def importOutputFileToDeck():
    file = u"D:\Japanese\jap_anki\.output.txt"
    try:
        importFileToModel("Vocabulary cant write", file)
        importFileToModel("Vocabulary", file)
    except:
        # "Error in import of .output to deck, probably because it doesn't have new words."
        i = 1
    cleanupDuplicates()



# ============================================================================================
# Print output file
# ============================================================================================

def printDetails(word, kana):
  kanjis = File.getKanjisDict()
  details = ""
  for k in word:
    try:
      details = details + k + " - " + kanjis[k] + "<br />"
    except:
      if kana:
        details = details + ".<br />"
      else:
        details = details + "$<br />"

  roots = findRootWords(word)
  if len(roots) > 0:
    for root in roots:
      details = details + "<br /> " + root + " " + roots[root]

  return details.replace('\r\n','')

def printTags(word, jisho, extra_tag=""):
  tagsString = 'AG2 ' + extra_tag + ' '
  tagsString += 'kanji' + str(String.countKanjis(word)) + ' '
  if jisho['is_common']:
    tagsString = tagsString + 'COMMON '
  if len(findRootWords(word)) > 0:
    tagsString = tagsString + 'auto_compound '
  for tag in jisho['tags']:
    if "kana alone" in tag.lower():
      tagsString = tagsString + 'KANA '
    if "onomato" in tag.lower():
      tagsString = tagsString + 'ONOM '

  return tagsString

def makeOutputFileFromData(words, extra_tag=""):
    global COUNTERS
    COUNTERS.increment("new", value=len(words))

    file = codecs.open('D:/Japanese/jap_anki/.output.txt', 'wb', 'utf-8')

    for word in words:
      for jisho in Jisho.getJisho(word):
          is_kana = False
          for tag in jisho['tags']:
            if "kana alone" in tag.lower():
              is_kana = True

          file.write(jisho['definition'].replace("\t", "") + '\t')
          if is_kana:
            file.write(jisho['word'].replace("\t", "") + "<br />" + jisho['pronunciation'].replace("\t", "") + '\t')
          else:
            file.write(jisho['word'].replace("\t", "") + '\t')
          file.write(jisho['pronunciation'].replace("\t", "") + '\t')
          file.write(printDetails(jisho['word'], is_kana).replace("\t", "") + '\t')

          file.write(jisho['ExtraPronounciations'].replace("\t", "") + '\t')
          file.write(jisho['ExtraMeanings'].replace("\t", "") + '\t')

          file.write(printTags(jisho['word'], jisho, extra_tag).replace("\t", ""))
          file.write('\r\n')

    file.close()

def overwriteInputFile(file, words):
    file = codecs.open('D:/Japanese/jap_anki/' + file, 'wb', 'utf-8')
    if not words:
        file.write(u'　')
    for word in words:
        file.write(word + ' ')
    file.close()

# ============================================================================================
# Main functions
# ============================================================================================


def importInNew():
    global COUNTERS
    words = File.fileToRawWords('in_new.txt')

    words_to_add = set()
    jisho_failures = set()

    for word in words:
        COUNTERS.increment("in_new_processed")
        jisho = Jisho.getJisho(word)[0]
        if not jisho or 'word' not in jisho:
            card = Anki.getCardForWord(word)

            if card:
                Anki.rescheduleCard(card)
                jisho_failures.add(word + "*")
            else:
                jisho_failures.add(word)
            continue


        real_word = jisho['word']

        card = Anki.getCardForWord(real_word)
        if not card:
            COUNTERS.increment("in_new_new")
            words_to_add.add(real_word)
        else:
            if card['is_sink']:
                COUNTERS.increment("in_new_sinks")
            elif card['is_manual']:
                COUNTERS.increment("in_new_manual")
                Anki.rescheduleCard(card)
            else:
                COUNTERS.increment("in_new_renew")
                Anki.deleteCard(card)
                words_to_add.add(real_word)


    makeOutputFileFromData(words_to_add, extra_tag="auto_freq")
    importOutputFileToDeck()
    overwriteInputFile('in_new.txt', jisho_failures)
    COUNTERS.increment("in_new_jisho_failures", value=len(jisho_failures))


def importInReview():
    global COUNTERS
    words = File.fileToRawWords('in_review.txt')

    words_to_add = set()

    for original_word in words:
        COUNTERS.increment("in_review_processed")
        if Anki.rescheduleKanjis(original_word):
            continue
        card = Anki.getCardForWord(original_word)
        if card:
            Anki.rescheduleCard(card)
            COUNTERS.increment("in_review_resched")
        else:
            words_expanded = String.expandToSubwords(original_word)
            for word in words_expanded:
                card = Anki.getCardForWord(word)
                if not card:
                    jisho = Jisho.getJisho(word)[0]
                    if jisho:
                        card = Anki.getCardForWord(jisho['word'])
                        if not card:
                            COUNTERS.increment("in_review_new")
                            words_to_add.add(jisho['word'])

    makeOutputFileFromData(words_to_add)
    importOutputFileToDeck()
    overwriteInputFile('in_review.txt', [])


# ============================================================================================
# Misc manipulation
# ============================================================================================

def resetDecks():
  dynDeckIds = [ d["id"] for d in mw.col.decks.all() if d["dyn"] ]
  [mw.col.sched.rebuildDyn(did) for did in sorted(dynDeckIds) ]
  mw.reset()

# ============================================================================================
# Counters
# ============================================================================================
class Counters:
    _COUNTERS = {}

    def increment(self, key, value=1):
        if not key in self._COUNTERS:
            self._COUNTERS[key] = 0
        self._COUNTERS[key] += value

    def get(self, key):
        if not key in self._COUNTERS:
            return str(0)
        else :
            return str(self._COUNTERS[key])

    def printAll(self):
        str = " "
        for key in self._COUNTERS:
            str += key + ":" + self.get(key) + "\n"
        return str

def resetCounters():
    global COUNTERS
    COUNTERS = Counters()
    COUNTERS._COUNTERS = {}

def printCounters():
    global COUNTERS
    log = codecs.open('D:/Japanese/jap_anki/log.txt', 'a', 'utf-8')
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    log.write(str(date) + "\t")

    log.write("0\t")
    log.write(COUNTERS.get("expanded") + "\t")
    log.write(COUNTERS.get("new") + "\t")
    log.write(COUNTERS.get("deleted") + "\t")
    log.write(COUNTERS.get("rescheduled") + "\t")
    log.write("0\t")
    log.write(COUNTERS.get("in_new_processed") + "\t")
    log.write(COUNTERS.get("in_new_new") + "\t")
    log.write(COUNTERS.get("in_new_renew") + "\t")
    log.write(COUNTERS.get("in_review_processed") + "\t")
    log.write(COUNTERS.get("in_review_new") + "\t")
    log.write(COUNTERS.get("in_review_resched") + "\t")
    log.write(COUNTERS.get("kanjis") + "\t")
    log.write(COUNTERS.get("extra_polysemic") + "\t")

    log.write("\r\n")
    log.close()
    showInfo("counters:\n" + COUNTERS.printAll())
    if (COUNTERS.get("dupe_cleaned") != COUNTERS.get("new")):
        showInfo("SUSPICIOUS BEHAVIOUR IN COUNTERS, new != clean. Do check:/n" + COUNTERS.printAll())




# ============================================================================================
# Menu things
# ============================================================================================

def doRoutine():
  mw.onSync()
  mw.progress.start(immediate=True)
  resetCounters()
  importInReview()
  importInNew()
  Logs.logStats()
  Logs.logKanjis()
  resetDecks()
  mw.progress.finish()
  mw.onSync()
  printCounters()

def addActionMenu(text, function):
    action = QAction(text, mw)
    action.triggered.connect(function)
    mw.form.menuTools.addAction(action)

addActionMenu("=> Do everything", doRoutine)
addActionMenu("Import in_new.txt words", importInNew)
addActionMenu("Import in_review.txt words", importInReview)
addActionMenu("Import output", importOutputFileToDeck)
addActionMenu("Reset decks", resetDecks)

addActionMenu("Log Stats", Logs.logStats)
addActionMenu("Log Kanjis", Logs.logKanjis)
