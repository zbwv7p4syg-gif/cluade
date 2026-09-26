# Subsets ZCOOL KuaiLe (SIL OFL) to the characters the film uses: python3 subset.py path/to/ZCOOLKuaiLe-Regular.ttf
import re, sys, glob
from fontTools import subset
text = ''.join(open(f, encoding='utf-8').read() for f in glob.glob('src/*.js'))
chars = sorted(set(c for c in text if ord(c) > 0x2000)) + [chr(c) for c in range(0x20, 0x7f)]
opts = subset.Options(); opts.flavor = 'woff2'
font = subset.load_font(sys.argv[1], opts); s = subset.Subsetter(opts); s.populate(text=''.join(chars)); s.subset(font)
subset.save_font(font, 'assets/zcool-kuaile-subset.woff2', opts)
print(len(chars), 'glyphs:', ''.join(c for c in chars if ord(c) > 0x2000))
