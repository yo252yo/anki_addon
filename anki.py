from aqt import mw
from .string import String
from .counters import Counters

TAG_MANUAL = "+"
TAG_TRASH = "XX"

class Anki(object):
    def _getAnkiOfWord(word):
        Counters.increment("anki_queries")
        result = {}
        cards_ids = mw.col.findCards("Writing:" + word)
        if len(cards_ids) == 0 :
            cards_ids = mw.col.findCards("Writing:" + word + "<b*")
        if len(cards_ids) == 0 :
            return "N"

        result['cid'] = cards_ids

        result['is_sink'] = len(mw.col.findCards("Writing:" + word + " tag:" + TAG_TRASH)) > 0
        result['is_manual'] = len(mw.col.findCards("Writing:" + word + " tag:" + TAG_MANUAL)) > 0
        return result

    def getCardForWord(word):
      global _ANKI
      try:
        _ANKI
      except:
        _ANKI = {}

      if not word in _ANKI:
        _ANKI[word] = Anki._getAnkiOfWord(word)

      if _ANKI[word] == "N":
        return None
      else:
        return _ANKI[word]

    def rescheduleCard(card):
      if card['is_sink']:
        return
      Counters.increment("rescheduled", value=len(card['cid']))
      mw.col.sched.unsuspendCards(card['cid'])
      mw.col.sched.resetCards(card['cid'])
      mw.col.sched.reschedCards(card['cid'],0,7)

    def deleteCard(card):
      Counters.increment("deleted", value=len(card['cid']))
      mw.col.remNotes(card['cid'])

    def rescheduleIfKanjis(word):
      if len(word) != 1:
        return False
      Counters.increment("kanjis")
      cards_ids = mw.col.findCards("Kanji:" + word + " or Kanji0:" + word + " or Kanji2:" + word + " or Kanji3:" + word + " or Kanji4:" + word)
      #mw.col.sched.unsuspendCards(cards_ids)
      #mw.col.sched.resetCards(cards_ids)
      mw.col.sched.reschedCards(cards_ids, 0, 1)
      return cards_ids

    def resetDecks():
      dynDeckIds = [ d["id"] for d in mw.col.decks.all() if d["dyn"] ]
      [mw.col.sched.rebuildDyn(did) for did in sorted(dynDeckIds) ]
      mw.reset()

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

    def cleanupDuplicates():
        ids = mw.col.findNotes("(mid:1432900443242 -Details:*$* -Details:) or (mid:1432882338168 $)")
        Counters.increment("dupe_cleaned", value=len(ids))
        mw.col.remNotes(ids)
