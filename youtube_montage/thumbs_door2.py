"""Thumbnails for 'Don't Open the Door' episode 2: the baker whose head has turned all the way round ('don't make a
sound.'), and the two hands at the stairs ('which one is Noah?'). Dark pages, three or four words, badge corner empty."""
from thumbs_door1 import *  # noqa: F401,F403
from thumbs_door1 import d, render
from build_door1 import KSKIN, WHITE, back_fig, black
from build_door2 import front_head  # noqa: F401  (also registers the 'handin' poses)

ims = []
# ---------------------------------------------------------------- F1: the baker, head turned round
bx, by, bs = 1300, 1180, 2.6
els = [black(0.97), d([Fl(P_rect(bx - 290, 60, 580, 1100, 0), (130, 150, 120)), stk(P_rect(bx - 290, 60, 580, 1100, 6), 8, (90, 86, 92))], 2),
       d(back_fig(bx, by, bs, hair=None), 3), d(front_head(bx, by, bs), 4),
       d([stk(P_ell(bx - 34, by - 124 * bs - 6, 30, 18, 1, 0.06), 7, WHITE), stk(P_ell(bx + 34, by - 124 * bs - 6, 30, 18, 2, 0.06), 7, WHITE),
          stk(P_line(bx - 4, by - 124 * bs, bx - 24, by - 124 * bs + 80, 0.02, 3), 7, WHITE),
          stk(P_line(bx + 4, by - 124 * bs, bx + 26, by - 124 * bs + 84, 0.02, 4), 7, WHITE)], 5),       # apron strings tied at his back
       T("don't", 110, 330, 190, WHITE, at=0, rot=-4), T("make a", 130, 540, 190, WHITE, at=0, rot=-4), T("sound.", 150, 790, 230, RED, at=0, rot=-4)]
ims.append(render("F1_dont_make_a_sound", els))
# ---------------------------------------------------------------- F2: two Noahs - one in the dark doorway upstairs, one holding her hand
els = [d([Fl(P_rect(1320, 70, 330, 560, 0), (226, 219, 205)), stk(P_rect(1320, 70, 330, 560, 7), 8),
          Fl(P_rect(1350, 100, 270, 530, 0), (112, 116, 124))], 2),
       Fig(1485, 600, 1.25, poses=[("wait", 0)], moods=[("blank", 0)], kind="spiky", seed=12, enter="none", idle=0.0, skin=KSKIN),
       d([stk(P_line(1320, 630, 1650, 630, 0.01, 5), 7, (200, 196, 190))], 5),
       Fig(880, 1060, 1.15, poses=[("handin", 0)], moods=[("worried", 0)], kind="spiky", seed=12, enter="none", idle=0.0),
       Fig(1120, 1060, 1.6, poses=[("handin_l", 0)], moods=[("wow", 0)], kind="bob", seed=13, enter="none", idle=0.0),
       T("which one", 110, 330, 170, INK, at=0, rot=-4), T("is", 130, 540, 170, INK, at=0, rot=-4), T("Noah?", 300, 560, 230, RED, at=0, rot=-4)]
ims.append(render("F2_which_one_is_noah", els))

small = Image.new("RGB", (2 * 178 + 10, 114), (255, 255, 255))
for k, im in enumerate(ims):
    small.paste(im.resize((168, 94), Image.LANCZOS), (10 + k * 178, 10))
small.save(os.path.join(OUT, "feed_size_ep2.png"))
print("ok")
