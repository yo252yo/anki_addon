from aqt import mw
from anki.importing import TextImporter
import codecs
import shutil
import time
from .anki import Anki
from .cardmaker import CardMaker
from .readfile import ReadFile
from .jisho import Jisho
from aqt.utils import showInfo
from .counters import Counters
from .string import String
from .dumps import Dumps

class Importer(object):
    VERBOSE = False

    def _makeOutputFileFromWords(filename, words, extra_tag=""):
        file = codecs.open('D:/Japanese/jap_anki/internal/' + filename, 'wb', 'utf-8')

        for word in words:
          for jisho in Jisho.getJisho(word):
              Counters.increment("new")
              Counters.increment("new:" + filename)
              Counters.increment("new_" + extra_tag)
              is_kana = False
              for tag in jisho['tags']:
                if "kana alone" in tag.lower():
                  is_kana = True

              if is_kana:
                file.write(jisho['word'].replace("\t", "") + "<br />" + jisho['pronunciation'].replace("\t", "") + '\t')
              else:
                file.write(jisho['word'].replace("\t", "") + '\t')
              file.write(jisho['definition'].replace("\t", "") + '\t')
              file.write(jisho['pronunciation'].replace("\t", "") + '\t')
              file.write(CardMaker.makeDetailsString(jisho['word'], is_kana).replace("\t", "") + '\t')

              file.write(jisho['ExtraPronounciations'].replace("\t", "") + '\t')
              file.write(jisho['ExtraMeanings'].replace("\t", "") + '\t')

              file.write(CardMaker.makeTagsString(jisho['word'], jisho, extra_tag).replace("\t", ""))
              file.write('\r\n')

        file.close()

    def _importFileToCards(file, model_name):
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

    def _importOutputFileToDeck(filename):
        file = ("D:/Japanese/jap_anki/internal/" + filename)
        try:
            Importer._importFileToCards(file, "Vocabulary cant write")
            Importer._importFileToCards(file, "Vocabulary")
        except:
            # "Error in import of .output to deck, probably because it doesn't have new words."
            i = 1
        time.sleep(1)
        mw.reset()
        Anki.cleanupDuplicates(filename)

    def _overwriteInputFile(filename, words):
        overwritten_file = 'D:/Japanese/jap_anki/' + filename
        copy_file = 'D:/Japanese/jap_anki/internal/copy_' + filename

        shutil.copyfile(overwritten_file, copy_file)
        file = codecs.open(overwritten_file, 'wb', 'utf-8')
        if not words:
            file.write(u'　')
        for word in words:
            file.write(word + ' ')
        file.close()

    def _processInNew(filename):
        words = ReadFile.fileToRawWords(filename)

        words_to_add = set()
        jisho_failures = set()
        deletions = set()

        for word in words:
            Counters.increment("in_new_processed")
            jisho = Jisho.getJisho(word)[0]
            if not jisho or 'word' not in jisho:
                card = Anki.getCardForWord(word)

                if card:
                    Anki.rescheduleCard(card)
                    Counters.increment("in_new_reschedfail")
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
                    deletions.add(word + str(len(card['cid'])))
                    words_to_add.add(real_word)

        Dumps.dump_strings("D:/Japanese/jap_anki/internal/.deletions.txt", deletions)
        return (words_to_add, jisho_failures)

    def _processInReview(filename):
        words = ReadFile.fileToRawWords(filename)

        words_to_add = set()

        for original_word in words:
            Counters.increment("in_review_processed")
            if Anki.rescheduleIfKanjis(original_word):
                continue
            card = Anki.getCardForWord(original_word)
            if card:
                Anki.rescheduleCard(card)
                Counters.increment("in_review_resched")
            else:
                # Resched our best guess
                real_word = Jisho.getJisho(original_word)[0]
                if real_word:
                    card = Anki.getCardForWord(real_word['word'])
                    if card:
                        Anki.rescheduleCard(card)
                        Counters.increment("in_review_resched")

                # Expand word
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
        return (words_to_add, [])

    def _importWords(input_file_name, output_file_name, words_to_add, jisho_failures):
        Importer._makeOutputFileFromWords(output_file_name, words_to_add, extra_tag="auto_freq")
        if Importer.VERBOSE:
            showInfo("Output made")
        Importer._importOutputFileToDeck(output_file_name)
        if Importer.VERBOSE:
            showInfo("Output imported")
        Importer._overwriteInputFile(input_file_name, jisho_failures)
        Counters.increment("in_new_jisho_failures", value=len(jisho_failures))

    def importInBothFiles():
        (words_to_add_new, jisho_failures_new) = Importer._processInNew('in_new.txt')
        if Importer.VERBOSE:
            showInfo("Transformed in_new")
        Importer._importWords('in_new.txt', 'output_in_new.txt', words_to_add_new, jisho_failures_new)
        (words_to_add_review, jisho_failures_review) = Importer._processInReview('in_review.txt')
        if Importer.VERBOSE:
            showInfo("Transformed in_review")
        Importer._importWords('in_review.txt', 'output_in_review.txt', words_to_add_review, jisho_failures_review)

        intersection = list(set(words_to_add_new) & set(words_to_add_review))
        Counters.increment("in_both_files", value=len(intersection))
