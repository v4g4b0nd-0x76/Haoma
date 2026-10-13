#!/usr/bin/env python3
"""Print `region` shortcode lines for the maps (see AI.md, "Map").

    python3 tools/regions.py <world|middle-east|persia|india|aegean|scandinavia> <en|fa>

Every country or civilization drawn on a map is a ring of lon/lat points here, so
it re-derives against the map's own projection - the same projection
tools/genmaps.py draws the coast with, padding included.  Paste the printed line
into that culture page's map shortcode body (both languages):

    region points="47.5,32.9 48.7,32.1 ..." label="Mesopotamia" note="..."
            href="/cultures/mesopotamian/" color="gold" /

points are "x,y" pairs in % of the map image, three or more, in order.  href is
the culture's own page (the shortcode applies the language prefix); leave it off
and the region is hover-only.  Note and label live in one table entry so English
and Farsi stay in step: translate the pair, never just one of them.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmaps  # noqa: E402

PAD = 16  # the inset genmaps' project() uses inside the SVG

# map -> [ (key, label_en, label_fa, note_en, note_fa, href|None, ring) ]
# ring = 3+ (lon, lat) points in order, roughly hugging the region.
R = {
    "world": [
        ("mesopotamia", "Mesopotamia", "بین‌النهرین",
         "Sumer, Akkad, Babylonia and Assyria, between the Tigris and Euphrates.",
         "سومر، اکد، بابل و آشور، میان دجله و فرات.",
         "/cultures/mesopotamian/",
         [(38.5, 36.5), (43, 37.5), (47.5, 36), (48, 30.5), (44, 28.5), (39.5, 30), (37.5, 33)]),
        ("persia", "Persia", "ایران",
         "The Iranian plateau, home of the Avesta and the Shahnameh.",
         "فلات ایران، سرزمین اوستا و شاهنامه.",
         "/cultures/iranian/",
         [(48.5, 37.5), (54, 38.5), (61, 37), (63, 30), (58, 25.5), (51, 27), (48, 32)]),
        ("greece", "Greece", "یونان",
         "The gods of Olympus and the heroes of Troy.",
         "خدایان المپ و قهرمانان تروا.",
         "/cultures/greek/",
         [(19.5, 41), (23, 42), (26.5, 41), (26, 36), (22.5, 35.5), (19, 37.5)]),
        ("india", "India", "هند",
         "The land of the Vedas and of the two great epics.",
         "سرزمین وداها و دو حماسهٔ بزرگ.",
         "/cultures/indian/",
         [(68, 32.5), (75, 34), (83, 30), (88, 25), (86, 19), (79, 11), (73, 17), (67.5, 23)]),
        ("north", "The North", "سرزمین شمال",
         "Norse myth and the Icelandic sagas.",
         "اسطوره‌های نورس و ساگاهای ایسلندی.",
         "/cultures/norse/",
         [(4, 57.5), (9, 61.5), (13, 66), (19, 70.5), (27, 71), (31, 67), (30, 61), (24, 57.5), (15, 55), (7, 55)]),
    ],
    "middle-east": [
        ("anatolia", "Anatolia", "آناتولی",
         "The mountainous peninsula north of the Mediterranean, later called Asia Minor.",
         "شبه‌جزیرهٔ کوهستانی شمال مدیترانه که بعدها آسیای صغیر خوانده شد.",
         None,
         [(26.5, 40.5), (32, 40.9), (38, 40.9), (43, 39.5), (44, 37.5), (40, 36.5), (34, 36), (29, 36.8), (26.5, 38.5)]),
        ("levant", "Levant", "شام",
         "The coast between Anatolia and Egypt, crossed by the oldest trade roads.",
         "ساحل میان آناتولی و مصر، با کهن‌ترین راه‌های تجاری.",
         None,
         [(34.5, 36.8), (37.6, 36.6), (38.5, 34), (37.5, 31.5), (35.6, 31), (33.8, 31.4), (33.3, 33), (33.6, 35.5)]),
        ("mesopotamia", "Mesopotamia", "بین‌النهرین",
         "The plain between the Tigris and Euphrates; the first cities rose here.",
         "دشت میان دجله و فرات؛ نخستین شهرها در همین‌جا برخاستند.",
         "/cultures/mesopotamian/",
         [(38.6, 37.6), (43, 37.6), (47.6, 36.2), (48.2, 30.4), (44.4, 29.4), (40.4, 31), (38.4, 34.2)]),
        ("arabia", "Arabia", "عربستان",
         "The desert peninsula south of the Fertile Crescent.",
         "شبه‌جزیرهٔ بیابانی جنوبِ هلال حاصلخیز.",
         None,
         [(34.8, 29.6), (40, 30.9), (45.5, 30), (50.5, 27.5), (55, 25), (57, 24), (52, 23.3), (44, 23.3), (38.5, 23.3), (35.5, 25.5), (34.5, 27.5)]),
        ("persia", "Persia", "ایران",
         "The plateau east of the Zagros, the wider Iranian world.",
         "فلات شرق زاگرس، جهان پهناور ایرانی.",
         "/cultures/iranian/",
         [(48.4, 37.5), (53, 38.5), (57, 37), (59.5, 33), (59.5, 27), (55, 25.5), (51.5, 27.5), (48.6, 30.5), (48.2, 34)]),
    ],
    "persia": [
        ("media", "Media", "ماد",
         "The north-western highlands, home of Ecbatana (Hamadan).",
         "ارتفاعات شمال‌غربی، سرزمین اکباتان (همدان).",
         None,
         [(44.5, 37.5), (48, 38.5), (51, 37.5), (51.5, 34.5), (49.5, 32), (46.5, 32.5), (44.5, 35)]),
        ("persia", "Persia", "پارس",
         "The southern heartland of Fars, where Persepolis stands.",
         "قلب جنوبی فارس، جایی که تخت جمشید برپاست.",
         "/cultures/iranian/",
         [(49, 32.4), (52, 33), (55, 33.5), (57, 31), (56.5, 27.5), (52.5, 26.5), (49.5, 28.5), (48.8, 30.5)]),
        ("parthia", "Parthia", "پارت",
         "The north-eastern march, later the realm of the Parthians.",
         "مرز شمال‌شرقی، بعدها قلمرو پارتیان.",
         None,
         [(54, 38.5), (58, 39), (62, 38.5), (63, 35.5), (60, 33.5), (56.5, 34.5), (53.5, 35.5)]),
        ("aria", "Aria", "آریا",
         "The eastern highlands around Herat.",
         "ارتفاعات شرقی پیرامون هرات.",
         None,
         [(60, 36), (63.5, 36.5), (66.5, 35.5), (67, 32), (64, 30.5), (61, 31.5), (59.8, 33.5)]),
        ("transoxiana", "Transoxiana", "فرارود",
         "The plain beyond the Oxus (Amu Darya), the eastern edge of the Iranian world.",
         "دشت آن‌سوی جیحون (آمودریا)، شرقی‌ترین بخش جهان ایرانی.",
         None,
         [(62.5, 39.6), (66, 39.8), (69.5, 39), (69.5, 36.6), (66, 36.2), (63, 37)]),
    ],
    "india": [
        ("himalaya", "Himalaya", "هیمالیا",
         "The mountain wall of the north, sacred across Indian traditions.",
         "دیوار بزرگ کوهستان شمال، مقدس در سنت‌های هندی.",
         None,
         [(66, 33.4), (74, 32.6), (82, 30.2), (90, 27.6), (97, 26.6), (97, 28.6), (90, 29.8), (82, 32.2), (74, 34.2), (66, 35)]),
        ("thar", "Thar Desert", "صحرای تار",
         "The great desert between the Indus and the Ganges.",
         "بیابان بزرگ میان سند و گنگ.",
         None,
         [(69, 29.6), (73, 29), (74.5, 26), (73, 23), (70, 23.6), (68.5, 26.2)]),
        ("ganges", "Gangetic Plain", "دشت گنگ",
         "The river plain of Hastinapur, Varanasi and the epic kingdoms.",
         "دشت رود گنگ، سرزمین هستیناپور، واراناسی و پادشاهی‌های حماسی.",
         "/cultures/indian/",
         [(75, 30), (81, 28.4), (87, 26.4), (91, 24.8), (89.5, 23.4), (84, 23.6), (78, 25.6), (74.5, 27.4)]),
        ("bengal", "Bengal", "بنگال",
         "The wide delta where the Ganges meets the sea.",
         "دلتای پهناور که گنگ به دریا می‌ریزد.",
         None,
         [(88.2, 23.2), (92, 22.8), (93, 20.6), (90.5, 18.4), (88, 20), (87, 21.6)]),
        ("deccan", "Deccan", "دکن",
         "The plateau that fills the southern peninsula.",
         "فلاتی که شبه‌قارهٔ جنوبی را پر می‌کند.",
         None,
         [(73.5, 21), (77, 19), (80, 17), (82, 14), (80, 11.5), (76, 13), (73, 16), (71.5, 19)]),
    ],
    "aegean": [
        ("greece", "Greece", "یونان",
         "Mountain and island: Olympus, Delphi, Athens.",
         "کوه و جزیره: المپ، دلفی و آتن.",
         "/cultures/greek/",
         [(19.5, 41.4), (21.5, 41.4), (23, 40.5), (24, 39), (23.5, 37.5), (22.5, 36.5), (21, 37.5), (20, 38.5), (19, 39.5)]),
        ("thrace", "Thrace", "تراکیه",
         "The land north of the Aegean and the Hellespont.",
         "سرزمین شمال اژه و هلسپونت.",
         None,
         [(24.5, 42.6), (27, 43), (28.6, 42), (28, 41), (26, 40.8), (24.6, 41.4)]),
        ("anatolia", "Anatolia", "آناتولی",
         "The coast across the Aegean, home of Troy and the Ionian cities.",
         "ساحل آن‌سوی اژه، سرزمین تروا و شهرهای یونیایی.",
         None,
         [(26.5, 40.6), (31, 41.5), (36, 41.5), (38.6, 40), (38.6, 37), (36, 36.4), (31, 36.4), (27.5, 37), (26, 38.6)]),
        ("crete", "Crete", "کرت",
         "The island of Knossos and the Minotaur's labyrinth.",
         "جزیرهٔ کنوسوس و هزارتوی مینوتاور.",
         None,
         [(23.4, 35.6), (25, 35.7), (26.4, 35.3), (26, 34.7), (24, 34.7), (23.3, 35.1)]),
        ("cyprus", "Cyprus", "قبرس",
         "The island south of Anatolia, sacred to Aphrodite.",
         "جزیرهٔ جنوب آناتولی، مقدس برای آفرودیت.",
         None,
         [(32.2, 35.2), (34, 35.4), (34.5, 34.7), (33, 34.3), (32.2, 34.7)]),
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


def line(row, box, w, lang):
    key, le, lf, ne, nf, href, ring = row
    label, note = (le, ne) if lang == "en" else (lf, nf)
    pts = " ".join("%.1f,%.1f" % pct_art(lo, la, box, w) for lo, la in ring)
    h = ' href="%s"' % href if href else ""
    return 'region points="%s" label="%s" note="%s"%s color="gold" /' % (pts, label, note, h)


def lines_for(name, lang):
    spec = genmaps.MAPS[name]
    return [line(row, spec["box"], spec["w"], lang) for row in R[name]]


if __name__ == "__main__":
    for out in lines_for(sys.argv[1], sys.argv[2]):
        print(out)
