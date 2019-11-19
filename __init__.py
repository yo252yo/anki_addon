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

TAG_MANUAL = "+"
TAG_TRASH = "XX"

  
# ============================================================================================
# Anki DB functions
# ============================================================================================
 
def _getAnkiOfWord(word): 
    global COUNTERS
    COUNTERS.increment("anki_queries")
    
    result = {}
    cards_ids = mw.col.findNotes("Writing:" + word)
    if len(cards_ids) == 0 :
        cards_ids = mw.col.findNotes("Writing:" + word + "<b*")
    if len(cards_ids) == 0 :
        return "N"

    result['cid'] = cards_ids
    
    result['is_sink'] = len(mw.col.findNotes("Writing:" + word + " tag:" + TAG_TRASH)) > 0
    result['is_manual'] = len(mw.col.findNotes("Writing:" + word + " tag:" + TAG_MANUAL)) > 0
    return result
 
def getCardForWord(word):  
  global _ANKI
  try:
    _ANKI
  except:
    _ANKI = {}

  if not word in _ANKI:
    _ANKI[word] = _getAnkiOfWord(word)
  
  if _ANKI[word] == "N":
    return None
  else:
    return _ANKI[word]

def rescheduleCard(card): 
  if card['is_sink']:
    return

  global COUNTERS
  COUNTERS.increment("rescheduled", value=len(card['cid']))

  mw.col.sched.unsuspendCards(card['cid'])
  mw.col.sched.resetCards(card['cid'])
  mw.col.sched.reschedCards(card['cid'],0,7)
 
def deleteCard(card):
  global COUNTERS
  COUNTERS.increment("deleted", value=len(card['cid']))
  mw.col.remNotes(card['cid'])
  
def rescheduleKanjis(word):
  if len(word) != 1:
    return False
    
  global COUNTERS
  COUNTERS.increment("kanjis")
    
  cards_ids = mw.col.findCards("Kanji:" + word + " or Kanji0:" + word + " or Kanji2:" + word + " or Kanji3:" + word + " or Kanji4:" + word)
  
  #mw.col.sched.unsuspendCards(cards_ids)
  #mw.col.sched.resetCards(cards_ids)
  mw.col.sched.reschedCards(cards_ids, 0, 1)
  return cards_ids
 
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
    m = mw.col.models.byName(model_name)
    deck_id = mw.col.decks.id(":Expressions")
    mw.col.decks.select(deck_id)    
    deck = mw.col.decks.get(deck_id)
    deck['mid'] = m['id']
    mw.col.decks.save(deck)
  
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

def _getJishoOfWord(word):
    global COUNTERS
    COUNTERS.increment("jisho_queries")
    
    url = 'http://jisho.org/api/v1/search/words?keyword=' + urllib.parse.quote(word)
    data = json.load(urllib.request.urlopen(url))
    word_data = data['data'][0]        
        
    jisho = {}
    jisho['pronunciation'] = word_data['japanese'][0]['reading'].rstrip('\r\n')
    try:
        jisho['word'] = word_data['japanese'][0]['word'].rstrip('\r\n')
    except:
        jisho['word'] = pronunciation
 
    definitions = word_data['senses'][0]['english_definitions']
    jisho['definition'] = (". ".join(definitions)).replace(",", ".").rstrip('\r\n')
    
    jisho['tags'] = set().union(word_data['tags'], word_data['senses'][0]['tags'])   
    jisho['is_common'] = word_data['is_common']
    
    return jisho
    
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
      _JISHO[jisho['word']] = jisho
    except Exception as inst:
      _JISHO[word] = "N"
    
  if _JISHO[word] == "N":
    return None
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
  tagsString = 'AG1 ' + extra_tag + ' '
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
      jisho = getJisho(word)
      if jisho:
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
        jisho = getJisho(word)
        if not jisho or 'word' not in jisho:
            card = getCardForWord(word)
            if card:
                rescheduleCard(card)
            else:
                jisho_failures.add(word)
            continue
        
        real_word = jisho['word']
        
        card = getCardForWord(real_word)
        if not card:
            COUNTERS.increment("in_new_new")
            words_to_add.add(real_word)
        else:
            if card['is_sink']:
                COUNTERS.increment("in_new_sinks")
            elif card['is_manual']:
                COUNTERS.increment("in_new_manual")
                rescheduleCard(card)
            else :
                COUNTERS.increment("in_new_renew")
                deleteCard(card)
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
        if rescheduleKanjis(original_word):
            continue 
        card = getCardForWord(original_word)
        if card:
            rescheduleCard(card)
            COUNTERS.increment("in_review_resched")
        else:
            words_expanded = expandToSubwords(original_word)
            for word in words_expanded:
                card = getCardForWord(word)
                if not card:
                    jisho = getJisho(word)
                    if jisho:
                        card = getCardForWord(jisho['word'])
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
# Logging things
# ============================================================================================

def logs(log, string):
    log.write(str(len(mw.col.findCards(string))) + "\t")


def logStats():
    log = codecs.open('D:/Japanese/jap_anki/log_counts.txt', 'a', 'utf-8')
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    log.write(str(date) + "\t")
    logs(log, "is:new -is:suspended")
    logs(log, "is:due")
    logs(log, "is:review")
    logs(log, "is:suspended")
    logs(log, "mid:1432882338168") # vocabulary
    logs(log, "mid:1432900443242") # vocabulary cant write
    logs(log, "added:1")
    logs(log, "rated:1")
    log.write("0\t")
    logs(log, "tag:AG1")
    logs(log, "deck::Vocabulary::Listening")
    logs(log, "deck::Vocabulary::Reading")
    logs(log, "deck::Vocabulary::Talking")
    logs(log, "deck::Kanjis::All") # kanjis
    logs(log, "(mid:1432882338168 or mid:1432900443242) is:suspended") # suspended voc
    base = "(mid:1432882338168 or mid:1432900443242) -is:suspended -tag:XX "
    logs(log, base + "is:new") # new voc
    logs(log, base + "prop:ivl<21") # young voc
    logs(log, base + "prop:ivl>21") # mature voc
    logs(log, "mid:1432882338168 -is:suspended -tag:XX prop:ivl>21") # vocabulary known
    logs(log, "mid:1432900443242 -is:suspended -tag:XX prop:ivl>21") # vocabulary cant write known
    logs(log, "deck::Kanjis::All prop:ivl>21") # kanjis known
    
    
    log.write("\r\n")
    log.close()
    
def logKanjis():
    log = codecs.open('D:/Japanese/jap_anki/kanjis_ivl.txt', 'w', 'utf-8')
    kanjis_cards = mw.col.findCards("deck::Kanjis::All")
    reverse_cards = mw.col.findCards("deck::Kanjis::Reverse")
    ivls = {}
    
    for id in kanjis_cards:
        card = mw.col.getCard(id)
        note = mw.col.getCard(id).note()
        ivls[note["Kanji"]] = card.ivl
        
    for id in reverse_cards:
        card = mw.col.getCard(id)
        note = mw.col.getCard(id).note()
        if note["Kanji"] in ivls:
            ivls[note["Kanji"]] += 0.5 * min(ivls[note["Kanji"]], card.ivl)
            ivls[note["Kanji"]] = 0.3 * ivls[note["Kanji"]] + 0.3 * card.ivl
        else:
            ivls[note["Kanji"]] = card.ivl
    
    log.write("Kanji\t\t ivl\r\n")
    for kanji in ivls:
        log.write(kanji + "\t\t" + str(math.ceil(ivls[kanji])) + "\r\n")
        
    log.close()
   
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
  logStats()
  logKanjis()
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

addActionMenu("Log Stats", logStats)
addActionMenu("Log Kanjis", logKanjis)
