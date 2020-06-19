from aqt import mw
from anki.importing import TextImporter
from .anki import Anki
from .file import File
from .jisho import Jisho
import codecs
from .counters import Counters
from .string import String

class Output(object):
    def cleanupDuplicates():

        ids = mw.col.findNotes("(mid:1432900443242 -Details:*$* -Details:) or (mid:1432882338168 $)")
        Counters.increment("dupe_cleaned", value=len(ids))
        mw.col.remNotes(ids)

    def importFileToModel(model_name, file):
        deck_id = mw.col.decks.id(":Expressions")
        mw.col.decks.select(deck_id)

        m = mw.col.models.byName(model_name)
        deck = mw.col.decks.get(deck_id)

        deck['mid'] = m['id']
        mw.col.decks.save(deck)
        m['did'] = deck_id

        importer = TextImporter(mw.col, file)
        importer.allowHTML = True
        importer.initMapping()
        importer.run()


    def importOutputFileToDeck():
        file = u"D:\Japanese\jap_anki\internal\.output.txt"
        try:
            Output.importFileToModel("Vocabulary cant write", file)
            Output.importFileToModel("Vocabulary", file)
        except:
            # "Error in import of .output to deck, probably because it doesn't have new words."
            i = 1
        Output.cleanupDuplicates()



    def printDetails(word, kana):
      kanjis = File.getKanjisDict()
      details = ""
      for k in word:
        try:
          details = details + k + " - " + kanjis[k] + "<br />"
        except:
          if kana:
            details = details + ".<br />"
          else:
            details = details + "$<br />"

      roots = Anki.findRootWords(word)
      if len(roots) > 0:
        for root in roots:
          details = details + "<br /> " + root + " " + roots[root]

      return details.replace('\r\n','')

    def printTags(word, jisho, extra_tag=""):
      tagsString = 'AG2 ' + extra_tag + ' '
      tagsString += 'kanji' + str(String.countKanjis(word)) + ' '
      if jisho['is_common']:
        tagsString = tagsString + 'COMMON '
      if len(Anki.findRootWords(word)) > 0:
        tagsString = tagsString + 'auto_compound '
      for tag in jisho['tags']:
        if "kana alone" in tag.lower():
          tagsString = tagsString + 'KANA '
        if "onomato" in tag.lower():
          tagsString = tagsString + 'ONOM '

      return tagsString

    def makeOutputFileFromData(words, extra_tag=""):

        Counters.increment("new", value=len(words))

        file = codecs.open('D:/Japanese/jap_anki/internal/.output.txt', 'wb', 'utf-8')

        for word in words:
          for jisho in Jisho.getJisho(word):
              is_kana = False
              for tag in jisho['tags']:
                if "kana alone" in tag.lower():
                  is_kana = True

              file.write(jisho['definition'].replace("\t", "") + '\t')
              if is_kana:
                file.write(jisho['word'].replace("\t", "") + "<br />" + jisho['pronunciation'].replace("\t", "") + '\t')
              else:
                file.write(jisho['word'].replace("\t", "") + '\t')
              file.write(jisho['pronunciation'].replace("\t", "") + '\t')
              file.write(Output.printDetails(jisho['word'], is_kana).replace("\t", "") + '\t')

              file.write(jisho['ExtraPronounciations'].replace("\t", "") + '\t')
              file.write(jisho['ExtraMeanings'].replace("\t", "") + '\t')

              file.write(Output.printTags(jisho['word'], jisho, extra_tag).replace("\t", ""))
              file.write('\r\n')

        file.close()

    def overwriteInputFile(file, words):
        file = codecs.open('D:/Japanese/jap_anki/internal/' + file, 'wb', 'utf-8')
        if not words:
            file.write(u'　')
        for word in words:
            file.write(word + ' ')
        file.close()


    def importInNew():

        words = File.fileToRawWords('in_new.txt')

        words_to_add = set()
        jisho_failures = set()

        for word in words:
            Counters.increment("in_new_processed")
            jisho = Jisho.getJisho(word)[0]
            if not jisho or 'word' not in jisho:
                card = Anki.getCardForWord(word)

                if card:
                    Anki.rescheduleCard(card)
                    jisho_failures.add(word + "*")
                else:
                    jisho_failures.add(word)
                continue


            real_word = jisho['word']

            card = Anki.getCardForWord(real_word)
            if not card:
                Counters.increment("in_new_new")
                words_to_add.add(real_word)
            else:
                if card['is_sink']:
                    Counters.increment("in_new_sinks")
                elif card['is_manual']:
                    Counters.increment("in_new_manual")
                    Anki.rescheduleCard(card)
                else:
                    Counters.increment("in_new_renew")
                    Anki.deleteCard(card)
                    words_to_add.add(real_word)


        Output.makeOutputFileFromData(words_to_add, extra_tag="auto_freq")
        Output.importOutputFileToDeck()
        Output.overwriteInputFile('in_new.txt', jisho_failures)
        Counters.increment("in_new_jisho_failures", value=len(jisho_failures))


    def importInReview():

        words = File.fileToRawWords('in_review.txt')

        words_to_add = set()

        for original_word in words:
            Counters.increment("in_review_processed")
            if Anki.rescheduleKanjis(original_word):
                continue
            card = Anki.getCardForWord(original_word)
            if card:
                Anki.rescheduleCard(card)
                Counters.increment("in_review_resched")
            else:
                words_expanded = String.expandToSubwords(original_word)
                for word in words_expanded:
                    card = Anki.getCardForWord(word)
                    if not card:
                        jisho = Jisho.getJisho(word)[0]
                        if jisho:
                            card = Anki.getCardForWord(jisho['word'])
                            if not card:
                                Counters.increment("in_review_new")
                                words_to_add.add(jisho['word'])

        Output.makeOutputFileFromData(words_to_add)
        Output.importOutputFileToDeck()
        Output.overwriteInputFile('in_review.txt', [])
