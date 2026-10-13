"""One zip per video, ready to drop into Desktop/YouTube: inside, a folder with the video, the 3 thumbnails, the title,
the description, the subtitles, and the tags and settings. ranger_mes_videos.bat/.ps1 (Windows) and .command (Mac)
unpack every zip into Desktop/YouTube, numbered after the folders already there, skipping a video already filed."""
import os
import re
import shutil
import sys
import zipfile

D = os.path.dirname(os.path.abspath(__file__))
R = "/home/user/cadence/youtube_montage/scripts"
T = os.path.join(D, "thumbs")
BATCH = sys.argv[1] if len(sys.argv) > 1 else "night1"
OUT = os.path.join(D, "livraison" if BATCH == "night1" else "livraison_" + BATCH)
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
TD = os.path.join(D, "thumbs_doodle")

VIDEOS = [
    dict(name="Every ETF Explained (version humaine)", video="web/etf_human.mp4", file="Every ETF Explained in 11 Minutes",
         kit="kit_etf_h/every_etf_human_youtube_upload.txt", srt="kit_etf_h/every_etf_human_subtitles_en.srt",
         thumbs=[("X1", T + "/thumb_X1_etf_basket.jpg"), ("S1", T + "/thumb_S1_etf_list.jpg"), ("S3", T + "/thumb_S3_etf_12.jpg")],
         note="Remplace la vidéo ETF programmée demain (mercredi) à 16 h : même titre, même description, montage « passe humaine ».",
         thumbs_line="X1 (panier d'ETF), S1 (liste des 12 boîtes) et S3 (« 12. »)"),
    dict(name="Every Investment Account in Europe Explained", video="web/every_account_1080p.mp4",
         kit=R + "/every_account_youtube_upload.txt", srt=R + "/every_account_subtitles_en.srt",
         thumbs=[("X3", T + "/thumb_X3_accounts_which_one.jpg"), ("A4", T + "/thumb_A4_accounts_cards.jpg"), ("A1", T + "/thumb_A1_accounts_list.jpg")]),
    dict(name="Every Investing Mistake Explained", video="web/every_mistake_1080p.mp4",
         kit=R + "/every_mistake_youtube_upload.txt", srt=R + "/every_mistake_subtitles_en.srt",
         thumbs=[("X4", T + "/thumb_X4_mistakes_dont_press.jpg"), ("M5", T + "/thumb_M5_mistakes_quote.jpg"), ("M6", T + "/thumb_M6_mistakes_checklist.jpg")]),
    dict(name="How to Save Money So Easily It Feels Illegal", video="web/save_money_illegal.mp4",
         kit=R + "/save_money_illegal_youtube_upload.txt", srt=R + "/save_money_illegal_subtitles_en.srt",
         thumbs=[("S1", D + "/thumbs_save/S1_feels_illegal.jpg"), ("S2", D + "/thumbs_save/S2_autopilot.jpg"), ("S3", D + "/thumbs_save/S3_brain_now.jpg")]),
    dict(name="Every Bank Fee Explained", video="web/every_fee_1080p.mp4",
         kit=R + "/every_fee_youtube_upload.txt", srt=R + "/every_fee_subtitles_en.srt",
         thumbs=[("X5", T + "/thumb_X5_fees_never_press.jpg"), ("F4", T + "/thumb_F4_fees_statement.jpg"), ("F5", T + "/thumb_F5_fees_atm.jpg")]),
    dict(name="POV - You Invest 10,000 euros at the Worst Possible Moment", video="web/pov_worst_moment_1080p.mp4",
         kit=R + "/pov_worst_moment_youtube_upload.txt", srt=R + "/pov_worst_moment_subtitles_en.srt",
         thumbs=[("X6", T + "/thumb_X6_worst_bought_here.jpg"), ("W4", T + "/thumb_W4_worst_calendar.jpg"), ("W1", T + "/thumb_W1_worst_10000.jpg")]),
]


def txt(s):
    """Text for Windows Notepad as well as Mac: UTF-8 with BOM, CRLF line ends."""
    return ("﻿" + s.strip("\n").replace("\r\n", "\n").replace("\n", "\r\n") + "\r\n").encode("utf-8")


def section(kit, head, nxt):
    a = kit.index(head)
    a = kit.index("\n", a) + 1
    b = kit.index(nxt, a) if nxt else len(kit)
    return kit[a:b].strip("\n")


def build(k, v):
    kit = open(os.path.join(D, v["kit"]), encoding="utf-8").read()
    if v.get("thumbs_line"):
        kit = re.sub(r"(Miniatures « Test & compare » : ).*", lambda m: m.group(1) + v["thumbs_line"] + ".", kit)
    title_block = section(kit, "TITRE (", "DESCRIPTION (")
    lines = [l for l in title_block.split("\n")]
    title = lines[0].strip()
    variants = [l.strip() for l in lines[lines.index("Variantes à tester :") + 1:] if l.strip()] if "Variantes à tester :" in lines else []
    desc = section(kit, "DESCRIPTION (", "TAGS (")
    tags_head = kit[kit.index("TAGS ("):kit.index("\n", kit.index("TAGS ("))]
    tags = section(kit, "TAGS (", "RÉGLAGES")
    settings = section(kit, "RÉGLAGES", None)
    srt_name = "sous-titres anglais.srt"
    settings = re.sub(r"importe \S+\.srt", f"importe « {srt_name} »", settings)
    thumb_names = []
    for j, (lab, _) in enumerate(v["thumbs"]):
        thumb_names.append(f"miniature {j + 1} - {lab}" + (" (recommandee)" if j == 0 else "") + ".jpg")
    settings += "\n- Fichiers miniatures : " + ", ".join(thumb_names) + "."
    files = {
        f"{v.get('file', v['name'])}.mp4": ("file", os.path.join(D, v["video"])),
        "titre.txt": ("bytes", txt(("NOTE : " + v["note"] + "\n\n" if v.get("note") else "") + "TITRE\n" + title +
                                   ("\n\nVariantes à tester (onglet « Test & compare » ou plus tard) :\n" + "\n".join(variants) if variants else ""))),
        "description.txt": ("bytes", txt(desc)),
        "sous-titres anglais.srt": ("file", os.path.join(D, v["srt"])),
        "tags et reglages.txt": ("bytes", txt(tags_head + "\n" + tags + "\n\n\nRÉGLAGES\n" + settings)),
    }
    for n_, (lab, p) in zip(thumb_names, v["thumbs"]):
        files[n_] = ("file", p)
    zp = os.path.join(OUT, f"EuroUnboxed {k} - {v['name']}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        for n_, (kind, data) in files.items():
            arc = f"{v['name']}/{n_}"
            if kind == "file":
                z.write(data, arc)
            else:
                z.writestr(arc, data)
    return zp


NIGHT2 = [
    dict(name="Compound Interest Explained So Simply It Feels Illegal", video="web/compound_interest.mp4",
         kit="kit_compound/compound_interest_youtube_upload.txt", srt="kit_compound/compound_interest_subtitles_en.srt",
         thumbs=[("A1", TD + "/A1_time.jpg"), ("A2", TD + "/A2_anna_ben.jpg"), ("A3", TD + "/A3_rule_72.jpg")]),
    dict(name="7 Tricks Shops Use to Make You Spend More", video="web/shop_tricks.mp4",
         kit="kit_tricks/shop_tricks_youtube_upload.txt", srt="kit_tricks/shop_tricks_subtitles_en.srt",
         thumbs=[("B1", TD + "/B1_999.jpg"), ("B2", TD + "/B2_fake_timer.jpg"), ("B3", TD + "/B3_decoy.jpg")]),
    dict(name="How to Invest Your First 1,000 euros So Simply It Feels Illegal", video="web/first_1000.mp4",
         kit="kit_first1000/first_1000_youtube_upload.txt", srt="kit_first1000/first_1000_subtitles_en.srt",
         thumbs=[("C1", TD + "/C1_now_what.jpg"), ("C2", TD + "/C2_8_steps.jpg"), ("C3", TD + "/C3_buy_everything.jpg")]),
    dict(name="How to Pay Off Debt So Fast It Feels Illegal", video="web/pay_off_debt.mp4",
         kit="kit_debt/pay_off_debt_youtube_upload.txt", srt="kit_debt/pay_off_debt_subtitles_en.srt",
         thumbs=[("D1", TD + "/D1_boulder.jpg"), ("D2", TD + "/D2_minimum_button.jpg"), ("D3", TD + "/D3_which_order.jpg")]),
]
if BATCH == "night2":
    VIDEOS = [v for v in NIGHT2 if os.path.exists(os.path.join(D, v["video"]))]
    zips = [build(9 + k, v) for k, v in enumerate(VIDEOS)]
else:
    zips = [build(k + 1, v) for k, v in enumerate(VIDEOS)]

# Shorts and TikTok: one folder each, with their titles, descriptions and calendar
plan = open(os.path.join(D, "shorts", "shorts_upload.txt"), encoding="utf-8").read()
packs = [("Shorts YouTube - semaine 1", [f for f in sorted(os.listdir(os.path.join(D, "shorts"))) if f.startswith("short_") and "tiktok" not in f and f.endswith(".mp4")],
          "titres, descriptions et calendrier.txt", plan),
         ("TikTok - semaine 1", [f for f in sorted(os.listdir(os.path.join(D, "shorts"))) if f.startswith("short_tiktok_") and f.endswith(".mp4")],
          "legendes TikTok.txt", "Mêmes textes que les Shorts YouTube, sans « #shorts » ; les fichiers short_tiktok_* finissent sur « Full video on YouTube · "
          "Euro Unboxed ». Active l'étiquette « contenu généré par l'IA » (voix synthétique).\n\n" + plan)]
for k, (name, vids, tname, ttxt) in enumerate(packs if BATCH == "night1" else [], len(VIDEOS) + 1):
    zp = os.path.join(OUT, f"EuroUnboxed {k} - {name}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        for f in vids:
            z.write(os.path.join(D, "shorts", f), f"{name}/{f}")
        z.writestr(f"{name}/{tname}", txt(ttxt))
    zips.append(zp)

PS1 = r'''# Range les vidéos Euro Unboxed : chaque zip "EuroUnboxed N - ..." de ce dossier devient un dossier numéroté
# dans Bureau\YouTube, à la suite des dossiers déjà présents. Une vidéo déjà rangée (même nom de dossier) est ignorée.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$yt = Join-Path ([Environment]::GetFolderPath("Desktop")) "YouTube"
New-Item -ItemType Directory -Force -Path $yt | Out-Null
$existing = @(Get-ChildItem -LiteralPath $yt -Directory)
$nums = @(foreach ($d in $existing) { if ($d.Name -match '^(\d+)') { [int]$Matches[1] } })
if ($nums.Count -gt 0) { [int]$n = ($nums | Measure-Object -Maximum).Maximum } else { [int]$n = $existing.Count }
$zips = Get-ChildItem -LiteralPath $here -Filter "EuroUnboxed *.zip" | Sort-Object { [int](($_.BaseName -split ' ')[1]) }
if (-not $zips) { Write-Host "Aucun zip 'EuroUnboxed ...' a cote de ce fichier." }
foreach ($z in $zips) {
  $tmp = Join-Path $yt ("_tmp_" + [guid]::NewGuid().ToString("N"))
  try {
    Expand-Archive -LiteralPath $z.FullName -DestinationPath $tmp
    foreach ($f in Get-ChildItem -LiteralPath $tmp -Directory) {
      $already = $existing | Where-Object { $_.Name.EndsWith($f.Name) }
      if ($already) { Write-Host ("Deja range : " + $f.Name); continue }
      $n = $n + 1
      $dest = Join-Path $yt (("{0:D2}" -f $n) + " - " + $f.Name)
      Move-Item -LiteralPath $f.FullName -Destination $dest
      Write-Host ("Range : " + $dest)
    }
  } finally {
    if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Recurse -Force }
  }
}
Write-Host ""
Write-Host ("Termine. Tout est dans : " + $yt)
Start-Process explorer.exe $yt
'''
BAT = '@echo off\r\npowershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ranger_mes_videos.ps1"\r\npause\r\n'
CMD = r'''#!/bin/bash
# Range les vidéos Euro Unboxed (Mac) : chaque zip "EuroUnboxed N - ..." de ce dossier devient un dossier numéroté
# dans Bureau/YouTube, à la suite des dossiers déjà présents. Une vidéo déjà rangée est ignorée.
cd "$(dirname "$0")" || exit 1
YT="$HOME/Desktop/YouTube"
mkdir -p "$YT"
n=$(ls -1 "$YT" | grep -oE '^[0-9]+' | sort -n | tail -1)
[ -z "$n" ] && n=$(find "$YT" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
n=$((10#$n))
while IFS= read -r z; do
  tmp="$YT/_tmp_$$"
  mkdir -p "$tmp" && unzip -q "$z" -d "$tmp"
  for f in "$tmp"/*/; do
    name=$(basename "$f")
    if ls -1 "$YT" | grep -v '^_tmp_' | grep -qF -- "$name"; then echo "Déjà rangé : $name"; continue; fi
    n=$((n + 1))
    mv "$f" "$YT/$(printf '%02d' "$n") - $name"
    echo "Rangé : $(printf '%02d' "$n") - $name"
  done
  rm -rf "$tmp"
done < <(ls -1 EuroUnboxed\ *.zip 2>/dev/null | sort -t' ' -k2,2n)
echo "Terminé. Tout est dans : $YT"
open "$YT"
'''
open(os.path.join(OUT, "ranger_mes_videos.ps1"), "wb").write(("﻿" + PS1).replace("\n", "\r\n").encode("utf-8"))
open(os.path.join(OUT, "ranger_mes_videos.bat"), "w", newline="").write(BAT)
open(os.path.join(OUT, "ranger_mes_videos.command"), "w", newline="\n").write(CMD)
os.chmod(os.path.join(OUT, "ranger_mes_videos.command"), 0o755)
for zp in zips:
    print(f"{os.path.getsize(zp) / 2**20:5.1f} MiB  {os.path.basename(zp)}")
