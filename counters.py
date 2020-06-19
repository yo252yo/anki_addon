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

    def show():
        showInfo("counters:\r\n" + Counters.printAll())

    def sanityCheck():
        if (Counters.get("dupe_cleaned") != Counters.get("new")):
            showInfo("SUSPICIOUS BEHAVIOUR IN COUNTERS, new != clean. Do check:/n" + Counters.printAll())
