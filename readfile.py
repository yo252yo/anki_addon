import codecs
import csv

class ReadFile(object):
    kanjis = {}

    def _handleWordEncoding(word):
      if word.startswith(u'\ufeff'):
        word = word[1:]
      return word

    def fileToRawWords(file):
        f = codecs.open('D:/Japanese/jap_anki/' + file, 'rb', 'utf-8')
        words = set()
        for line in f:
          for rawline in line.split(' '):
              for rawword in rawline.split(u'　'):
                if not rawword or rawword == '' or rawword == ' ' or rawword == u'　':
                    continue
                word = ReadFile._handleWordEncoding(rawword).rstrip('\r\n')
                words.add(word)
        return words

    def getKanjisDict():
        if len(ReadFile.kanjis.keys()) > 0:
            return ReadFile.kanjis

        kanas = codecs.open('D:/Japanese/jap_anki/internal/kanas.txt', 'rb', 'utf-8')
        for kana in kanas:
          kana = ReadFile._handleWordEncoding(kana)
          k = kana[:1]
          d = kana[4:]
          ReadFile.kanjis[k] = d

        sim = codecs.open('D:/Japanese/jap_anki/dumps/graph_kanjis_details.txt', 'rb', 'utf-8')
        cr = csv.reader(sim)
        for row in cr:
          k = ReadFile._handleWordEncoding(row[0])
          d = ReadFile._handleWordEncoding(row[2]) + " (" + ReadFile._handleWordEncoding(row[1]) + ")"
          ReadFile.kanjis[k] = d
        sim.close()

        return ReadFile.kanjis
