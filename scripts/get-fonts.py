#!/usr/bin/env python3
# This script downloads several Noto fonts from https://github.com/notofonts/noto-fonts
# That repo was archived in 2023 and is no longer updated.
# Additional fonts can be found on https://notofonts.github.io

import os
import re
import requests
import tempfile
import shutil
import warnings
import yaml
import zipfile

FONTDIR = os.environ.get("FONTDIR", "./fonts")

try:
    os.mkdir(FONTDIR)
except FileExistsError:
    warnings.warn("Font directory already exists")

def downloadToFile(urls, destination, dir=FONTDIR):
    headers = {"User-Agent": "get-fonts.py/osm-carto"}

    try:
        r = requests.get(urls[0], headers=headers)
        if r.status_code != 200:
            if len(urls) > 1:
                warnings.warn(f"Failed to download {urls[0]}, retrying with next font source")
                downloadToFile(urls[1:], destination, dir=dir)
            else:
                raise Exception
        with open(os.path.join(dir, destination), "wb") as f:
            f.write(r.content)
    except:
        raise Exception(f"Failed to download {urls}")

# return a CartoCSS-friendly name for installed fonts
# example: NotoSansCherokee -> Noto Sans Cherokee
# support: Noto Sans NKo, Noto Sans Symbols2
def cartoFont(script, variation):
    return f"{re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', script)} {variation.capitalize()}"

# prepare to save font names to MSS file
regularFonts = []
boldFonts = []

# download scripts in alphabetical order
fontInfo = yaml.safe_load(open('scripts/fonts.yaml', 'r'))
scripts = sorted(list(fontInfo['fonts'].keys()))
for script in scripts:
    scriptInfo = fontInfo['fonts'][script]
    variations = ['regular'] + (scriptInfo.get('variations', []))
    regularFonts.append(cartoFont(script, 'Regular'))
    for variation in variations:
        filename = f"{script}-{variation.capitalize()}.ttf"
        fontUrls = list(map(lambda url: url + filename, scriptInfo['urls']))
        downloadToFile(fontUrls, filename)
        if variation in ['bold', 'black']:
            boldFonts.append(cartoFont(script, variation.capitalize()))

# reformat fonts.mss
reformattedMSS = ""
with open('./style/fonts.mss', 'r') as fontCartoFile:
    fontCartoContent = fontCartoFile.read()

    # write in regular fonts
    try:
        regularStart = fontCartoContent.index('/* {regular fonts} */')
        regularEnd = fontCartoContent.index('/* {/regular fonts} */')
    except:
        raise Exception("File fonts.mss did not include {regular fonts} {/regular fonts} tags")
    reformattedMSS = fontCartoContent[:regularStart + 21] + "\n"
    for font in regularFonts:
        if font not in ['Noto Sans Regular']:
            reformattedMSS += f"                \"{font}\",\n"
    reformattedMSS += f"                {fontCartoContent[regularEnd:]}"

    # write in bold/black fonts
    fontCartoContent = reformattedMSS
    try:
        boldStart = fontCartoContent.index('/* {bold fonts} */')
        boldEnd = fontCartoContent.index('/* {/bold fonts} */')
    except:
        raise Exception("File fonts.mss did not include {bold fonts} {/bold fonts} tags")
    reformattedMSS = fontCartoContent[:boldStart + 18] + "\n"
    for font in boldFonts:
        if font not in ['Noto Sans Bold']:
            reformattedMSS += f"                \"{font}\",\n"
    reformattedMSS += f"                {fontCartoContent[boldEnd:]}"

with open('./style/fonts.mss', 'w') as outputMSS:
    outputMSS.write(reformattedMSS)

# Other noto fonts which don't follow the URL pattern above

# CJK fonts
downloadToFile(
    [
        "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf"
    ],
    "NotoSansCJKjp-Regular.otf",
)
downloadToFile(
    [
        "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Bold.otf"
    ],
    "NotoSansCJKjp-Bold.otf",
)

# Fonts in zipfiles need a temporary directory
TMPDIR = tempfile.mkdtemp(prefix="get-fonts.")

# Noto Emoji B&W isn't available as a separate download, so we need to download the package and unzip it
downloadToFile(
    ["https://archive.org/download/noto-emoji/Noto_Emoji.zip"],
    "Noto_Emoji.zip",
    dir=TMPDIR,
)
emojiPath = os.path.join(TMPDIR, "Noto_Emoji.zip")
emojiExtract = ["NotoEmoji-Regular.ttf", "NotoEmoji-Bold.ttf"]
with zipfile.ZipFile(emojiPath, "r") as zip_ref:
    for file in emojiExtract:
        source = zip_ref.getinfo(f"static/{file}")
        zip_ref.extract(source, FONTDIR)
        # move from FONTDIR/static/x to overwrite FONTDIR/x
        unzipSrc = os.path.join(FONTDIR, file)
        if os.path.exists(unzipSrc):
            os.remove(unzipSrc)
        shutil.move(os.path.join(FONTDIR, "static", file), FONTDIR)

downloadToFile(
    ["https://mirrors.dotsrc.org/osdn/hanazono-font/68253/hanazono-20170904.zip"],
    "hanazono.zip",
    dir=TMPDIR,
)
hanazonoPath = os.path.join(TMPDIR, "hanazono.zip")
with zipfile.ZipFile(hanazonoPath, "r") as zip_ref:
    for file in ["HanaMinA.ttf", "HanaMinB.ttf"]:
        source = zip_ref.getinfo(file)
        zip_ref.extract(source, FONTDIR)

# clean up tmp directories
shutil.rmtree(TMPDIR)
fontdir_static = os.path.join(FONTDIR, "static")
if os.path.exists(fontdir_static):
    shutil.rmtree(fontdir_static)
