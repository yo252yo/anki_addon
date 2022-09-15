from aqt import mw
from .anki import Anki
from .readfile import ReadFile
from .string import String
from aqt.utils import showInfo
import re

from aqt.qt import *

class CardMaker(object):
    VERBOSE = False
    VersionAG = "AG3"
    VersionAD = "AD5"
    html_re = re.compile(r'(<!--.*?-->|<[^>]*>)')

    def _makeDetailsString(word, kana):
      kanjis = ReadFile.getKanjisDict()
      details = ""
      for k in word:
        try:
          k = k.lower()
          if (k == "\n") or (k == "\\") or (k == "/") or (k == "$"):
              continue
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

    def _makeTagsString(word, jisho, extra_tag=""):
      tagsString = CardMaker.VersionAG + ' ' + CardMaker.VersionAD + ' ' + extra_tag + ' '
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

    def sanitize(word):
        raw = word.replace("&nbsp;", " ").replace("<br\s*?>", "\n").replace("<div>", "\n").replace("</div>", "").replace("\n\n", "\n")
        no_tags = CardMaker.html_re.sub('', raw)
        return no_tags.strip().replace("\n", "<br />")

    def _refreshDetailsForSearch(search):
        cards = mw.col.findNotes(search)
        if CardMaker.VERBOSE:
            showInfo("Updating details for search:" + search)

        for cid in cards:
            try:
                note = mw.col.getNote(cid)
                note.tags.append(CardMaker.VersionAD)
                if "Details" in note:
                    word = ""
                    if "ProperNoun" in note:
                        note["ProperNoun"] = CardMaker.sanitize(note["ProperNoun"])
                        word = note["ProperNoun"]
                    if "Writing" in note:
                        note["Writing"] = CardMaker.sanitize(note["Writing"])
                        word = note["Writing"]
                    if word:
                        note["Details"] = CardMaker._makeDetailsString(word, ("KANA" in note.tags))
                note.flush()

            except Exception as err:
                showInfo("Failed:" + str(err))
        if CardMaker.VERBOSE:
            showInfo("Updated cards:" + str(len(cards)))

    def updateDetailsPrompt():
        text, ok = QInputDialog.getText(mw, 'Update cards from a given search', "Query", QLineEdit.Normal, "")
        if not ok:
            return
        CardMaker._refreshDetailsForSearch(text)

    def updateAllDetails():
        CardMaker._refreshDetailsForSearch("-tag:" + CardMaker.VersionAD)

    def updateDetailsOfProperNouns():
        CardMaker._refreshDetailsForSearch("note:ProperNoun")

    def populateMissingDeatils():
        CardMaker._refreshDetailsForSearch("Details:")

    def refreshDetailsForLastKanji():
        CardMaker._refreshDetailsForSearch(ReadFile.getLastKanji())

    def refreshDetailsForAllKanjis():
        kanjis = ReadFile.getKanjisDict()
        for k in kanjis:
            CardMaker._refreshDetailsForSearch(k + " (? OR $)")
