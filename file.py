
import codecs

class File(object):
    def handleWordEncoding(word):
      if word.startswith(u'\ufeff'):
        word = word[1:]
      return word

    def fileToRawWords(file):
        f = codecs.open('D:/Japanese/jap_anki/internal/' + file, 'rb', 'utf-8')
        words = set()
        for line in f:
          for rawline in line.split(' '):
              for rawword in rawline.split(u'　'):
                if not rawword or rawword == '' or rawword == ' ' or rawword == u'　':
                    continue
                word = File.handleWordEncoding(rawword).rstrip('\r\n')
                words.add(word)

        return words

    #def getKanjisDict():
    #    kanjis = {}
    #    sim = codecs.open('D:/Japanese/jap_anki/dumps/kanjis_details.txt', 'rb', 'utf-8')
    #    cr = csv.reader(sim)
    #    for row in cr:
    #      k = File.handleWordEncoding(row[0])
    #      d = File.handleWordEncoding(row[2]) + " (" + File.handleWordEncoding(row[1]) + ")"
    #      kanjis[k] = d
    #    sim.close()
    #    return kanjis


    # OLD VERSION, REPLACE BY THE ABOVE
    def getKanjisDict():
        kanjis = {}
        sim = codecs.open('D:/Japanese/jap_anki/dumps/kanjis_old.txt', 'rb', 'utf-8')
        for kanji in sim:
          kanji = File.handleWordEncoding(kanji)
          k = kanji[:1]
          d = kanji[4:]
          kanjis[k] = d
        sim.close()
        return kanjis
