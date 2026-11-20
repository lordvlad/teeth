#!/usr/bin/env python3
"""Generates the animal artwork: the original lion plus tiger cub, kitten, bulldog pup, wolf pup and bear cub.

  python3 design/animals.py          -> design/<id>.svg (full animal, 768x1024, standalone) for every animal
  python3 design/animals.py --apply  -> also rewrites two generated regions in public/index.html:
        <!-- animals:begin --> ... <!-- animals:end -->   the shared mouth + teeth (same for every animal)
        /* animals:begin */ ... /* animals:end */          ANIMALS = { id: { back, front } }: the per-animal head art that
                                                            goes behind / in front of the mouth

All animals share the lion's layout (drawn in 768x1024 space): the lion's mane fills the timer disc, the other animals are heads only; the mouth and its 16 teeth
are identical, so the highlight logic doesn't care which animal is shown. Teeth carry data-k = TR | BR | BL | TL | F.
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CX, CY = 383, 447  # centre of the mane / ruff


# ------------------------------------------------------------------ shared mouth + teeth
def scallop(cx, cy, rx, ry, n, off=0.0, k=.5):
    pts = [(cx + rx * math.cos(math.radians(off + i * 360 / n)), cy + ry * math.sin(math.radians(off + i * 360 / n))) for i in range(n)]
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(1, n + 1):
        x, y = pts[i % n]; px, py = pts[i - 1]; ch = math.hypot(x - px, y - py)
        d += f" A{ch * k:.1f} {ch * k:.1f} 0 0 1 {x:.1f} {y:.1f}"
    return d + " Z"


def spiky(cx, cy, rx, ry, n, valley=.84, off=-90.0):
    pts = []
    for i in range(n * 2):
        a = math.radians(off + i * 180 / n)
        f = 1 if i % 2 == 0 else valley
        pts.append(f"{cx + rx * f * math.cos(a):.1f} {cy + ry * f * math.sin(a):.1f}")
    return "M" + " L".join(pts) + " Z"


INC_DOWN = "M-18 -22 H18 V8 C18 18 10 22 0 22 C-10 22 -18 18 -18 8 Z"
INC_UP = "M-19 18 H19 V-6 C19 -16 10 -18 0 -18 C-10 -18 -19 -16 -19 -6 Z"
FANG_UL = "M-27 -42 C-7 -49 13 -47 27 -41 C26 -8 14 22 -3 40 C-19 16 -27 -12 -27 -42 Z"
FANG_UR = "M-27 -41 C-13 -47 7 -49 27 -42 C27 -12 19 16 3 40 C-13 20 -26 -8 -27 -41 Z"
FANG_LL = "M-25 25 C-27 3 -15 -13 3 -27 C19 -11 29 7 25 27 C11 35 -11 35 -25 25 Z"
FANG_LR = "M-24 27 C-28 9 -18 -11 0 -27 C16 -13 28 5 24 25 C12 35 -10 35 -24 27 Z"
TEETH = [
    ("TL", 285, 451, 0, "path", FANG_UL), ("TR", 485, 451, 0, "path", FANG_UR),
    ("TL", 244, 452, -20, "rect", (34, 30)), ("TR", 526, 452, 20, "rect", (34, 30)),
    ("F", 326, 425, 0, "path", INC_DOWN), ("F", 364, 424, 0, "path", INC_DOWN),
    ("F", 403, 424, 0, "path", INC_DOWN), ("F", 441, 425, 0, "path", INC_DOWN),
    ("BL", 287, 589, 0, "path", FANG_LL), ("BR", 482, 589, 0, "path", FANG_LR),
    ("BL", 253, 575, 22, "rect", (38, 34)), ("BR", 517, 575, -22, "rect", (38, 34)),
    ("F", 329, 616, 0, "path", INC_UP), ("F", 367, 621, 0, "path", INC_UP),
    ("F", 403, 621, 0, "path", INC_UP), ("F", 441, 616, 0, "path", INC_UP),
]


def teeth():
    out = ['<g id="teeth" fill="#fffdf6" stroke="#bfae92" stroke-width="2.5">']
    for key, cx, cy, rot, kind, shape in TEETH:
        attrs = f'class="tooth" data-k="{key}"'
        t = f"translate({cx} {cy})" + (f" rotate({rot})" if rot else "")
        if kind == "rect":
            w, h = shape
            el = f'<rect {attrs} x="{-w / 2:g}" y="{-h / 2:g}" width="{w}" height="{h}" rx="{min(w, h) * .38:.1f}"/>'
        else:
            el = f'<path {attrs} d="{shape}"/>'
        out.append(f'  <g transform="{t}">{el}</g>')
    out.append("</g>")
    return "\n".join(out)


MOUTH_DEFS = '''<defs>
  <radialGradient id="mouthG" cx="50%" cy="48%" r="60%"><stop offset="0" stop-color="#8e2a38"/><stop offset=".55" stop-color="#b3434e"/><stop offset="1" stop-color="#c4545c"/></radialGradient>
  <linearGradient id="tongueG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fb8d8d"/><stop offset="1" stop-color="#f4707a"/></linearGradient>
  <clipPath id="mouthClip"><path d="M205 478 C200 420 262 396 385 396 C508 396 570 420 565 478 C562 572 484 642 385 642 C286 642 208 572 205 478 Z"/></clipPath>
</defs>'''

MOUTH = f'''<g stroke-linejoin="round" stroke-linecap="round">
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
{teeth()}
</g>'''


# ------------------------------------------------------------------ per-animal art
def mirror(svg):
    """Right-hand copy of left-hand art: mirror around the head's centre line x=385."""
    return f'<g transform="translate(770 0) scale(-1 1)">{svg}</g>'


def grad(id_, a, b, c=None, v="x1=\"0\" y1=\"0\" x2=\"0.35\" y2=\"1\""):
    stops = f'<stop offset="0" stop-color="{a}"/>' + (f'<stop offset=".6" stop-color="{b}"/><stop offset="1" stop-color="{c}"/>' if c else f'<stop offset="1" stop-color="{b}"/>')
    return f'<linearGradient id="{id_}" {v}>{stops}</linearGradient>'


# ears, left-hand side (mirrored for the right)
EARS = {
    "round": lambda c: (f'<circle cx="198" cy="306" r="46" fill="{c["earO"]}"/><circle cx="206" cy="311" r="28" fill="{c["earI"]}" stroke-width="4"/>'
                        f'<path d="M196 322 Q200 300 216 296" fill="none" stroke="{c["earLine"]}" stroke-width="4"/>'),
    "bear": lambda c: (f'<circle cx="206" cy="298" r="46" fill="{c["earO"]}"/><circle cx="212" cy="304" r="26" fill="{c["earI"]}" stroke-width="4"/>'),
    "cat": lambda c: (f'<path d="M166 340 C158 292 174 246 200 216 C240 234 272 266 286 304 Z" fill="{c["earO"]}"/>'
                      f'<path d="M190 326 C186 294 196 268 208 246 C232 260 252 280 260 306 Z" fill="{c["earI"]}" stroke-width="4"/>'),
    "wolf": lambda c: (f'<path d="M170 344 C158 282 166 224 194 174 C236 204 272 250 286 306 Z" fill="{c["earO"]}"/>'
                       f'<path d="M192 326 C186 278 192 238 204 208 C230 230 252 262 260 300 Z" fill="{c["earI"]}" stroke-width="4"/>'),
    "floppy": lambda c: (f'<path d="M176 342 C142 298 172 252 226 258 C264 262 284 290 288 314 C252 308 228 324 224 352 C206 358 186 354 176 342 Z" fill="{c["earO"]}"/>'
                         f'<path d="M206 286 C230 284 252 292 262 306" fill="none" stroke="{c["earI"]}" stroke-width="7"/>'),
}

NOSES = {
    "tri": lambda c: (f'<path d="M358 345 Q384 333 410 345 Q410 366 384 372 Q358 366 358 345 Z" fill="{c["nose"]}" stroke="{c["noseLine"]}" stroke-width="4"/>'
                      f'<ellipse cx="383" cy="345" rx="12" ry="5" fill="{c["noseHi"]}" stroke="none"/>'),
    "kitten": lambda c: (f'<path d="M366 346 Q384 338 402 346 Q398 364 384 368 Q370 364 366 346 Z" fill="{c["nose"]}" stroke="{c["noseLine"]}" stroke-width="4"/>'),
    "wide": lambda c: (f'<path d="M346 344 Q384 328 422 344 Q426 372 384 378 Q342 372 346 344 Z" fill="{c["nose"]}" stroke="{c["noseLine"]}" stroke-width="4"/>'
                       f'<ellipse cx="384" cy="342" rx="22" ry="6" fill="{c["noseHi"]}" stroke="none"/>'),
    "oval": lambda c: (f'<ellipse cx="384" cy="352" rx="26" ry="18" fill="{c["nose"]}" stroke="{c["noseLine"]}" stroke-width="4"/>'
                       f'<ellipse cx="384" cy="346" rx="12" ry="5" fill="{c["noseHi"]}" stroke="none"/>'),
}

# palettes
ANIMALS = {}


def P(**k):
    return k


PAL = {
    "tiger": P(ol="#8a3a10", ruff=("#f7922b", "#e8741a"), ruffLine="#f9ad5c", earO="#f59a35", earI="#fff1dc", earLine="#8a3a10",
               rim="#ee8a26", face=("#fbb04a", "#f8a23c", "#f39630"), patch="#fff4e0", brow="#5a2810", eye="#4a2410", cheek="#f08a5a",
               nose="#e88a7a", noseLine="#8a3a10", noseHi="#f6b4a6", line="#8a3a10", dot="#8a3a10", chin="#a8501a",
               body=("#f9ac45", "#f39a33"), haunch="#f7a63c", paw="#fbb54f"),
    "kitten": P(ol="#a8683a", ruff=("#f9d19a", "#f1b974"), ruffLine="#fbdcb0", earO="#f5c389", earI="#ffc4cf", earLine="#a8683a",
                rim="#efb672", face=("#fde5c0", "#fbd8a6", "#f8cf98"), patch="#fff6ea", brow="#d9a064", eye="#6a3c1c", cheek="#f6a8a0",
                nose="#f58aa0", noseLine="#b0506a", noseHi="#fbb8c6", line="#b0803e", dot="#b0803e", chin="#b57a3a",
                body=("#fbd9a6", "#f4c283"), haunch="#f9cf96", paw="#fff0d8"),
    "bulldog": P(ol="#6e4222", ruff=("#ecc189", "#e0aa6c"), ruffLine="#f4d2a6", earO="#7a4a2a", earI="#b27a4c", earLine="#6e4222",
                 rim="#e0aa6c", face=("#f6d3a2", "#f0c791", "#eabb82"), patch="#fffaf2", brow="#a8703a", eye="#4a2a14", cheek="#e79a84",
                 nose="#2b2320", noseLine="#1a1410", noseHi="#6a5a52", line="#7a4a26", dot="#7a4a26", chin="#8a5a30",
                 body=("#f0c690", "#e5b074"), haunch="#ecbd84", paw="#fff1e0"),
    "wolf": P(ol="#4d5868", ruff=("#8d98a7", "#79879a"), ruffLine="#a9b3c0", earO="#7f8b9b", earI="#4d5868", earLine="#3a4452",
              rim="#8591a1", face=("#bfc7d1", "#b0bac6", "#a4afbc"), patch="#f1f4f7", brow="#6a7686", eye="#2f3846", cheek="#e7a4a8",
              nose="#2b3340", noseLine="#161b24", noseHi="#6a7686", line="#4d5868", dot="#4d5868", chin="#3a4452",
              body=("#b5bec9", "#a4afbc"), haunch="#adb7c3", paw="#e9edf2"),
    "bear": P(ol="#6b3a1a", ruff=("#b87440", "#a5622e"), ruffLine="#cf8e5a", earO="#b87440", earI="#e9b98a", earLine="#6b3a1a",
              rim="#a5622e", face=("#d89c64", "#cf9057", "#c78649"), patch="#f0d0a8", brow="#8a5028", eye="#3a2214", cheek="#e8957a",
              nose="#3a2214", noseLine="#1f1209", noseHi="#7a5a46", line="#6b3a1a", dot="#6b3a1a", chin="#7a4420",
              body=("#ca8c56", "#b97b45"), haunch="#c3834c", paw="#d9a272"),
}


def head_generic(id_, c, ears, nose, forehead="", jowl="", whiskers=False, dots=False, patch=(385, 490, 190, 170)):
    faceG = f"faceG_{id_}"
    px, py, prx, pry = patch
    patch_svg = f'<ellipse cx="{px}" cy="{py}" rx="{prx}" ry="{pry}" fill="{c["patch"]}" stroke="none" opacity=".95"/>' if c.get("patch") else ""
    dots_svg = (f'<g fill="{c["dot"]}" stroke="none"><circle cx="318" cy="366" r="2.5"/><circle cx="332" cy="372" r="2.5"/><circle cx="346" cy="368" r="2.5"/>'
                '<circle cx="420" cy="368" r="2.5"/><circle cx="436" cy="372" r="2.5"/><circle cx="450" cy="366" r="2.5"/></g>') if dots else ""
    back = f'''<g stroke="{c["ol"]}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <defs>{grad(faceG, *c["face"], v='x1="0" y1="0" x2="0" y2="1"')}</defs>
  {ears}{mirror(ears)}
  {jowl}
  <ellipse cx="385" cy="475" rx="236" ry="224" fill="{c["rim"]}"/>
  <ellipse cx="385" cy="462" rx="224" ry="208" fill="url(#{faceG})" stroke="none"/>
  {patch_svg}
  {forehead}
  <path d="M284 299 Q300 289 318 297 M456 297 Q474 289 490 299" fill="none" stroke="{c["brow"]}" stroke-width="9"/>
  <path d="M250 342 Q284 300 322 334 M448 334 Q486 300 520 342" fill="none" stroke="{c["eye"]}" stroke-width="9"/>
  <ellipse cx="243" cy="371" rx="22" ry="13" fill="{c["cheek"]}" stroke="none" opacity=".85"/>
  <ellipse cx="524" cy="371" rx="22" ry="13" fill="{c["cheek"]}" stroke="none" opacity=".85"/>
  {nose}
  <path d="M384 372 V384 M384 384 C372 398 338 396 318 378 M384 384 C396 398 432 396 452 378" fill="none" stroke="{c["line"]}" stroke-width="4"/>
  {dots_svg}
</g>'''
    wh = ""
    if whiskers:
        left = '<path d="M336 372 C300 362 270 360 238 366 M338 382 C302 384 272 392 246 404 M344 362 C312 346 284 340 256 340" fill="none"/>'
        wh = f'<g stroke="{c["line"]}" stroke-width="3.5" stroke-linecap="round" opacity=".8">{left}{mirror(left)}</g>'
    front = f'''<g stroke-linejoin="round" stroke-linecap="round">
  <path d="M356 664 Q385 676 414 664" fill="none" stroke="{c["chin"]}" stroke-width="4"/>
  {wh}
</g>'''
    return back, front


def body_generic(id_, c, tail, markings=""):
    bodyG = f"bodyG_{id_}"
    return f'''<g stroke="{c["ol"]}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <defs>{grad(bodyG, *c["body"], v='x1="0" y1="0" x2="0" y2="1"')}</defs>
{tail}
  <path d="M300 740 C250 770 214 820 210 872 C206 922 244 952 296 952 L494 952 C546 952 584 922 576 872 C568 820 528 770 476 740 Z" fill="url(#{bodyG})"/>
  <ellipse cx="258" cy="868" rx="52" ry="78" fill="{c["haunch"]}"/>
  <ellipse cx="520" cy="868" rx="52" ry="78" fill="{c["haunch"]}"/>
  {markings}
  <path d="M340 780 C336 850 336 900 340 940 L456 940 C460 900 458 850 452 780 Z" fill="{c["haunch"]}"/>
  <path d="M368 800 C366 850 366 900 368 936 M428 800 C430 850 430 900 428 936" fill="none" stroke-width="4"/>
  <g transform="translate(0 14)">
  <path d="M206 912 C200 884 240 872 272 884 C292 892 296 918 284 930 C262 944 220 940 206 912 Z" fill="{c["paw"]}"/>
  <path d="M238 892 V918 M262 894 V922" fill="none" stroke-width="3.5"/>
  <path d="M492 884 C524 872 566 884 570 912 C558 940 516 944 494 930 C482 918 486 892 492 884 Z" fill="{c["paw"]}"/>
  <path d="M520 894 V922 M544 892 V918" fill="none" stroke-width="3.5"/>
  <path d="M276 936 C270 902 330 898 362 912 C378 926 378 946 362 950 C326 958 284 952 276 936 Z" fill="{c["paw"]}"/>
  <path d="M308 916 V944 M334 914 V946" fill="none" stroke-width="3.5"/>
  <path d="M416 912 C450 898 512 902 518 936 C510 952 468 958 430 950 C412 946 410 924 416 912 Z" fill="{c["paw"]}"/>
  <path d="M446 914 V946 M472 914 V944" fill="none" stroke-width="3.5"/>
  </g>
</g>'''


# ---- lion (the approved original, kept as it was)
def lion():
    ol = "#b8591a"
    mane = scallop(CX, 447, 336, 326, 14, off=-90 + 360 / 28, k=.51)
    mane_inner = scallop(CX, 449, 300, 292, 14, off=-90 + 360 / 28, k=.51)
    back = f'''<g stroke="{ol}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <defs>
    <linearGradient id="maneG" x1="0" y1="0" x2="0.35" y2="1"><stop offset="0" stop-color="#fa8f27"/><stop offset="1" stop-color="#ef7a1c"/></linearGradient>
    <linearGradient id="faceG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fcc94b"/><stop offset=".6" stop-color="#f9bd3a"/><stop offset="1" stop-color="#f6ae30"/></linearGradient>
  </defs>
  <path d="{mane}" fill="url(#maneG)" stroke-width="6"/>
  <path d="{mane_inner}" fill="none" stroke="#f9a04a" stroke-width="5" opacity=".55"/>
  <circle cx="198" cy="306" r="46" fill="#f9bd3a"/>
  <circle cx="206" cy="311" r="28" fill="#dc9a3d" stroke-width="4"/>
  <path d="M196 322 Q200 300 216 296" fill="none" stroke="#a95a1b" stroke-width="4"/>
  <circle cx="572" cy="306" r="46" fill="#f9bd3a"/>
  <circle cx="564" cy="311" r="28" fill="#dc9a3d" stroke-width="4"/>
  <path d="M574 322 Q570 300 554 296" fill="none" stroke="#a95a1b" stroke-width="4"/>
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
</g>'''
    front = '''<g stroke-linejoin="round" stroke-linecap="round"><path d="M356 664 Q385 676 414 664" fill="none" stroke="#c0701c" stroke-width="4"/></g>'''
    body = f'''<g stroke="{ol}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <defs><linearGradient id="bodyG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbc03e"/><stop offset="1" stop-color="#f5ae2e"/></linearGradient></defs>
  <path d="M562 842 C632 846 674 826 674 790" fill="none" stroke="{ol}" stroke-width="30"/>
  <path d="M562 842 C632 846 674 826 674 790" fill="none" stroke="#f7b733" stroke-width="20"/>
  <g transform="translate(26 14)"><path d="M596 752 C584 716 618 700 636 712 C640 692 664 680 676 694 C670 716 700 726 694 762 C686 796 640 812 614 800 C598 790 596 768 596 752 Z" fill="#f58a24"/>
  <path d="M636 712 C630 736 638 752 662 762 M616 738 C620 756 636 770 656 774" fill="none" stroke="#c9631a" stroke-width="3.5"/></g>
  <path d="M300 740 C250 770 214 820 210 872 C206 922 244 952 296 952 L494 952 C546 952 584 922 576 872 C568 820 528 770 476 740 Z" fill="url(#bodyG)"/>
  <ellipse cx="258" cy="868" rx="52" ry="78" fill="#f9b936"/>
  <ellipse cx="520" cy="868" rx="52" ry="78" fill="#f9b936"/>
  <path d="M340 780 C336 850 336 900 340 940 L456 940 C460 900 458 850 452 780 Z" fill="#f8b935"/>
  <path d="M368 800 C366 850 366 900 368 936 M428 800 C430 850 430 900 428 936" fill="none" stroke-width="4"/>
  <g transform="translate(0 14)">
  <path d="M206 912 C200 884 240 872 272 884 C292 892 296 918 284 930 C262 944 220 940 206 912 Z" fill="#f9bb3d"/>
  <path d="M238 892 V918 M262 894 V922" fill="none" stroke-width="3.5"/>
  <path d="M492 884 C524 872 566 884 570 912 C558 940 516 944 494 930 C482 918 486 892 492 884 Z" fill="#f9bb3d"/>
  <path d="M520 894 V922 M544 892 V918" fill="none" stroke-width="3.5"/>
  <path d="M276 936 C270 902 330 898 362 912 C378 926 378 946 362 950 C326 958 284 952 276 936 Z" fill="#f9bb3d"/>
  <path d="M308 916 V944 M334 914 V946" fill="none" stroke-width="3.5"/>
  <path d="M416 912 C450 898 512 902 518 936 C510 952 468 958 430 950 C412 946 410 924 416 912 Z" fill="#f9bb3d"/>
  <path d="M446 914 V946 M472 914 V944" fill="none" stroke-width="3.5"/>
  </g>
</g>'''
    return body, back, front


def tiger():
    c = PAL["tiger"]
    left_cheek = '<path d="M168 432 Q196 444 218 434 M170 486 Q198 494 216 484 M182 540 Q204 544 222 534" fill="none"/>'
    forehead = (f'<g stroke="{c["brow"]}" stroke-width="10" fill="none">'
                '<path d="M385 246 V300 M350 256 Q352 282 364 300 M420 256 Q418 282 406 300 M314 274 Q320 292 332 304 M456 274 Q450 292 438 304"/>'
                f'{left_cheek}{mirror(left_cheek)}</g>')
    back, front = head_generic("tiger", c, EARS["round"](c), NOSES["tri"](c), forehead=forehead, dots=True, patch=(385, 500, 196, 160))
    tail = (f'<path d="M562 842 C636 850 684 822 676 760" fill="none" stroke="{c["ol"]}" stroke-width="30"/>'
            f'<path d="M562 842 C636 850 684 822 676 760" fill="none" stroke="#f7a63c" stroke-width="20"/>'
            f'<path d="M562 842 C636 850 684 822 676 760" fill="none" stroke="#5a2810" stroke-width="20" stroke-dasharray="9 24" stroke-dashoffset="-6" stroke-linecap="butt"/>'
            f'<circle cx="676" cy="760" r="14" fill="#5a2810" stroke="none"/>')
    marks = (f'<path d="M232 800 Q262 804 286 790 M222 850 Q256 856 284 842 M536 790 Q562 804 596 800 M538 842 Q566 856 604 850" fill="none" stroke="#5a2810" stroke-width="9" opacity=".75"/>')
    return body_generic("tiger", c, tail, marks), back, front


def kitten():
    c = PAL["kitten"]
    cheeks = '<path d="M190 418 Q214 424 230 416 M186 462 Q212 468 228 460" fill="none"/>'
    forehead = (f'<g stroke="{c["brow"]}" stroke-width="9" fill="none"><path d="M385 252 V298 M350 262 Q354 282 364 298 M420 262 Q416 282 406 298"/>{cheeks}{mirror(cheeks)}</g>')
    back, front = head_generic("kitten", c, EARS["cat"](c), NOSES["kitten"](c), forehead=forehead, whiskers=True, patch=(385, 500, 168, 140))
    tail = (f'<path d="M562 846 C650 856 706 812 684 738" fill="none" stroke="{c["ol"]}" stroke-width="30"/>'
            f'<path d="M562 846 C650 856 706 812 684 738" fill="none" stroke="{c["body"][0]}" stroke-width="20"/>'
            f'<path d="M562 846 C650 856 706 812 684 738" fill="none" stroke="#e4a468" stroke-width="20" stroke-dasharray="9 26" stroke-dashoffset="-8" stroke-linecap="butt"/>')
    marks = '<path d="M236 804 Q262 806 284 796 M538 796 Q562 806 590 804" fill="none" stroke="#e4a468" stroke-width="8" opacity=".8"/>'
    return body_generic("kitten", c, tail, marks), back, front


def bulldog():
    c = PAL["bulldog"]
    wrinkles = f'<path d="M322 266 Q385 244 448 266 M334 290 Q385 272 436 290" fill="none" stroke="{c["brow"]}" stroke-width="7"/>'
    jowl = ('<ellipse cx="226" cy="540" rx="52" ry="74" fill="#ecbd84"/><ellipse cx="544" cy="540" rx="52" ry="74" fill="#ecbd84"/>')
    back, front = head_generic("bulldog", c, EARS["floppy"](c), NOSES["wide"](c), forehead=wrinkles, jowl=jowl, dots=True, patch=(385, 490, 200, 175))
    tail = f'<ellipse cx="572" cy="842" rx="26" ry="20" fill="{c["body"][1]}" stroke="{c["ol"]}" stroke-width="5"/>'
    marks = f'<path d="M286 780 C300 760 330 752 350 760" fill="none" stroke="{c["brow"]}" stroke-width="7" opacity=".6"/>'
    return body_generic("bulldog", c, tail, marks), back, front


def wolf():
    c = PAL["wolf"]
    tuft = f'<path d="M346 266 L366 222 L378 254 L394 214 L410 256 L428 224 L432 268 Z" fill="{c["face"][1]}" stroke="{c["ol"]}" stroke-width="4"/>'
    sidefur = f'<path d="M168 456 L196 468 L170 486 L200 500 L176 520" fill="none" stroke="{c["ruffLine"]}" stroke-width="6"/>'
    back, front = head_generic("wolf", c, EARS["wolf"](c), NOSES["wide"](c), forehead=tuft + sidefur + mirror(sidefur), dots=True, patch=(385, 505, 200, 150))
    tail = (f'<path d="M562 856 C650 892 736 840 706 736 C676 780 628 804 562 810 Z" fill="{c["body"][1]}" stroke="{c["ol"]}" stroke-width="5"/>'
            f'<path d="M706 736 C688 772 662 792 636 800 C670 810 700 780 706 736 Z" fill="#eef1f5" stroke="{c["ol"]}" stroke-width="4"/>')
    marks = f'<path d="M232 800 Q262 806 286 794 M538 794 Q562 806 594 800" fill="none" stroke="{c["ruffLine"]}" stroke-width="8" opacity=".8"/>'
    return body_generic("wolf", c, tail, marks), back, front


def bear():
    c = PAL["bear"]
    back, front = head_generic("bear", c, EARS["bear"](c), NOSES["oval"](c), dots=False, patch=(385, 508, 192, 152))
    tail = f'<circle cx="570" cy="842" r="26" fill="{c["body"][1]}" stroke="{c["ol"]}" stroke-width="5"/>'
    marks = f'<ellipse cx="396" cy="840" rx="48" ry="56" fill="{c["patch"]}" stroke="none" opacity=".75"/>'
    return body_generic("bear", c, tail, marks), back, front


ORDER = ["lion", "tiger", "kitten", "bulldog", "wolf", "bear"]
BUILDERS = {"lion": lion, "tiger": tiger, "kitten": kitten, "bulldog": bulldog, "wolf": wolf, "bear": bear}


def full_svg(body, back, front):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 768 1024" width="768" height="1024">
{MOUTH_DEFS}
{body}
{back}
{MOUTH}
{front}
</svg>
'''


def build():
    out = {}
    for id_ in ORDER:
        body, back, front = BUILDERS[id_]()
        out[id_] = (body, back, front)
    return out


if __name__ == "__main__":
    art = build()
    for id_, (body, back, front) in art.items():
        open(os.path.join(HERE, f"{id_}.svg"), "w").write(full_svg(body, back, front))
    print("wrote", ", ".join(f"design/{i}.svg" for i in ORDER))
    if "--apply" in sys.argv:
        p = os.path.join(HERE, "..", "public", "index.html")
        s = open(p).read()
        a, b = "<!-- animals:begin -->", "<!-- animals:end -->"
        i, j = s.index(a) + len(a), s.index(b)
        shared = f'\n{MOUTH_DEFS}\n    <g id="aniBack"></g>\n{MOUTH}\n    <g id="aniFront"></g>\n    '
        s = s[:i] + shared + s[j:]
        a, b = "/* animals:begin */", "/* animals:end */"
        i, j = s.index(a) + len(a), s.index(b)
        data = {k: {"back": art[k][1], "front": art[k][2]} for k in ORDER}
        js = "\n  const ANIMAL_ORDER = " + json.dumps(ORDER) + ";\n  const ANIMALS = " + json.dumps(data, separators=(",", ":")) + ";\n  "
        s = s[:i] + js + s[j:]
        open(p, "w").write(s)
        print("updated public/index.html")
