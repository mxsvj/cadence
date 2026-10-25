"""Louder thumbnails for 'How to Invest Your First €1,000 (8 Steps, in Order)' (C4, C5), in the style that worked for the
shop-tricks video (B10): a flat block of colour on half the frame, a shocked face, three or four words.
C4: the €1,000 and 'do THIS first.' (the video's step 1: kill expensive debt). C5: the 8-step staircase, 'in THIS order.'"""
from thumbs_tricks_punchy import *  # noqa: F401,F403
from thumbs_tricks_punchy import block, d, render, shock

ims = []
# ---------------------------------------------------------------- C4: €1,000 - do THIS first
note = [(1150, 230), (1790, 190), (1830, 560), (1190, 600)]
els = [block([(1000, -20), (1940, -20), (1940, 1100), (1150, 1100)], ORANGE),
       d([Fl(P_poly(note, True), (214, 226, 196)), stk(P_poly(note, True), 9),
          stk(P_poly([(1190, 260), (1760, 225), (1795, 530), (1225, 565)], True), 4, GREY)], 3),
       T("€1,000", 1490, 440, 150, INK, at=0, anchor="m", rot=-4),
       d(shock(520, 690, 200, look=1.0), 5),
       T("do THIS", 90, 210, 170, INK, at=0, rot=-3), T("first.", 160, 420, 200, RED, at=0, rot=-3)]
assert 90 + text_w("do THIS", 170) < 1000
ims.append(render("C4_do_this_first", els))
# ---------------------------------------------------------------- C5: the staircase - in THIS order
pts = [(1000, 1000)]
for k in range(8):
    x, y = 1000 + k * 110, 1000 - k * 100
    pts += [(x + 110, y)] + ([(x + 110, y - 100)] if k < 7 else [])
els = [block([(940, -20), (1940, -20), (1940, 1100), (1060, 1100)], HL),
       d([stk(P_poly(pts), 12)], 2)]
for k in range(8):
    els.append(T(str(k + 1), 1055 + k * 110, 975 - k * 100, 80, RED if k == 0 else INK, at=0, anchor="m"))
els += [d(shock(470, 700, 190, look=1.0), 5),
        T("in THIS", 90, 210, 170, INK, at=0, rot=-3), T("order.", 150, 420, 200, RED, at=0, rot=-3),
        T("€1,000", 1230, 230, 130, INK, at=0, rot=-4)]
ims.append(render("C5_in_this_order", els))

small = Image.new("RGB", (2 * 178 + 10, 114), (255, 255, 255))
for k, im in enumerate(ims):
    small.paste(im.resize((168, 94), Image.LANCZOS), (10 + k * 178, 10))
small.save(os.path.join(OUT, "feed_size_C4_C5.png"))
print("ok")
