from aqt import mw
from .anki import Anki
from .readfile import ReadFile
from .string import String
from aqt.utils import showInfo

class CardMaker(object):
    VERBOSE = False
    Version = "AG3"

    def makeDetailsString(word, kana):
      kanjis = ReadFile.getKanjisDict()
      details = ""
      for k in word:
        try:
          if kanjis[k].strip()[0] == ".":
              continue #kanas, romaji, etc...
          details = details + k + " - " + kanjis[k] + "<br />"
        except:
          if kana:
            details = details + "?<br />" #kanji we dont know yet
          else:
            details = details + "$<br />"
      if len(details) == 0:
        details = "."
      if len(word) > 2:
          roots = Anki.findRootWords(word)
          if len(roots) > 0:
            for root in roots:
              details = details + "<br /> " + root + " " + roots[root]
      return details.replace('\r\n','').replace('\n','').replace('\t', '')

    def makeTagsString(word, jisho, extra_tag=""):
      tagsString = CardMaker.Version + ' ' + extra_tag + ' '
      tagsString += 'kanji' + str(String.countKanjis(word)) + ' '
      if jisho['is_common']:
        tagsString = tagsString + 'COMMON '
      if len(Anki.findRootWords(word)) > 0:
        tagsString = tagsString + 'auto_compound '
      for tag in jisho['tags']:
        if "kana alone" in tag.lower():
          tagsString = tagsString + 'KANA '
        if "onomato" in tag.lower():
          tagsString = tagsString + 'ONOM '
      return tagsString

    def _refreshDetailsForSearch(search):
        cards = mw.col.findNotes(search)
        if CardMaker.VERBOSE:
            showInfo("Updating details for search:" + search)
        i = 0
        for cid in cards:
            try:
                note = mw.col.getNote(cid)
                note.tags.append(CardMaker.Version)
                if "Details" in note:
                    word = ""
                    if "ProperNoun" in note:
                        word = note["ProperNoun"]
                    if "Writing" in note:
                        word = note["Writing"]
                    if word:
                        note["Details"] = CardMaker.makeDetailsString(word, False)
                note.flush()
            except Exception as err:
                showInfo("Failed:" + str(err))
        if CardMaker.VERBOSE:
            showInfo("Updated cards:" + str(len(cards)))


    def refreshAllDetails():
        CardMaker._refreshDetailsForSearch("-tag:" + CardMaker.Version)

    def forceUpdateDetailsOfProperNouns():
        CardMaker._refreshDetailsForSearch("note:ProperNoun")

    def updateDetailsOfProperNouns():
        CardMaker._refreshDetailsForSearch("note:ProperNoun Details:")
