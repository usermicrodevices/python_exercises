#!/usr/bin/env python
# Script to render text as a PNG image.

# texttopng

# Example (all ASCII glyphs):
"""
printf $(printf '\\%s' $(seq 40 176 | grep -v '[89]')) |
  fold -w 32 |
  python3 texttopng.py > ascii.png
"""

import binascii
import itertools

import png, sys


def usage(fil):
    fil.write("texttopng [-h|--help] text\n")


font = {
32: '0000000000000000',
33: '0010101010001000',
34: '0028280000000000',
35: '0000287c287c2800',
36: '00103c5038147810',
37: '0000644810244c00',
38: '0020502054483400',
39: '0010100000000000',
40: '0008101010101008',
41: '0020101010101020',
42: '0010543838541000',
43: '000010107c101000',
44: '0000000000301020',
45: '000000007c000000',
46: '0000000000303000',
47: '0000040810204000',
48: '0038445454443800',
49: '0008180808080800',
50: '0038043840407c00',
51: '003c041804043800',
52: '00081828487c0800',
53: '0078407804047800',
54: '0038407844443800',
55: '007c040810101000',
56: '0038443844443800',
57: '0038443c04040400',
58: '0000303000303000',
59: '0000303000301020',
60: '0004081020100804',
61: '0000007c007c0000',
62: '0040201008102040',
63: '0038440810001000',
64: '00384c545c403800',
65: '0038447c44444400',
66: '0078447844447800',
67: '0038444040443800',
68: '0070484444487000',
69: '007c407840407c00',
70: '007c407840404000',
71: '003844405c443c00',
72: '0044447c44444400',
73: '0038101010103800',
74: '003c040404443800',
75: '0044487048444400',
76: '0040404040407c00',
77: '006c545444444400',
78: '004464544c444400',
79: '0038444444443800',
80: '0078447840404000',
81: '0038444444443c02',
82: '0078447844444400',
83: '0038403804047800',
84: '007c101010101000',
85: '0044444444443c00',
86: '0044444444281000',
87: '0044445454543800',
88: '0042241818244200',
89: '0044443810101000',
90: '007c081020407c00',
91: '0038202020202038',
92: '0000402010080400',
93: '0038080808080838',
94: '0010284400000000',
95: '000000000000fe00',
96: '0040200000000000',
97: '000038043c443c00',
98: '0040784444447800',
99: '0000384040403800',
100: '00043c4444443c00',
101: '000038447c403c00',
102: '0018203820202000',
103: '00003c44443c0438',
104: '0040784444444400',
105: '0010003010101000',
106: '0010003010101020',
107: '0040404870484400',
108: '0030101010101000',
109: '0000385454444400',
110: '0000784444444400',
111: '0000384444443800',
112: '0000784444784040',
113: '00003c44443c0406',
114: '00001c2020202000',
115: '00003c4038047800',
116: '0020203820201800',
117: '0000444444443c00',
118: '0000444444281000',
119: '0000444454543800',
120: '0000442810284400',
121: '00004444443c0438',
122: '00007c0810207c00',
123: '0018202060202018',
124: '0010101000101010',
125: '003008080c080830',
126: '0020540800000000'
}
font_utf8_ru = {
1025: '287c407840407c00',
1040: font[65],
1041: '0078407844447800',
1042: font[66],
1043: '007c404040404000',
1044: '001c2424243c4200',
1045: font[69],
1046: '0054543854545400',
1047: '0038083808083800',
1048: '00444c5c74644400',
1049: '10444c5c74644400',
1050: font[75],
1051: '0008142222424200',
1052: '00245a4242424200',
1053: font[72],
1054: font[79],
1055: '007c444444444400',
1056: font[80],
1057: font[67],
1058: font[84],
1059: '0042423e02023c00',
1060: '007c54547c101000',
1061: font[88],
1062: '0044444444447c02',
1063: '002424241c040400',
1064: '0054545454547c00',
1065: '0054545454547c02',
1066: '0060203824243800',
1067: '004242724a4a7200',
1068: '0020203824243800',
1069: '003c420e02423c00',
1070: '005c547454545c00',
1071: '003c443c44444400',
1072: font[97],
1073: '0000784078447800',
1074: '0000784478447800',
1075: '0000784040404000',
1076: '00001c24243c4200',
1077: font[101],
1078: '0000545438545400',
1079: '0000380838083800',
1080: '0000242c3c342400',
1081: '0010242c3c342400',
1082: font[107],
1083: '0000081424242400',
1084: '0000142a22222200',
1085: '000044447c444400',
1086: font[111],
1087: '00007c4444444400',
1088: font[112],
1089: font[99],
1090: '00007c1010101000',
1091: font[121],
1092: '00007c547c101000',
1093: font[120],
1094: '0000242424243c02',
1095: '000024241c040400',
1096: '0000545454547c00',
1097: '0000545454547c02',
1098: '0000602038243800',
1099: '00004242724a7200',
1100: '0000202038243800',
1101: '000038041c043800',
1102: '00005c5474545c00',
1103: '00003c443c444400',
1104: '001038447c403c00',#ѐ
1105: '002838447c403c00'
}


def char(c):
    """Get image data for the character `i` (a one character string).
    Returned as a list of rows.
    Each row is a tuple containing the packed pixels.
    """

    i = ord(c)
    #sys.stderr.write(f'{c}, {i}\n')
    symbol = font[32]
    if i in font:
        symbol = font[i]
    elif i in font_utf8_ru:
        symbol = font_utf8_ru[i]
    else:
        return [(0,)] * 8
    return [(row,) for row in binascii.unhexlify(symbol)]


def texttoraster(m):
    """
    Convert the string *m* to a raster image.
    Any newlines in *m* will cause more than one line of output.
    The resulting raster will be taller.
    Prior to rendering each line,
    it is padded on the right with
    enough spaces to make all lines the same length.
    """

    lines = m.split('\n')
    maxlen = max(len(line) for line in lines)
    justified = [line.ljust(maxlen) for line in lines]
    rasters = [linetoraster(line) for line in justified]
    x, = set(r[0] for r in rasters)
    y = sum(r[1] for r in rasters)
    raster = itertools.chain(*(r[2] for r in rasters))
    return x, y, raster


def linetoraster(m):
    """
    Convert a single line of text *m* to a raster image,
    by rendering it using the font in *font*.

    A triple of (*width*, *height*, *pixels*) is returned;
    *pixels* is in boxed row packed pixel format.
    """

    # Assumes monospaced font.
    x = 8 * len(m)
    y = 8
    return x, y, [itertools.chain(*row) for row in zip(*map(char, m))]


def render(message, out):
    x, y, pixels = texttoraster(message)
    w = png.Writer(x, y, greyscale=True, bitdepth=1)
    w.write_packed(out, pixels)
    out.flush()


def main(argv=None):
    import sys, io

    if argv is None:
        argv = sys.argv
    for a in argv:
        if a.startswith('-'):
            if a in ('-h', '--help'):
                usage(sys.stdout)
                sys.exit(0)
            else:
                sys.stderr.write("Unknown option: %s\n" % a)
                usage(sys.stderr)
                sys.exit(4)
    arg = argv[1:]
    if len(arg) > 0:
        message = arg[0]
        #out = open("%s.png" % message, 'wb')
        #out = open('out.png', 'wb')
        #out = io.StringIO()
        out = io.BytesIO()
    else:
        message = sys.stdin.read()
        out = png.binary_stdout()

    render(message, out)
    with open('out.png', 'wb') as f:
        f.write(out.getbuffer())

if __name__ == '__main__':
    main()
