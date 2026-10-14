"""Build assets/nine-pixel.woff2: the 12px pixel font used for every piece of text in the MV.

    python3 make_font.py <fusion-pixel.ttf> [extra.lrc ...]

The source is Fusion Pixel (TakWolf, SIL OFL 1.1; the 2022-04-05 release, 12px monospaced). The subset keeps
ASCII, common punctuation, the 3755 GB2312 level-1 hanzi and any extra characters found in the files given
after the font, so most .lrc files render without missing glyphs. 'Fusion Pixel' is a Reserved Font Name, so
the subset is renamed to 'Nine Pixel' as the OFL requires. Needs: pip install fonttools brotli
"""
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

NAME = 'Nine Pixel'
level1 = ''.join(bytes([hi, lo]).decode('gb2312') for hi in range(0xB0, 0xD8) for lo in range(0xA1, 0xFF)
                 if not (hi == 0xD7 and lo > 0xF9))
text = ''.join(chr(c) for c in range(0x20, 0x7F)) + '，。、！？：；“”‘’（）《》·…—～「」『』♪×÷' + level1
for extra in sys.argv[2:]:
    with open(extra, encoding='utf-8') as fh:
        text += fh.read()

opts = subset.Options()
opts.flavor = 'woff2'
opts.name_IDs = []
opts.notdef_outline = True
font = TTFont(sys.argv[1])
sub = subset.Subsetter(opts)
sub.populate(text=text)
sub.subset(font)
names = font['name']
for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
    names.setName(NAME, 1, pid, eid, lid)
    names.setName('Regular', 2, pid, eid, lid)
    names.setName(NAME + ' Regular', 4, pid, eid, lid)
    names.setName('NinePixel-Regular', 6, pid, eid, lid)
    names.setName('Modified (subset, renamed) from Fusion Pixel by TakWolf, SIL Open Font License 1.1', 10, pid, eid, lid)
font.flavor = 'woff2'
font.save('assets/nine-pixel.woff2')
print(f"assets/nine-pixel.woff2: {len(font.getBestCmap())} characters")
