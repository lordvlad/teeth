#!/usr/bin/env python3
"""Generates the lion artwork.

  python3 design/lion.py          -> design/lion.svg (full lion, 768x1024, standalone)
  python3 design/lion.py --apply  -> also replaces the region between <!-- lion:begin --> and <!-- lion:end -->
                                     in public/index.html with the head-only fragment used as the timer's background

The fragment lives in a 768x1024 coordinate space and is scaled/centred by a wrapper <g> in index.html.
Teeth carry data-k = TR | BR | BL | TL | F (quadrant / front group) and class "tooth" for the timer highlights.
"""
import math, os, re, sys

OL = "#b8591a"  # outline orange-brown
HERE = os.path.dirname(os.path.abspath(__file__))


def mane(cx, cy, rx, ry, n, off=0, k=.5):
    pts = [(cx + rx * math.cos(math.radians(off + i * 360 / n)), cy + ry * math.sin(math.radians(off + i * 360 / n))) for i in range(n)]
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(1, n + 1):
        x, y = pts[i % n]; px, py = pts[i - 1]; ch = math.hypot(x - px, y - py)
        d += f" A{ch * k:.1f} {ch * k:.1f} 0 0 1 {x:.1f} {y:.1f}"
    return d + " Z"


MANE = mane(383, 447, 336, 326, 14, off=-90 + 360 / 28, k=.51)
MANE_INNER = mane(383, 449, 300, 292, 14, off=-90 + 360 / 28, k=.51)

# ---- teeth: (key, center x, center y, rotation, local shape) ; shapes are centred on (0,0)
INC_DOWN = "M-18 -22 H18 V8 C18 18 10 22 0 22 C-10 22 -18 18 -18 8 Z"        # flat top, round tip down (upper jaw)
INC_UP = "M-19 18 H19 V-6 C19 -16 10 -18 0 -18 C-10 -18 -19 -16 -19 -6 Z"    # round tip up (lower jaw)
FANG_UL = "M-27 -42 C-7 -49 13 -47 27 -41 C26 -8 14 22 -3 40 C-19 16 -27 -12 -27 -42 Z"
FANG_UR = "M-27 -41 C-13 -47 7 -49 27 -42 C27 -12 19 16 3 40 C-13 20 -26 -8 -27 -41 Z"
FANG_LL = "M-25 25 C-27 3 -15 -13 3 -27 C19 -11 29 7 25 27 C11 35 -11 35 -25 25 Z"
FANG_LR = "M-24 27 C-28 9 -18 -11 0 -27 C16 -13 28 5 24 25 C12 35 -10 35 -24 27 Z"
TEETH = [
    # (key, cx, cy, rot, kind, shape/size)
    ("TL", 285, 451, 0, "path", FANG_UL), ("TR", 485, 451, 0, "path", FANG_UR),
    ("TL", 244, 452, -20, "rect", (34, 30)), ("TR", 526, 452, 20, "rect", (34, 30)),
    ("F", 326, 425, 0, "path", INC_DOWN), ("F", 364, 424, 0, "path", INC_DOWN),
    ("F", 403, 424, 0, "path", INC_DOWN), ("F", 441, 425, 0, "path", INC_DOWN),
    ("BL", 287, 589, 0, "path", FANG_LL), ("BR", 482, 589, 0, "path", FANG_LR),
    ("BL", 253, 575, 22, "rect", (38, 34)), ("BR", 517, 575, -22, "rect", (38, 34)),
    ("F", 329, 616, 0, "path", INC_UP), ("F", 367, 621, 0, "path", INC_UP),
    ("F", 403, 621, 0, "path", INC_UP), ("F", 441, 616, 0, "path", INC_UP),
]


def teeth(interactive=True):
    out = ['<g id="teeth" fill="#fffdf6" stroke="#bfae92" stroke-width="2.5">'] if interactive else ['<g fill="#fffdf6" stroke="#bfae92" stroke-width="2.5">']
    for key, cx, cy, rot, kind, shape in TEETH:
        attrs = f'class="tooth" data-k="{key}"'
        t = f'translate({cx} {cy})' + (f' rotate({rot})' if rot else '')
        if kind == "rect":
            w, h = shape
            el = f'<rect {attrs} x="{-w / 2:g}" y="{-h / 2:g}" width="{w}" height="{h}" rx="{min(w, h) * .38:.1f}"/>'
        else:
            el = f'<path {attrs} d="{shape}"/>'
        out.append(f'  <g transform="{t}">{el}</g>')
    out.append("</g>")
    return "\n".join(out)


DEFS = '''<defs>
  <linearGradient id="maneG" x1="0" y1="0" x2="0.35" y2="1"><stop offset="0" stop-color="#fa8f27"/><stop offset="1" stop-color="#ef7a1c"/></linearGradient>
  <linearGradient id="faceG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fcc94b"/><stop offset=".6" stop-color="#f9bd3a"/><stop offset="1" stop-color="#f6ae30"/></linearGradient>
  <linearGradient id="bodyG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbc03e"/><stop offset="1" stop-color="#f5ae2e"/></linearGradient>
  <radialGradient id="mouthG" cx="50%" cy="48%" r="60%"><stop offset="0" stop-color="#8e2a38"/><stop offset=".55" stop-color="#b3434e"/><stop offset="1" stop-color="#c4545c"/></radialGradient>
  <linearGradient id="tongueG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fb8d8d"/><stop offset="1" stop-color="#f4707a"/></linearGradient>
  <clipPath id="mouthClip"><path d="M205 478 C200 420 262 396 385 396 C508 396 570 420 565 478 C562 572 484 642 385 642 C286 642 208 572 205 478 Z"/></clipPath>
</defs>'''

TAIL_BODY = f'''  <!-- tail -->
  <path d="M562 842 C632 846 674 826 674 790" fill="none" stroke="{OL}" stroke-width="30"/>
  <path d="M562 842 C632 846 674 826 674 790" fill="none" stroke="#f7b733" stroke-width="20"/>
  <g transform="translate(26 14)"><path d="M596 752 C584 716 618 700 636 712 C640 692 664 680 676 694 C670 716 700 726 694 762 C686 796 640 812 614 800 C598 790 596 768 596 752 Z" fill="#f58a24"/>
  <path d="M636 712 C630 736 638 752 662 762 M616 738 C620 756 636 770 656 774" fill="none" stroke="#c9631a" stroke-width="3.5"/></g>
  <!-- body -->
  <path d="M300 740 C250 770 214 820 210 872 C206 922 244 952 296 952 L494 952 C546 952 584 922 576 872 C568 820 528 770 476 740 Z" fill="url(#bodyG)"/>
  <ellipse cx="258" cy="868" rx="52" ry="78" fill="#f9b936"/>
  <ellipse cx="520" cy="868" rx="52" ry="78" fill="#f9b936"/>
  <path d="M340 780 C336 850 336 900 340 940 L456 940 C460 900 458 850 452 780 Z" fill="#f8b935"/>
  <path d="M368 800 C366 850 366 900 368 936 M428 800 C430 850 430 900 428 936" fill="none" stroke-width="4"/>
  <g transform="translate(0 14)">  <!-- paws -->
  <path d="M206 912 C200 884 240 872 272 884 C292 892 296 918 284 930 C262 944 220 940 206 912 Z" fill="#f9bb3d"/>
  <path d="M238 892 V918 M262 894 V922" fill="none" stroke-width="3.5"/>
  <path d="M492 884 C524 872 566 884 570 912 C558 940 516 944 494 930 C482 918 486 892 492 884 Z" fill="#f9bb3d"/>
  <path d="M520 894 V922 M544 892 V918" fill="none" stroke-width="3.5"/>
  <path d="M276 936 C270 902 330 898 362 912 C378 926 378 946 362 950 C326 958 284 952 276 936 Z" fill="#f9bb3d"/>
  <path d="M308 916 V944 M334 914 V946" fill="none" stroke-width="3.5"/>
  <path d="M416 912 C450 898 512 902 518 936 C510 952 468 958 430 950 C412 946 410 924 416 912 Z" fill="#f9bb3d"/>
  <path d="M446 914 V946 M472 914 V944" fill="none" stroke-width="3.5"/>
  </g>'''


def head(interactive):
    return f'''  <!-- mane -->
  <path d="{MANE}" fill="url(#maneG)" stroke-width="6"/>
  <path d="{MANE_INNER}" fill="none" stroke="#f9a04a" stroke-width="5" opacity=".55"/>
  <!-- ears -->
  <circle cx="198" cy="306" r="46" fill="#f9bd3a"/>
  <circle cx="206" cy="311" r="28" fill="#dc9a3d" stroke-width="4"/>
  <path d="M196 322 Q200 300 216 296" fill="none" stroke="#a95a1b" stroke-width="4"/>
  <circle cx="572" cy="306" r="46" fill="#f9bd3a"/>
  <circle cx="564" cy="311" r="28" fill="#dc9a3d" stroke-width="4"/>
  <path d="M574 322 Q570 300 554 296" fill="none" stroke="#a95a1b" stroke-width="4"/>
  <!-- face -->
  <ellipse cx="385" cy="475" rx="236" ry="224" fill="#f2a82e"/>
  <ellipse cx="385" cy="462" rx="224" ry="208" fill="url(#faceG)" stroke="none"/>
  <path d="M345 252 C334 236 348 224 362 232 C360 218 376 206 388 213 C396 206 408 216 408 230 C411 238 406 248 400 256 Z" fill="#fbc44c"/>
  <path d="M362 232 C366 238 372 240 378 236" fill="none" stroke-width="3.5"/>
  <path d="M284 299 Q300 289 318 297 M456 297 Q474 289 490 299" fill="none" stroke="#ec8a2c" stroke-width="9"/>
  <path d="M250 342 Q284 300 322 334 M448 334 Q486 300 520 342" fill="none" stroke="#7a3a14" stroke-width="9"/>
  <ellipse cx="243" cy="371" rx="22" ry="13" fill="#f3a35d" stroke="none"/>
  <ellipse cx="524" cy="371" rx="22" ry="13" fill="#f3a35d" stroke="none"/>
  <path d="M358 345 Q384 333 410 345 Q410 366 384 372 Q358 366 358 345 Z" fill="#a85f2b" stroke="#7a3a14" stroke-width="4"/>
  <ellipse cx="383" cy="345" rx="12" ry="5" fill="#c98a4c" stroke="none"/>
  <path d="M384 372 V384 M384 384 C372 398 338 396 318 378 M384 384 C396 398 432 396 452 378" fill="none" stroke="#a85f2b" stroke-width="4"/>
  <g fill="#a85f2b" stroke="none"><circle cx="318" cy="366" r="2.5"/><circle cx="332" cy="372" r="2.5"/><circle cx="346" cy="368" r="2.5"/><circle cx="420" cy="368" r="2.5"/><circle cx="436" cy="372" r="2.5"/><circle cx="450" cy="366" r="2.5"/></g>
  <!-- mouth -->
  <path d="M205 478 C200 420 262 396 385 396 C508 396 570 420 565 478 C562 572 484 642 385 642 C286 642 208 572 205 478 Z" fill="url(#mouthG)" stroke="#8f3a24" stroke-width="7"/>
  <g clip-path="url(#mouthClip)" stroke="none">
    <ellipse cx="385" cy="492" rx="88" ry="76" fill="#822433"/>
    <ellipse cx="385" cy="488" rx="62" ry="56" fill="#611728"/>
    <path d="M350 440 C346 480 356 516 385 520 C414 516 424 480 420 440 Z" fill="#a8404f"/>
    <path d="M366 452 C364 480 372 502 385 506 C398 502 406 480 404 452" fill="none" stroke="#8b2c3c" stroke-width="3.5"/>
    <path d="M286 580 C300 548 345 534 385 534 C428 534 472 548 488 580 C470 618 432 636 385 636 C340 636 302 618 286 580 Z" fill="url(#tongueG)"/>
    <path d="M300 566 C330 548 360 544 385 546 C410 544 440 548 470 566" fill="none" stroke="#fdb1b0" stroke-width="4" opacity=".8"/>
    <path d="M385 560 C380 584 384 606 392 626" fill="none" stroke="#ee6370" stroke-width="5"/>
    <path d="M205 400 H565 V420 C520 410 450 408 385 408 C320 408 250 410 205 420 Z" fill="#ee8e8e"/>
    <path d="M205 640 H565 V618 C520 626 450 630 385 630 C320 630 250 626 205 618 Z" fill="#ee8e8e"/>
  </g>
{teeth(interactive)}
  <path d="M356 664 Q385 676 414 664" fill="none" stroke="#c0701c" stroke-width="4"/>'''


def full():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 768 1024" width="768" height="1024">
{DEFS}
<g stroke="{OL}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
{TAIL_BODY}
{head(False)}
</g>
</svg>
'''


def fragment():
    return f'''<g stroke="{OL}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
{DEFS}
{head(True)}
</g>'''


if __name__ == "__main__":
    open(os.path.join(HERE, "lion.svg"), "w").write(full())
    print("wrote design/lion.svg")
    if "--apply" in sys.argv:
        p = os.path.join(HERE, "..", "public", "index.html")
        s = open(p).read()
        a, b = "<!-- lion:begin -->", "<!-- lion:end -->"
        i, j = s.index(a) + len(a), s.index(b)
        s = s[:i] + "\n" + fragment() + "\n    " + s[j:]
        open(p, "w").write(s)
        print("updated public/index.html")
