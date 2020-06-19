from aqt import mw

class Anki(object):
    def _getAnkiOfWord(word):
        global COUNTERS
        COUNTERS.increment("anki_queries")

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
