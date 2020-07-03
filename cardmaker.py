from aqt import mw
from .anki import Anki
from .readfile import ReadFile
from .string import String

class CardMaker(object):
    def makeDetailsString(word, kana):
      kanjis = ReadFile.getKanjisDict()
      details = ""
      for k in word:
        try:
          details = details + k + " - " + kanjis[k] + "<br />"
        except:
          if kana:
            details = details + ".<br />"
          else:
            details = details + "$<br />"
      roots = Anki.findRootWords(word)
      if len(roots) > 0:
        for root in roots:
          details = details + "<br /> " + root + " " + roots[root]
      return details.replace('\r\n','').replace('\n','').replace('\t', '')

    def makeTagsString(word, jisho, extra_tag=""):
      tagsString = 'AG2 ' + extra_tag + ' '
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

    def updateDetailsOfProperNouns():
        cards = mw.col.findNotes("note:ProperNoun Details:")
        for cid in cards:
            note = mw.col.getNote(cid)
            # We may need to replace False by is_kana from jisho if we expand this out of proper nouns
            note["Details"] = CardMaker.makeDetailsString(note["ProperNoun"], False)
            note.flush()
