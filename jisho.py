import json
import urllib
from .counters import Counters

class Jisho(object):
    _JISHO = {}

    def _tryGetJishoField(data, field):
        if field in data:
            result = data[field]

            if type(result) == str:
                return result.replace(",", ".").rstrip('\r\n').lower()
            else:
                return ". ".join([i.replace(",", ".").rstrip('\r\n').lower() for i in result])
        else:
            return ""

    def _tryGetJishoWord(data):
        result = Jisho._tryGetJishoField(data, 'word')
        if result == "":
            result = Jisho._tryGetJishoField(data, 'reading')
        return result

    def _getJishoPronouciations(word_data):
        main = Jisho._tryGetJishoField(word_data['japanese'][0], 'reading')
        all = set([Jisho._tryGetJishoField(j, 'reading') for j in word_data['japanese']]).union(set([Jisho._tryGetJishoField(j, 'word') for j in word_data['japanese']]))
        try:
          all.remove("")
        except:
          i = 1 # expected
        return (main, all)

    def _getJishoDefinition(word_data):
        main = Jisho._tryGetJishoField(word_data['senses'][0], 'english_definitions')
        all = set([Jisho._tryGetJishoField(j, 'english_definitions') for j in word_data['senses']])
        try:
          all.remove("")
        except:
          i = 1 # expected
        return (main, all)

    def _getJishoOfData(word_data):
        jisho = {}
        pronunciation, pronounciations = Jisho._getJishoPronouciations(word_data)
        jisho['word'] = Jisho._tryGetJishoWord(word_data['japanese'][0])
        jisho['pronunciation'] = pronunciation
        try:
            pronounciations.remove(jisho['word'])
            pronounciations.remove(pronunciation)
        except:
            print("not supposed to happen but no biggie")
        if pronounciations:
            jisho['ExtraPronounciations'] = "//".join(pronounciations)
        else:
            jisho['ExtraPronounciations'] = "."

        definition, definitions = Jisho._getJishoDefinition(word_data)
        jisho['definition'] = definition
        try:
            definitions.remove(definition)
        except:
            print("not supposed to happen but no biggie")
    if definitions:
        jisho['ExtraMeanings'] = "//".join(definitions)
    else:
        jisho['ExtraMeanings'] = "."

        jisho['tags'] = set().union(word_data['tags'], word_data['senses'][0]['tags'])
        if('is_common' in word_data):
            jisho['is_common'] = word_data['is_common']
        else:
            jisho['is_common'] = False

        return jisho

    def _getJishoOfWord(word):
        Counters.increment("jisho_queries")

        url = 'http://jisho.org/api/v1/search/words?keyword=' + urllib.parse.quote(word)
        data = json.load(urllib.request.urlopen(url))

        if 'data' not in data or len(data['data']) < 1:
            raise OSError

        result = [Jisho._getJishoOfData(data['data'][0])]
        words = [result[0]['word']]

        for word_data in data['data'][1:]:
            current_word = Jisho._tryGetJishoWord(word_data['japanese'][0])
            if current_word in words:
                i = words.index(current_word)

                Counters.increment("extra_polysemic")
                pronunciation, pronounciations = Jisho._getJishoPronouciations(word_data)
                result[i]['ExtraPronounciations'] += "<br />"
                result[i]['ExtraPronounciations'] += "//".join(pronounciations)

                definition, definitions = Jisho._getJishoDefinition(word_data)
                result[i]['ExtraMeanings'] += "<br />"
                result[i]['ExtraMeanings'] += "//".join(definitions)

            elif current_word == word or Jisho._tryGetJishoField(word_data, 'reading') == word:
                Counters.increment("extra_polysemic")
                result.append(Jisho._getJishoOfData(word_data))
                words.append(current_word)

        return result

    def getJisho(word):
      if not word in Jisho._JISHO:
        try:
          jisho = Jisho._getJishoOfWord(word)
          Jisho._JISHO[word] = jisho
          Jisho._JISHO[jisho[0]['word']] = jisho
        except OSError as inst: # not in jisho
          Jisho._JISHO[word] = "N"

      if Jisho._JISHO[word] == "N":
        return [None]
      else:
        return Jisho._JISHO[word]
