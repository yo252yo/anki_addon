import re
from .counters import Counters

class String(object):
    def kanjify(text):
      hiragana = u'[ぁ-ゟ]'
      katakana = u'[゠-ヿ]'
      misc = u'[\)\(]'
      output = re.sub(hiragana, '', text)
      output = re.sub(katakana, '', output)
      output = re.sub(misc, '', output)
      #output = unicode(output)
      return output

    def countKanjis(word):
      return len(String.kanjify(word))

    def expandToSubwords(word):
      result = set()
      result.add(word)
      kanjiword = String.kanjify(word)
      for i in range(0, len(kanjiword)):
        for j in range(i, len(kanjiword)):
            subword = kanjiword[i:(j+1)]
            if (len(subword) >= 2 and not subword in result):
              result.add(subword)
      Counters.increment("expanded", value=len(result)-1)
      return result
