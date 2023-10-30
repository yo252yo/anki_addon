from aqt import mw
from .string import String
from .counters import Counters
from .dumps import Dumps
from aqt.utils import showInfo
import math

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
      mw.col.sched.unsuspend_cards(card['cid'])
      mw.col.sched.schedule_cards_as_new(card['cid'])

    def softRescheduleCard(card):
        if card['is_sink']:
          return
        Counters.increment("rescheduled", value=len(card['cid']))
        Counters.increment("softrescheduled", value=len(card['cid']))
        mw.col.sched.unsuspend_cards(card['cid'])
        mw.col.sched.set_due_date(card['cid'],"0-1")

    def deleteCard(card):
      Counters.increment("deleted", value=len(card['cid']))
      mw.col.remCards(card['cid'])
      mw.reset()

    def rescheduleIfKanjis(word):
      if len(word) != 1:
        return False
      Counters.increment("kanjis")
      cards_ids = mw.col.findCards("Kanji:" + word + " or Kanjis:*" + word + "*")
      mw.col.sched.set_due_date(cards_ids,"0-1")
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

    def cleanupDuplicates(filename):
        ids = mw.col.findNotes("(mid:1432900443242 -Details:*$* -Details:) or (mid:1432882338168 $)")
        Counters.increment("dupe_cleaned", value=len(ids))
        Counters.increment("dupe_cleaned_"+filename, value=len(ids))
        Dumps.dump_ids('D:/Japanese/jap_anki/internal/.cleanups.'+filename+'.txt', ids)
        mw.col.remNotes(ids)

    def rescheduleLatestKanjis():
        ids = mw.col.findNotes("deck:Kanjis added:3")
        for id in ids:
          note = mw.col.getNote(id)
          k = note["Kanji"]
          rids = mw.col.findNotes(k)
          mw.col.sched.set_due_date(rids, "0-"+str(math.floor(len(rids)/5)))
          Counters.increment("rescheduled_kanjis", value=len(rids))

    def changeDeckCanWrite():
        ids_can_write = mw.col.findCards("(mid:1432900443242 -Details:*$* -Details:)")
        ids_cant_write = mw.col.findCards("(mid:1432882338168 $)")
        Counters.increment("adjusted_can_write", value=len(ids_can_write))
        Counters.increment("adjusted_cant_write", value=len(ids_cant_write))

        mid_can_write = mw.col.models.byName("Vocabulary")['id']
        mid_cant_write = mw.col.models.byName("Vocabulary cant write")['id']
        did_can_write = mw.col.decks.id("Vocabulary::Reading")
        did_cant_write = mw.col.decks.id("Vocabulary::Listening")

        for id in ids_can_write:
          card = mw.col.getCard(id)
          note = card.note()
          note.mid = mid_can_write
          if (card.did == did_cant_write):
            card.did = did_can_write
          note.flush()
          card.flush()

        for id in ids_cant_write:
          card = mw.col.getCard(id)
          note = card.note()
          note.mid = mid_cant_write
          if (card.did == did_can_write):
            card.did = did_cant_write
          note.flush()
          card.flush()

        mw.reset()
        mw.col.sched.set_due_date(ids_can_write, "0-7")
