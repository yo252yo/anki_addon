# -*- coding: utf-8 -*-
from aqt import mw
import codecs
import datetime
import math
from .counters import Counters

class Dumps(object):
    def write(log, string):
        log.write(str(len(mw.col.findCards(string))) + "\t")

    def logStats(filename):
        log = codecs.open(filename, 'a', 'utf-8')
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        log.write(str(date) + "\t")
        Dumps.write(log, "is:new -is:suspended")
        Dumps.write(log, "is:due")
        Dumps.write(log, "is:review")
        Dumps.write(log, "is:suspended")
        Dumps.write(log, "mid:1432882338168") # vocabulary
        Dumps.write(log, "mid:1432900443242") # vocabulary cant write
        Dumps.write(log, "added:1")
        Dumps.write(log, "rated:1")
        log.write("0\t")
        Dumps.write(log, "(tag:AG2 or tag:AG1)")
        Dumps.write(log, "deck::Vocabulary::Listening")
        Dumps.write(log, "deck::Vocabulary::Reading")
        Dumps.write(log, "deck::Vocabulary::Talking")
        Dumps.write(log, "deck::Kanjis::All") # kanjis
        Dumps.write(log, "(mid:1432882338168 or mid:1432900443242) is:suspended") # suspended voc
        base = "(mid:1432882338168 or mid:1432900443242) -is:suspended -tag:XX "
        Dumps.write(log, base + "is:new") # new voc
        Dumps.write(log, base + "prop:ivl<21") # young voc
        Dumps.write(log, base + "prop:ivl>21") # mature voc
        Dumps.write(log, "mid:1432882338168 -is:suspended -tag:XX prop:ivl>21") # vocabulary known
        Dumps.write(log, "mid:1432900443242 -is:suspended -tag:XX prop:ivl>21") # vocabulary cant write known
        Dumps.write(log, "deck::Kanjis::All prop:ivl>21") # kanjis known
        log.write("\r\n")
        log.close()

    def logKanjis(filename):
        log = codecs.open(filename, 'w', 'utf-8')
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
                reverseivl = ivls[note["Kanji"]]
                m = min(reverseivl, card.ivl)
                avg_ivl = (2 * m + reverseivl + card.ivl) / 4
                ivls[note["Kanji"]] = min(3*m, avg_ivl)
            else:
                ivls[note["Kanji"]] = card.ivl

        log.write("Kanji\t\t ivl\r\n")
        for kanji in ivls:
            log.write(kanji + "\t\t" + str(math.ceil(ivls[kanji])) + "\r\n")

        log.close()

    def logCounters(filename):
        log = codecs.open(filename, 'a', 'utf-8')
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        log.write(str(date) + "\t")
        log.write("0\t")
        log.write(Counters.get("expanded") + "\t")
        log.write(Counters.get("new") + "\t")
        log.write(Counters.get("deleted") + "\t")
        log.write(Counters.get("rescheduled") + "\t")
        log.write("0\t")
        log.write(Counters.get("in_new_processed") + "\t")
        log.write(Counters.get("in_new_new") + "\t")
        log.write(Counters.get("in_new_renew") + "\t")
        log.write(Counters.get("in_review_processed") + "\t")
        log.write(Counters.get("in_review_new") + "\t")
        log.write(Counters.get("in_review_resched") + "\t")
        log.write(Counters.get("kanjis") + "\t")
        log.write(Counters.get("extra_polysemic") + "\t")
        log.write("\r\n")
        log.close()

    def dump_ids(filename, ids):
        file = codecs.open(filename, 'wb', 'utf-8')
        file.write(str(ids) + "\n")

        for nid in ids :
            # create string using the japanese and english vocabCardJapanese vocabCardEnglish
            vocabNote = mw.col.getNote(nid)
            file.write(vocabNote['Writing'] + "\n")
        file.close()

    def dump_strings(filename, strs):
        file = codecs.open(filename, 'wb', 'utf-8')
        for s in strs :
            file.write(s + "\n")
        file.close()
