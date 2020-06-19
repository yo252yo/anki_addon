# -*- coding: utf-8 -*-
from aqt import mw
import codecs
import datetime
import math

class Logs(object):
    def write(log, string):
        log.write(str(len(mw.col.findCards(string))) + "\t")


    def logStats():
        log = codecs.open('D:/Japanese/jap_anki/log_counts.txt', 'a', 'utf-8')
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        log.write(str(date) + "\t")
        Logs.write(log, "is:new -is:suspended")
        Logs.write(log, "is:due")
        Logs.write(log, "is:review")
        Logs.write(log, "is:suspended")
        Logs.write(log, "mid:1432882338168") # vocabulary
        Logs.write(log, "mid:1432900443242") # vocabulary cant write
        Logs.write(log, "added:1")
        Logs.write(log, "rated:1")
        log.write("0\t")
        Logs.write(log, "(tag:AG2 or tag:AG1)")
        Logs.write(log, "deck::Vocabulary::Listening")
        Logs.write(log, "deck::Vocabulary::Reading")
        Logs.write(log, "deck::Vocabulary::Talking")
        Logs.write(log, "deck::Kanjis::All") # kanjis
        Logs.write(log, "(mid:1432882338168 or mid:1432900443242) is:suspended") # suspended voc
        base = "(mid:1432882338168 or mid:1432900443242) -is:suspended -tag:XX "
        Logs.write(log, base + "is:new") # new voc
        Logs.write(log, base + "prop:ivl<21") # young voc
        Logs.write(log, base + "prop:ivl>21") # mature voc
        Logs.write(log, "mid:1432882338168 -is:suspended -tag:XX prop:ivl>21") # vocabulary known
        Logs.write(log, "mid:1432900443242 -is:suspended -tag:XX prop:ivl>21") # vocabulary cant write known
        Logs.write(log, "deck::Kanjis::All prop:ivl>21") # kanjis known

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
                ivls[note["Kanji"]] += 0.3 * min(ivls[note["Kanji"]], card.ivl)
                ivls[note["Kanji"]] = 0.3 * ivls[note["Kanji"]] + 0.3 * card.ivl
            else:
                ivls[note["Kanji"]] = card.ivl

        log.write("Kanji\t\t ivl\r\n")
        for kanji in ivls:
            log.write(kanji + "\t\t" + str(math.ceil(ivls[kanji])) + "\r\n")

        log.close()
