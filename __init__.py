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

TAG_MANUAL = "+"
TAG_TRASH = "XX"

# ============================================================================================
# File functions
# ============================================================================================

def handleWordEncoding(word):
  if word.startswith(u'\ufeff'):
    word = word[1:]
  return word

def fileToRawWords(file):
    f = codecs.open('D:/Japanese/jap_anki/' + file, 'rb', 'utf-8')
    words = set()
    for line in f:
      for rawline in line.split(' '):
          for rawword in rawline.split(u'　'):
            if not rawword or rawword == '' or rawword == ' ' or rawword == u'　':
                continue
            word = handleWordEncoding(rawword).rstrip('\r\n')
            words.add(word)

    return words

#def getKanjisDict():
#    kanjis = {}
#    sim = codecs.open('D:/Japanese/jap_anki/kanjis_details.txt', 'rb', 'utf-8')
#    cr = csv.reader(sim)
#    for row in cr:
#      k = handleWordEncoding(row[0])
#      d = handleWordEncoding(row[2]) + " (" + handleWordEncoding(row[1]) + ")"
#      kanjis[k] = d
#    sim.close()
#    return kanjis


# OLD VERSION, REPLACE BY THE ABOVE
def getKanjisDict():
    kanjis = {}
    sim = codecs.open('D:/Japanese/jap_anki/kanjis_old.txt', 'rb', 'utf-8')
    for kanji in sim:
      kanji = handleWordEncoding(kanji)
      k = kanji[:1]
      d = kanji[4:]
      kanjis[k] = d
    sim.close()
    return kanjis

# ============================================================================================
# String functions
# ============================================================================================

def kanjify(text):
  hiragana = u'[ぁ-ゟ]'
  katakana = u'[゠-ヿ]'
  output = re.sub(hiragana, '', text)
  output = re.sub(katakana, '', output)
  #output = unicode(output)

  return output

def countKanjis(word):
  return len(kanjify(word))

def expandToSubwords(word):
  result = set()
  result.add(word)
  kanjiword = kanjify(word)
  for i in range(0, len(kanjiword)):
    for j in range(i, len(kanjiword)):
        subword = kanjiword[i:(j+1)]
        if (len(subword) >= 2 and not subword in result):
          result.add(subword)

  global COUNTERS
  COUNTERS.increment("expanded", value=len(result)-1)
  return result

# ============================================================================================
# Utils for printing
# ============================================================================================

def findRootWords(word):
  limitsize = 25
  kanjiword = kanjify(word)
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
# Jisho interaction
# ============================================================================================

def tryGetJishoField(data, field):
    if field in data:
        result = data[field]

        if type(result) == str:
            return result.replace(",", ".").rstrip('\r\n').lower()
        else:
            return ". ".join([i.replace(",", ".").rstrip('\r\n').lower() for i in result])
    else:
        return ""

def _getJishoPronouciations(word_data):
    main = tryGetJishoField(word_data['japanese'][0], 'reading')
    all = set([tryGetJishoField(j, 'reading') for j in word_data['japanese']]).union(set([tryGetJishoField(j, 'word') for j in word_data['japanese']]))
    try:
      all.remove("")
    except:
      i = 1 # expected
    return (main, all)

def _getJishoDefinition(word_data):
    main = tryGetJishoField(word_data['senses'][0], 'english_definitions')
    all = set([tryGetJishoField(j, 'english_definitions') for j in word_data['senses']])
    try:
      all.remove("")
    except:
      i = 1 # expected
    return (main, all)


def _getJishoOfData(word_data):
    jisho = {}

    pronunciation, pronounciations = _getJishoPronouciations(word_data)

    try:
        jisho['word'] = word_data['japanese'][0]['word'].rstrip('\r\n')
    except:
        jisho['word'] = pronunciation

    jisho['pronunciation'] = pronunciation
    try:
        pronounciations.remove(jisho['word'])
        pronounciations.remove(pronunciation)
    except:
        print("not supposed to happen but no biggie")
    jisho['ExtraPronounciations'] = "//".join(pronounciations)

    definition, definitions = _getJishoDefinition(word_data)
    jisho['definition'] = definition
    try:
        definitions.remove(definition)
    except:
        print("not supposed to happen but no biggie")
    jisho['ExtraMeanings'] = "//".join(definitions)

    jisho['tags'] = set().union(word_data['tags'], word_data['senses'][0]['tags'])
    jisho['is_common'] = word_data['is_common']

    return jisho

def _getJishoOfWord(word):
    global COUNTERS
    COUNTERS.increment("jisho_queries")

    url = 'http://jisho.org/api/v1/search/words?keyword=' + urllib.parse.quote(word)
    data = json.load(urllib.request.urlopen(url))

    if 'data' not in data or len(data['data']) < 1:
        raise OSError

    result = [_getJishoOfData(data['data'][0])]
    words = [result[0]['word']]

    for word_data in data['data'][1:]:
        current_word = word_data['japanese'][0]['word']
        if current_word in words:
            i = words.index(current_word)

            COUNTERS.increment("extra_polysemic")
            pronunciation, pronounciations = _getJishoPronouciations(word_data)
            result[i]['ExtraPronounciations'] += "<br />"
            result[i]['ExtraPronounciations'] += "//".join(pronounciations)

            definition, definitions = _getJishoDefinition(word_data)
            result[i]['ExtraMeanings'] += "<br />"
            result[i]['ExtraMeanings'] += "//".join(definitions)

        elif current_word == word or tryGetJishoField(word_data, 'reading') == word:
            COUNTERS.increment("extra_polysemic")
            result.append(_getJishoOfData(word_data))
            words.append(current_word)

    return result

def getJisho(word):
  global _JISHO
  try:
    _JISHO
  except:
    _JISHO = {}

  if not word in _JISHO:
    try:
      jisho = _getJishoOfWord(word)
      _JISHO[word] = jisho
      _JISHO[jisho[0]['word']] = jisho
    except OSError as inst: # not in jisho
      _JISHO[word] = "N"

  if _JISHO[word] == "N":
    return [None]
  else:
    return _JISHO[word]


# ============================================================================================
# Print output file
# ============================================================================================

def printDetails(word, kana):
  kanjis = getKanjisDict()
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
  tagsString += 'kanji' + str(countKanjis(word)) + ' '
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
      for jisho in getJisho(word):
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
    words = fileToRawWords('in_new.txt')

    words_to_add = set()
    jisho_failures = set()

    for word in words:
        COUNTERS.increment("in_new_processed")
        jisho = getJisho(word)[0]
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
    words = fileToRawWords('in_review.txt')

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
            words_expanded = expandToSubwords(original_word)
            for word in words_expanded:
                card = Anki.getCardForWord(word)
                if not card:
                    jisho = getJisho(word)[0]
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
