import codecs
import csv
from .readfile import ReadFile
from anki.importing import TextImporter
from aqt import mw
import time

class KanjiImporter(object):
  VERBOSE = False
  KANJIFILE = 'D:/Japanese/jap_anki/internal/kanjisImport.txt'
  KANJISIMFILE = 'D:/Japanese/jap_anki/internal/kanjisSimImport.txt'
  KANJIVERSION = "KJ1"
  KANJISIMVERSION = "KJS4"

  def _makeKanjiFile():
    kanjis = codecs.open('D:/Japanese/jap_anki/dumps/graph_kanjis_details.txt', 'rb', 'utf-8')
    cr = csv.reader(kanjis)
    file = codecs.open(KanjiImporter.KANJIFILE, 'wb', 'utf-8')
    i = 0
    for row in cr:
      if i == 0:
          i = i + 1
          continue
      file.write(ReadFile._handleWordEncoding(row[0]).replace("\t", "") + '\t')
      file.write(ReadFile._handleWordEncoding(row[1]).replace("\t", "") + '\t')
      file.write(ReadFile._handleWordEncoding(row[2]).replace("\t", "") + '\t')
      file.write(ReadFile._handleWordEncoding(row[3]).replace("\t", "") + '\t')
      file.write('"'+ReadFile._handleWordEncoding(row[4]).replace("\t", "").replace("\n", "<br/>") + '"\t')
      file.write(KanjiImporter.KANJIVERSION + '\r\n')
    kanjis.close()
    file.close()

  def _importKanjiFile():
        deck_id = mw.col.decks.id(":Kanjis")
        mw.col.decks.select(deck_id)

        m = mw.col.models.byName("Kanji")
        deck = mw.col.decks.get(deck_id)

        deck['mid'] = m['id']
        mw.col.decks.save(deck)
        m['did'] = deck_id

        importer = TextImporter(mw.col, KanjiImporter.KANJIFILE)
        importer.allowHTML = True
        importer.initMapping()
        importer.run()

        time.sleep(1)
        mw.reset()

  def importKanjis():
    KanjiImporter._makeKanjiFile()
    KanjiImporter._importKanjiFile()

  def _makeKanjiSimFile():
    kanjis = codecs.open('D:/Japanese/jap_anki/dumps/graph_kanjis_sim.txt', 'rb', 'utf-8')
    cr = csv.reader(kanjis)
    file = codecs.open(KanjiImporter.KANJISIMFILE, 'wb', 'utf-8')
    i = 0
    for row in cr:
      if i == 0:
          i = i + 1
          continue
      file.write(ReadFile._handleWordEncoding(row[0]).replace("\t", "") + '<br>')
      file.write(ReadFile._handleWordEncoding(row[1]).replace("\t", "") + '<br>')
      file.write(ReadFile._handleWordEncoding(row[2]).replace("\t", "") + '<br>\t')

      file.write(ReadFile._handleWordEncoding(row[4]).replace("\t", "") + '<br>')
      file.write(ReadFile._handleWordEncoding(row[5]).replace("\t", "") + '<br>')
      file.write(ReadFile._handleWordEncoding(row[6]).replace("\t", "") + '<br>\t')

      file.write(KanjiImporter.KANJISIMVERSION + '\r\n')
    kanjis.close()
    file.close()

  def _importKanjiSimFile():
        deck_id = mw.col.decks.id(":KanjiSim")
        mw.col.decks.select(deck_id)

        m = mw.col.models.byName("Kanjisim")
        deck = mw.col.decks.get(deck_id)

        deck['mid'] = m['id']
        mw.col.decks.save(deck)
        m['did'] = deck_id

        importer = TextImporter(mw.col, KanjiImporter.KANJISIMFILE)
        importer.allowHTML = True
        importer.initMapping()
        importer.run()

        time.sleep(1)
        mw.reset()

  def importKanjisSim():
    KanjiImporter._makeKanjiSimFile()
    KanjiImporter._importKanjiSimFile()
