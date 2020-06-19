
import codecs
import datetime
from aqt.utils import showInfo

class Counters:
    _COUNTERS = {}

    def increment(key, value=1):
        if not key in Counters._COUNTERS:
            Counters._COUNTERS[key] = 0
        Counters._COUNTERS[key] += value

    def get(key):
        if not key in Counters._COUNTERS:
            return str(0)
        else :
            return str(Counters._COUNTERS[key])

    def printAll():
        str = " "
        for key in Counters._COUNTERS:
            str += key + ":" + Counters.get(key) + "\n"
        return str

    def resetCounters():
        Counters._COUNTERS = {}

    def log(filename):
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

    def show():
        showInfo("counters:\r\n" + Counters.printAll())

    def sanityCheck():
        if (Counters.get("dupe_cleaned") != Counters.get("new")):
            showInfo("SUSPICIOUS BEHAVIOUR IN COUNTERS, new != clean. Do check:/n" + Counters.printAll())
