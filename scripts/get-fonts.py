import os
import re
import requests
import warnings

FONTDIR = "./fonts"

try:
    os.mkdir(FONTDIR)
except FileExistsError:
    warnings.warn("Directory already exists")

fontURLs = []
fontRecords = requests.get(
    "https://raw.githubusercontent.com/notofonts/notofonts.github.io/main/state.json"
).json()
for script in fontRecords.keys():
    if "families" in fontRecords[script]:
        for fontName in fontRecords[script]["families"].keys():
            for file in fontRecords[script]["families"][fontName]["files"]:
                fontURLs.append(f"{script}/{file}")

# Fonts available in regular, bold, and italic
REGULAR_BOLD_ITALIC = ["NotoSans"]

# Fonts available in regular and bold
REGULAR_BOLD = [
    "NotoSansAdlamUnjoined",
    "NotoSansArabicUI",
    "NotoSansArmenian",
    "NotoSansBalinese",
    "NotoSansBamum",
    "NotoSansBengaliUI",
    "NotoSansCanadianAboriginal",
    "NotoSansCham",
    "NotoSansCherokee",
    "NotoSansDevanagariUI",
    "NotoSansEthiopic",
    "NotoSansGeorgian",
    "NotoSansGujaratiUI",
    "NotoSansGurmukhiUI",
    "NotoSansHebrew",
    "NotoSansJavanese",
    "NotoSansKannadaUI",
    "NotoSansKayahLi",
    "NotoSansKhmerUI",
    "NotoSansLaoUI",
    "NotoSansLisu",
    "NotoSansMalayalamUI",
    "NotoSansMyanmarUI",
    "NotoSansOlChiki",
    "NotoSansOriya",
    "NotoSansSinhalaUI",
    "NotoSansSundanese",
    "NotoSansSymbols",
    "NotoSansTaiTham",
    "NotoSansTamilUI",
    "NotoSansTeluguUI",
    "NotoSansThaana",
    "NotoSansThaiUI",
    "NotoSerifTibetan",
]

# Fonts with regular and black, but no bold
REGULAR_BLACK = ["NotoSansSyriac"]

# Fonts only available in regular
REGULAR = [
    "NotoSansBatak",
    "NotoSansBuginese",
    "NotoSansBuhid",
    "NotoSansChakma",
    "NotoSansCoptic",
    "NotoSansHanunoo",
    "NotoSansLepcha",
    "NotoSansLimbu",
    "NotoSansMandaic",
    "NotoSansMongolian",
    "NotoSansNewTaiLue",
    "NotoSansNKo",
    "NotoSansOsage",
    "NotoSansOsmanya",
    "NotoSansSamaritan",
    "NotoSansSaurashtra",
    "NotoSansShavian",
    "NotoSansSymbols2",
    "NotoSansTagalog",
    "NotoSansTagbanwa",
    "NotoSansTaiLe",
    "NotoSansTaiViet",
    "NotoSansTifinagh",
    "NotoSansVai",
    "NotoSansYi",
]

# Download the fonts in the lists above


def findFontUrl(filename):
    selectFont = None
    for url in fontURLs:
        if ("unhinted" in url) and (filename in url):
            if selectFont is not None:
                raise Exception(f"Multiple possible fonts for {filename}")
            selectFont = url
    if (selectFont is None) and ("UI" in filename):
        # 5 scripts go around UI font
        selectFont = findFontUrl(filename.replace("UI", ""))
    if selectFont is None:
        raise Exception(f"No font found for {filename}")
    return selectFont


def downloadToFile(url, destination):
    if ("UI-" not in url) and ("UI-" in destination):
        url = re.sub("-([RBI])", "UI-\\1", url).replace("/unhinted", "UI/unhinted")
    try:
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception
        with open(destination, "wb") as f:
            f.write(r.content)
    except:
        raise Exception(f"Failed to download {url}")


for font in REGULAR_BOLD + REGULAR_BOLD_ITALIC + REGULAR_BLACK + REGULAR:
    regular = f"{font}-Regular.ttf"
    regularFontUrl = findFontUrl(regular)
    downloadToFile(
        f"https://notofonts.github.io/{regularFontUrl}", f"{FONTDIR}/{regular}"
    )

    if (font in REGULAR_BOLD) or (font in REGULAR_BOLD_ITALIC):
        bold = f"{font}-Bold.ttf"
        boldFontUrl = findFontUrl(bold)
        downloadToFile(
            f"https://notofonts.github.io/{boldFontUrl}", f"{FONTDIR}/{bold}"
        )

    if font in REGULAR_BOLD_ITALIC:
        italic = f"{font}-Italic.ttf"
        italicFontUrl = findFontUrl(italic)
        downloadToFile(
            f"https://notofonts.github.io/{italicFontUrl}", f"{FONTDIR}/{italic}"
        )

    if font in REGULAR_BLACK:
        black = f"{font}-Black.ttf"
        blackFontUrl = findFontUrl(black)
        downloadToFile(
            f"https://notofonts.github.io/{blackFontUrl}", f"{FONTDIR}/{black}"
        )
