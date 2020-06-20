from aqt.utils import showInfo
import codecs

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
        for key in sorted(Counters._COUNTERS):
            str += key + ":" + Counters.get(key) + "\n"
        return str

    def resetCounters():
        Counters._COUNTERS = {}

    def dump():
        file = codecs.open("D:/Japanese/jap_anki/internal/.counters.txt", 'wb', 'utf-8')
        file.write(Counters.printAll())
        file.close()

    def show():
        Counters.dump()
        showInfo("counters:\r\n" + Counters.printAll())

    def sanityCheck():
        if (int(Counters.get("dupe_cleaned")) != (2*int(Counters.get("new")) - 2*int(Counters.get("in_both_files")))):
            showInfo("SUSPICIOUS BEHAVIOUR IN COUNTERS, new != clean. Do check.")
            showInfo(Counters.printAll())
