#!/usr/bin/env python3
"""Print `region` shortcode lines for the maps (see AI.md, "Map").

    python3 tools/regions.py <world|middle-east|persia|india|aegean|scandinavia> <en|fa>

Every country, civilization, or reign layer drawn on a map is a ring of lon/lat
points here, re-derived against the map's own projection (same as genmaps.py,
padding included). Paste the printed line into that culture page's map body
(both languages):

    region points="47.5,32.9 ..." label="Mesopotamia" note="..."
            href="/cultures/mesopotamian/" era="lands" id="mesopotamia" color="gold" /

points are "x,y" pairs in % of the map image. Optional era filters with the map
era strip; id enables #pin-<id> deep links. Translate label/note pairs together.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmaps  # noqa: E402

PAD = 16  # the inset genmaps' project() uses inside the SVG

# map -> [ (key, label_en, label_fa, note_en, note_fa, href|None, ring[, era]) ]
# ring = 3+ (lon, lat) points in order, roughly hugging the region.
# Optional era (slug): lands | achaemenid | parthian | myth | … — omit for always-on.
# The map shortcode filters by era; "all" shows every layer.
R = {
    "world": [
        ("mesopotamia", "Mesopotamia", "بین‌النهرین",
         "Sumer, Akkad, Babylonia and Assyria, between the Tigris and Euphrates.",
         "سومر، اکد، بابل و آشور، میان دجله و فرات.",
         "/cultures/mesopotamian/",
         [(38.2, 36.8), (40.5, 37.4), (43.2, 37.6), (45.8, 36.8), (47.6, 35.6), (48.2, 33.8),
          (48.0, 31.6), (46.8, 29.8), (44.6, 28.6), (42.0, 28.8), (39.8, 30.2), (38.4, 32.2), (37.8, 34.4)]),
        ("persia", "Persia", "ایران",
         "The Iranian plateau, home of the Avesta and the Shahnameh.",
         "فلات ایران، سرزمین اوستا و شاهنامه.",
         "/cultures/iranian/",
         [(48.2, 37.6), (51.0, 38.4), (54.2, 38.6), (57.5, 38.0), (60.5, 36.6), (62.4, 34.2),
          (63.0, 31.4), (62.0, 28.6), (59.4, 26.2), (56.0, 25.4), (52.4, 26.4), (49.6, 28.6),
          (48.2, 31.2), (48.0, 34.4)]),
        ("greece", "Greece", "یونان",
         "The gods of Olympus and the heroes of Troy.",
         "خدایان المپ و قهرمانان تروا.",
         "/cultures/greek/",
         [(19.4, 41.0), (21.2, 41.8), (23.2, 42.0), (25.2, 41.4), (26.4, 40.2), (26.2, 38.4),
          (25.4, 36.6), (23.8, 35.6), (22.0, 35.6), (20.2, 36.6), (19.2, 38.2), (19.0, 39.6)]),
        ("india", "India", "هند",
         "The land of the Vedas and of the two great epics.",
         "سرزمین وداها و دو حماسهٔ بزرگ.",
         "/cultures/indian/",
         [(68.0, 32.4), (71.5, 33.6), (75.2, 34.0), (79.0, 32.2), (82.6, 29.6), (86.0, 26.6),
          (88.0, 24.0), (87.2, 21.0), (84.5, 17.5), (80.5, 12.5), (76.5, 13.5), (73.0, 17.0),
          (70.0, 20.5), (67.8, 24.0), (67.5, 28.0)]),
        ("north", "The North", "سرزمین شمال",
         "Norse myth and the Icelandic sagas.",
         "اسطوره‌های نورس و ساگاهای ایسلندی.",
         "/cultures/norse/",
         [(4.0, 57.5), (6.5, 59.5), (9.0, 61.5), (11.5, 64.0), (14.5, 67.0), (18.0, 69.5),
          (22.0, 70.8), (26.0, 71.0), (29.5, 69.5), (31.0, 67.0), (30.5, 64.0), (30.0, 61.0),
          (27.0, 58.5), (23.0, 57.0), (18.0, 55.5), (13.0, 55.0), (8.5, 55.2), (5.5, 56.2)]),
    ],
    "middle-east": [
        ("anatolia", "Anatolia", "آناتولی",
         "Mountain peninsula north of the Mediterranean (Asia Minor); Hittite and later Phrygian lands.",
         "شبه‌جزیرهٔ کوهستانی شمال مدیترانه (آسیای صغیر)؛ سرزمین هیتی و بعدها فریگیه.",
         None,
         [(26.5, 40.4), (29.0, 40.8), (32.0, 40.9), (35.5, 40.9), (38.5, 40.6), (41.5, 39.8),
          (43.5, 38.6), (44.0, 37.4), (42.0, 36.6), (38.5, 36.2), (34.5, 36.0), (31.0, 36.4),
          (28.5, 37.2), (26.8, 38.4), (26.4, 39.4)],
         "lands"),
        ("levant", "Levant", "شام",
         "Coast between Anatolia and Egypt — cedar country of the Gilgamesh epic and oldest trade roads.",
         "ساحل میان آناتولی و مصر — سرزمین سرو حماسهٔ گیلگمش و کهن‌ترین راه‌های تجاری.",
         None,
         [(34.4, 36.8), (36.0, 36.8), (37.6, 36.5), (38.4, 35.2), (38.5, 33.8), (37.8, 32.4),
          (36.8, 31.4), (35.6, 30.9), (34.4, 31.2), (33.6, 32.0), (33.2, 33.2), (33.4, 34.6), (33.8, 35.8)],
         "lands"),
        ("mesopotamia", "Mesopotamia", "بین‌النهرین",
         "Land between the Tigris and Euphrates — Sumer, Akkad, Babylon and Assyria.",
         "سرزمین میان دجله و فرات — سومر، اکد، بابل و آشور.",
         "/cultures/mesopotamian/",
         [(38.4, 37.6), (40.8, 37.8), (43.2, 37.6), (45.6, 36.8), (47.4, 35.6), (48.2, 33.6),
          (48.2, 31.6), (47.0, 30.2), (44.8, 29.4), (42.4, 29.8), (40.4, 31.0), (39.0, 32.8),
          (38.2, 34.6), (38.2, 36.2)],
         "lands"),
        ("arabia", "Arabia", "عربستان",
         "Desert peninsula south of the Fertile Crescent; incense roads ran its western edge.",
         "شبه‌جزیرهٔ بیابانی جنوبِ هلال حاصلخیز؛ راه‌های بخور از لبهٔ باختری‌اش می‌گذشت.",
         None,
         [(34.8, 29.6), (37.5, 30.4), (40.5, 30.9), (43.5, 30.4), (46.5, 29.4), (49.5, 28.0),
          (52.5, 26.2), (55.0, 25.0), (57.0, 24.0), (54.5, 23.4), (50.5, 23.3), (46.0, 23.3),
          (41.5, 23.4), (37.5, 24.2), (35.2, 26.0), (34.5, 27.8)],
         "lands"),
        ("persia", "Persia", "ایران",
         "Plateau east of the Zagros — Avestan and Shahnameh country, neighbour to the two rivers.",
         "فلات شرق زاگرس — سرزمین اوستا و شاهنامه، همسایهٔ دو رود.",
         "/cultures/iranian/",
         [(48.2, 37.4), (50.5, 38.2), (53.0, 38.5), (55.5, 37.8), (57.5, 36.4), (59.0, 34.2),
          (59.5, 31.6), (59.5, 28.8), (58.0, 26.6), (55.5, 25.4), (52.5, 26.2), (50.2, 28.0),
          (48.6, 30.4), (48.0, 32.8), (48.0, 35.2)],
         "lands"),
        ("assyria", "Assyrian heartland", "قلب آشور",
         "Upper Tigris — Assur, Nineveh and Kalhu; Neo-Assyrian power (c. 900–612 BCE).",
         "بالادست دجله — آشور، نینوا و کالح؛ قدرت آشور نو (حدود ۹۰۰–۶۱۲ پ.م).",
         "/cultures/mesopotamian/",
         [(41.5, 37.2), (43.5, 37.4), (45.5, 37.0), (46.5, 35.8), (46.0, 34.2), (44.5, 33.4),
          (42.5, 33.6), (41.2, 34.8), (41.0, 36.2)],
         "assyrian"),
    ],
    "persia": [
        ("media", "Media", "ماد",
         "Highlands of the Medes; Ecbatana (Hamadan) is their legendary capital in Greek and Iranian memory.",
         "ارتفاعات مادها؛ اکباتان (همدان) پایتخت افسانه‌ای‌شان در یاد ایرانی و یونانی است.",
         None,
         [(44.4, 37.4), (46.2, 38.2), (48.0, 38.5), (49.8, 38.0), (51.0, 36.8), (51.5, 35.2),
          (51.2, 33.6), (50.0, 32.2), (48.4, 31.8), (46.6, 32.4), (45.2, 33.6), (44.4, 35.2), (44.2, 36.4)],
         "lands"),
        ("persia", "Persia", "پارس",
         "Fars — Persis — heartland of the Achaemenids; Persepolis and Pasargadae stand here.",
         "فارس — پارس — قلب هخامنشیان؛ تخت جمشید و پاسارگاد این‌جا برپاست.",
         "/cultures/iranian/",
         [(49.0, 32.4), (50.6, 32.8), (52.2, 33.0), (53.8, 33.3), (55.2, 33.2), (56.4, 32.0),
          (57.0, 30.4), (56.8, 28.8), (56.2, 27.4), (54.4, 26.6), (52.4, 26.5), (50.6, 27.4),
          (49.4, 28.6), (48.8, 30.0), (48.8, 31.4)],
         "lands"),
        ("parthia", "Parthia", "پارت",
         "North-eastern march that later gave the Arsacid (Parthian) dynasty its name.",
         "مرز شمال‌شرقی که بعدها نام دودمان اشکانی (پارتی) از آن آمد.",
         None,
         [(53.8, 38.2), (55.6, 38.8), (57.6, 39.0), (59.8, 38.8), (61.6, 37.8), (62.8, 36.4),
          (63.0, 34.8), (61.8, 33.6), (60.0, 33.2), (58.0, 33.8), (56.2, 34.6), (54.6, 35.4),
          (53.6, 36.4), (53.6, 37.4)],
         "lands"),
        ("aria", "Aria", "آریا",
         "Eastern highlands around Herat (Haraiva); a satrapy on the road to India.",
         "ارتفاعات شرقی پیرامون هرات (هَرَیو)؛ ساتراپی بر راه هند.",
         None,
         [(59.8, 35.8), (61.4, 36.4), (63.2, 36.6), (65.0, 36.2), (66.4, 35.2), (67.0, 33.6),
          (66.8, 32.0), (65.6, 30.8), (64.0, 30.4), (62.2, 30.8), (60.8, 31.8), (59.8, 33.0),
          (59.6, 34.4)],
         "lands"),
        ("transoxiana", "Transoxiana", "فرارود",
         "Beyond the Oxus (Amu Darya) — Sogdiana and the eastern edge of the Iranian world.",
         "آن‌سوی جیحون (آمودریا) — سغد و شرقی‌ترین بخش جهان ایرانی.",
         None,
         [(62.4, 39.4), (64.2, 39.8), (66.0, 39.8), (67.8, 39.4), (69.2, 38.6), (69.5, 37.4),
          (69.2, 36.6), (67.6, 36.2), (65.8, 36.2), (64.0, 36.6), (62.8, 37.4), (62.4, 38.4)],
         "lands"),
        # Schematic reign outlines (clipped to this map's plateau frame).
        ("achaemenid", "Achaemenid realm", "قلمرو هخامنشی",
         "c. 550–330 BCE — from the Zagros to the Oxus on this frame; the empire reached far beyond.",
         "حدود ۵۵۰–۳۳۰ پ.م — از زاگرس تا جیحون در این قاب؛ امپراتوری بسیار فراتر می‌رفت.",
         "/cultures/iranian/history/zoroastrianism-in-persia/",
         [(43.2, 38.2), (48.0, 39.0), (54.0, 39.2), (60.0, 38.8), (66.0, 37.8), (70.0, 36.0),
          (71.0, 33.0), (70.5, 29.5), (67.0, 26.5), (60.0, 25.5), (52.0, 26.0), (46.0, 27.5),
          (43.5, 30.5), (43.0, 34.5)],
         "achaemenid"),
        ("parthian-realm", "Parthian realm", "قلمرو اشکانی",
         "c. 247 BCE–224 CE — Arsacid power centred on Parthia and Media, reaching Mesopotamia west of this map.",
         "حدود ۲۴۷ پ.م–۲۲۴ م — قدرت اشکانی بر پارت و ماد، با میان‌رودان در باختر این نقشه.",
         None,
         [(47.5, 38.0), (53.0, 38.8), (59.0, 38.6), (65.0, 37.5), (68.5, 35.5), (68.0, 32.5),
          (64.0, 30.5), (58.0, 30.0), (52.0, 31.0), (48.0, 33.0), (47.0, 35.5)],
         "parthian"),
    ],
    "india": [
        ("himalaya", "Himalaya", "هیمالیا",
         "The mountain wall of the north, sacred across Indian traditions.",
         "دیوار بزرگ کوهستان شمال، مقدس در سنت‌های هندی.",
         None,
         [(66.0, 33.4), (70.0, 33.2), (74.0, 32.6), (78.0, 31.4), (82.0, 30.2), (86.0, 28.8),
          (90.0, 27.6), (94.0, 27.0), (97.0, 26.6), (97.0, 28.6), (93.0, 29.2), (90.0, 29.8),
          (86.0, 30.8), (82.0, 32.2), (78.0, 33.2), (74.0, 34.2), (70.0, 34.6), (66.0, 35.0)]),
        ("thar", "Thar Desert", "صحرای تار",
         "The great desert between the Indus and the Ganges.",
         "بیابان بزرگ میان سند و گنگ.",
         None,
         [(69.0, 29.6), (71.0, 29.4), (73.0, 29.0), (74.2, 27.4), (74.5, 26.0), (74.0, 24.4),
          (73.0, 23.0), (71.4, 23.2), (70.0, 23.6), (68.8, 24.8), (68.5, 26.2), (68.6, 28.0)]),
        ("ganges", "Gangetic Plain", "دشت گنگ",
         "The river plain of Hastinapur, Varanasi and the epic kingdoms.",
         "دشت رود گنگ، سرزمین هستیناپور، واراناسی و پادشاهی‌های حماسی.",
         "/cultures/indian/",
         [(75.0, 30.0), (77.5, 29.4), (81.0, 28.4), (84.0, 27.4), (87.0, 26.4), (89.5, 25.4),
          (91.0, 24.8), (90.4, 23.8), (89.0, 23.4), (86.0, 23.4), (84.0, 23.6), (81.0, 24.4),
          (78.0, 25.6), (75.8, 26.6), (74.5, 27.4), (74.4, 28.8)]),
        ("bengal", "Bengal", "بنگال",
         "The wide delta where the Ganges meets the sea.",
         "دلتای پهناور که گنگ به دریا می‌ریزد.",
         None,
         [(88.2, 23.2), (90.0, 23.2), (92.0, 22.8), (93.0, 21.6), (93.0, 20.6), (92.0, 19.4),
          (90.5, 18.4), (89.0, 19.0), (88.0, 20.0), (87.2, 21.0), (87.0, 21.6), (87.4, 22.6)]),
        ("deccan", "Deccan", "دکن",
         "The plateau that fills the southern peninsula.",
         "فلاتی که شبه‌قارهٔ جنوبی را پر می‌کند.",
         None,
         [(73.5, 21.0), (75.5, 20.0), (77.0, 19.0), (78.5, 18.0), (80.0, 17.0), (81.2, 15.4),
          (82.0, 14.0), (81.4, 12.6), (80.0, 11.5), (78.0, 12.0), (76.0, 13.0), (74.4, 14.6),
          (73.0, 16.0), (72.0, 17.6), (71.5, 19.0), (72.2, 20.2)]),
    ],
    "aegean": [
        ("greece", "Greece", "یونان",
         "Mountain and island: Olympus, Delphi, Athens.",
         "کوه و جزیره: المپ، دلفی و آتن.",
         "/cultures/greek/",
         [(19.5, 41.4), (20.5, 41.5), (21.5, 41.4), (22.4, 40.9), (23.2, 40.2), (23.8, 39.2),
          (24.0, 38.2), (23.6, 37.2), (22.8, 36.5), (21.8, 36.8), (21.0, 37.5), (20.2, 38.4),
          (19.4, 39.2), (19.2, 40.2), (19.2, 41.0)]),
        ("thrace", "Thrace", "تراکیه",
         "The land north of the Aegean and the Hellespont.",
         "سرزمین شمال اژه و هلسپونت.",
         None,
         [(24.5, 42.6), (25.8, 42.9), (27.0, 43.0), (28.0, 42.6), (28.6, 41.8), (28.2, 41.0),
          (27.0, 40.8), (25.8, 40.9), (24.8, 41.4), (24.4, 42.0)]),
        ("anatolia", "Anatolia", "آناتولی",
         "The coast across the Aegean, home of Troy and the Ionian cities.",
         "ساحل آن‌سوی اژه، سرزمین تروا و شهرهای یونیایی.",
         None,
         [(26.5, 40.6), (28.5, 41.2), (31.0, 41.5), (33.5, 41.5), (36.0, 41.4), (37.8, 40.6),
          (38.6, 39.4), (38.6, 38.0), (38.2, 36.8), (36.5, 36.4), (33.5, 36.4), (31.0, 36.4),
          (28.5, 36.8), (27.0, 37.6), (26.2, 38.8), (26.2, 39.8)]),
        ("crete", "Crete", "کرت",
         "The island of Knossos and the Minotaur's labyrinth.",
         "جزیرهٔ کنوسوس و هزارتوی مینوتاور.",
         None,
         [(23.4, 35.6), (24.2, 35.7), (25.0, 35.7), (25.8, 35.5), (26.4, 35.3), (26.2, 34.9),
          (26.0, 34.7), (25.0, 34.7), (24.0, 34.7), (23.4, 34.9), (23.3, 35.1), (23.3, 35.4)]),
        ("cyprus", "Cyprus", "قبرس",
         "The island south of Anatolia, sacred to Aphrodite.",
         "جزیرهٔ جنوب آناتولی، مقدس برای آفرودیت.",
         None,
         [(32.2, 35.2), (33.0, 35.4), (34.0, 35.4), (34.5, 35.0), (34.5, 34.7), (33.8, 34.4),
          (33.0, 34.3), (32.4, 34.5), (32.2, 34.7), (32.1, 35.0)]),
    ],
    "scandinavia": [
        ("scandinavia", "Scandinavia", "اسکاندیناوی",
         "Norway and Sweden: the saga coast of the North.",
         "نروژ و سوئد: ساحل ساگاهای شمال.",
         "/cultures/norse/",
         [(6.6, 58.1), (8.5, 61), (11, 63.5), (13.5, 66), (16.5, 68.5), (19, 70.3), (22, 71), (24.5, 70.8), (25.5, 69.5), (24, 67), (23.6, 64), (24, 60.8), (21.5, 59.6), (19, 58.4), (16.5, 56.6), (13.5, 55.5), (12.4, 55.4), (11.6, 57.5), (9.6, 58.9), (7.6, 57.9)]),
        ("denmark", "Denmark", "دانمارک",
         "The straits and islands between the North Sea and the Baltic.",
         "تنگه‌ها و جزایر میان دریای شمال و بالتیک.",
         None,
         [(8.1, 56.5), (8.6, 57.7), (10.6, 57.6), (10.8, 56), (12.6, 55.6), (12.4, 54.6), (10, 54.5), (8.3, 55.1)]),
        ("finland", "Finland", "فنلاند",
         "The lakes and forests east of the Bothnian Gulf.",
         "دریاچه‌ها و جنگل‌های شرق خلیج بوتنیا.",
         None,
         [(24.2, 60.6), (26, 62), (27.5, 64), (29, 66), (29, 68), (27.5, 70.2), (25.6, 69.6), (24.4, 67), (23.8, 64), (23.9, 61.5)]),
        ("karelia", "Karelia", "کارلیا",
         "The forest land east of Finland.",
         "سرزمین جنگلی شرق فنلاند.",
         None,
         [(29.4, 62.4), (31.5, 62.8), (33, 65), (32, 68), (30.2, 69), (29.4, 66)]),
        ("iceland", "Iceland", "ایسلند",
         "The island where the sagas were written down.",
         "جزیره‌ای که ساگاهای نورس در آن نوشته شدند.",
         None,
         [(-24, 63.6), (-20.4, 65), (-16.6, 66.5), (-14.2, 65.6), (-15.6, 64.4), (-19, 63.6), (-22.4, 63.5)]),
        ("britain", "Britain", "بریتانیا",
         "The islands west of the North Sea.",
         "جزایر باختر دریای شمال.",
         None,
         [(-6, 55.4), (-3, 56), (0.4, 55.4), (1.5, 53), (1.1, 51.7), (-1.4, 51.7), (-4, 51.7), (-5.8, 52.6), (-6, 54.4)]),
        ("gallia", "Gallia", "گالیا",
         "The continental shore south of the North Sea.",
         "ساحل قاره‌ای جنوب دریای شمال.",
         None,
         [(1.6, 53.5), (4.6, 53.3), (7.6, 52.6), (8, 51.1), (4.6, 51.1), (2.1, 51.4), (1.5, 52.5)]),
    ],
}


def pct_art(lon, lat, box, w):
    """% of the SVG image, matching genmaps' projection (which insets by PAD)."""
    lonspan, latspan = box[1] - box[0], box[3] - box[2]
    h = int(2 * PAD + latspan / lonspan * (w - 2 * PAD))
    fx = (lon - box[0]) / lonspan
    fy = (box[3] - lat) / latspan
    return ((PAD + fx * (w - 2 * PAD)) / w * 100,
            (PAD + fy * (h - 2 * PAD)) / h * 100)


def unpack(row):
    """(key, le, lf, ne, nf, href, ring) or same + era slug."""
    if len(row) == 8:
        return row
    if len(row) == 7:
        return row + ("",)
    raise ValueError("bad region row length %d" % len(row))


ERA_COLOR = {
    "achaemenid": "teal",
    "parthian": "silver",
    "assyrian": "blood",
    "myth": "fire",
}


def line(row, box, w, lang):
    key, le, lf, ne, nf, href, ring, era = unpack(row)
    label, note = (le, ne) if lang == "en" else (lf, nf)
    pts = " ".join("%.1f,%.1f" % pct_art(lo, la, box, w) for lo, la in ring)
    h = ' href="%s"' % href if href else ""
    e = ' era="%s"' % era if era else ""
    i = ' id="%s"' % key
    color = ERA_COLOR.get(era, "gold")
    return 'region points="%s" label="%s" note="%s"%s%s%s color="%s" /' % (
        pts, label, note, h, e, i, color)


def lines_for(name, lang):
    spec = genmaps.MAPS[name]
    return [line(row, spec["box"], spec["w"], lang) for row in R[name]]


if __name__ == "__main__":
    for out in lines_for(sys.argv[1], sys.argv[2]):
        print(out)
