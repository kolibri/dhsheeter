import os

import fitz  # PyMuPDF
import yaml
from typing import Self


def mm(inch: float) -> float:
    return inch * 72 / 25.4


class XY:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.raw = self.x, self.y
    def __eq__(self, other: Self) -> bool:
        return self.x == other.x and self.y == other.y
    def __str__(self):
        return str(self.x) + 'x' + str(self.y)
    def __hash__(self):
        return self.raw.__hash__()
    def add(self, other: Self):
        return XY(self.x + other.x, self.y + other.y)
    def sub(self, other: Self):
        return XY(self.x - other.x, self.y - other.y)
    def mult(self, factor: float):
        return XY(self.x * factor, self.y * factor)
    def div_abs(self, divisor: float):
        return XY(self.x // divisor, self.y // divisor)
    def in_area(self, area: [Self, Self]):
        return area[0].x <= self.x <= area[1].x and area[0].y <= self.y <= area[1].y
    def distance(self, other: Self):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    def angle(self, a: Self, c: Self) -> float:
        return math.degrees(math.atan2(c.y - self.y, c.x - self.x) - math.atan2(a.y - self.y, a.x - self.x))
    def flip(self) -> Self:
        return XY(self.y, self.x)
    def to_ints(self) -> Self:
        return XY(int(self.x), int(self.y))


def textbox(page, pos: XY, size: XY, text: str, fontsize: float = 12, lineheight: float = 1):
    if not text:
        return
    rect = fitz.Rect(mm(pos.x), mm(pos.y), mm(pos.x + size.x), mm(pos.y + size.y))

    ## try reducing font size
    base_letter_spacing = 1
    cfs = base_letter_spacing
    cfs = fontsize

    while cfs > 1:
        overflow = page.insert_textbox(
            rect,
            str(text),
            fontsize=cfs,
            lineheight=1.15,
            fontname="mainfont",
        )

        if overflow >= 0:   # text fits
            break
        cfs -= 0.5

def print_active_weapon(page, pos: XY, data):
    textbox(page, pos, XY(40, 8), data["name"])
    textbox(page, pos.add(XY(42,0)), XY(30, 8), data["trait_range"], 10)
    textbox(page, pos.add(XY(42+34,0)), XY(25, 8), data["damage"])
    if ("feature" in data):
        textbox(page, pos.add(XY(0,10)), XY(100, 25), data["feature"], 12, 1.8)

def page_sheet(page, data):
    page.insert_font(
        fontname="mainfont",
        fontfile="fonts/ComingSoon-Regular.ttf"
    )

    if "burden" in data and 1 == data["burden"]:
        textbox(page, XY(188, 54), XY(11,11), "x")
    if "burden" in data and 2 == data["burden"]:
        textbox(page, XY(188, 54), XY(11,11), "x")
        textbox(page, XY(195, 54), XY(11,11), "x")

    print_active_weapon(page, XY(105, 68), data["active_weapons"]["primary"])
    print_active_weapon(page, XY(105, 68).add(XY(0,33)), data["active_weapons"]["secondary"])

    textbox(page, XY(81,3.5), XY(40, 6), data["name"], 11)
    textbox(page, XY(155,3.5), XY(31, 6), data["pronouns"], 11)
    textbox(page, XY(82,10.5), XY(45, 6), data["community"] + " " + data["ancestry"], 11)
    textbox(page, XY(144,10.5), XY(42, 6), data["subclass"], 11)
    textbox(page, XY(195,6), XY(9, 12), data["level"], 20)

    textbox(page, XY(11,31), XY(8,10), data["evasion"],18)
    textbox(page, XY(34,31), XY(8,10), data["armor"], 18)
    textbox(page, XY(30,67), XY(7,6), data["threshold_minor"],11)
    textbox(page, XY(61,67), XY(7,6), data["threshold_major"],11)
    #textbox(page, XY(0,0), XY(8,9), data["hp"])
    #textbox(page, XY(0,0), XY(8,9), data["stress"])
    #textbox(page, XY(0,0), XY(8,9), data["hope"])
    i = 0
    for attr in ["agility", "strength", "finesse", "instinct", "presence", "knowledge"]:
        pos = XY(77,28).add(XY(23*i, 0))
        textbox(page, pos, XY(9,13), str(data["attributes"][attr]), 20)
        i = i + 1
    i = 0
    for exp in data["experiences"]:
        pos = XY(7,133).add(XY(0, 7*i))
        textbox(page, pos, XY(67,6), exp["name"], 11)
        textbox(page, pos.add(XY(75,0)), XY(10,6), "+ " + str(exp["mod"]), 11)
        i = i + 1
    # active armor
    textbox(page, XY(100,137), XY(52,6), data["active_armor"]["name"], 11)
    textbox(page, XY(100,137).add(XY(60,0)), XY(26,6), data["active_armor"]["base_thresholds"], 11)
    textbox(page, XY(100,137).add(XY(89,0)), XY(19,6), data["active_armor"]["base_score"], 11)
    textbox(page, XY(100,137).add(XY(7,10)), XY(97,14), data["active_armor"]["feature"], 11, 1.8)

    #inventory
    textbox(page, XY(100,171), XY(103,33), ', '.join(data["inventory"]), 11, 1.8)

    #inventory_weapons
    def print_inventory_weapon(page, pos: XY, data):
        textbox(page, pos.add(XY(0,0)), XY(41,6), data["name"], 11)
        textbox(page, pos.add(XY(43,0)), XY(32,6), data["trait_range"], 9)
        textbox(page, pos.add(XY(77,0)), XY(27,6), data["damage"], 11)
        textbox(page, pos.add(XY(3,9)), XY(98,18), data["feature"], 11, 1.8)

        if "burden" in data and 1 == data["burden"]:
            textbox(page, pos.add(XY(61, -5)), XY(11,11), "x")
        if "burden" in data and 2 == data["burden"]:
            textbox(page, pos.add(XY(61, -5)), XY(11,11), "x")
            textbox(page, pos.add(XY(65, -5)), XY(11,11), "x")

        if "hand" in data and data["hand"].lower().startswith("p"):
            textbox(page, pos.add(XY(71, -6)), XY(11,11), "x")
        if "hand" in data and data["hand"].lower().startswith("s"):
            textbox(page, pos.add(XY(89, -6)), XY(11,11), "x")


    i = 0
    for weapon in char["inventory_weapons"]:
        print_inventory_weapon(page, XY(101, 214).add(XY(0, 32*i)), weapon)
        i = i + 1

def page_cards(doc, data):

    carddoc = fitz.open("templates/cards.pdf")
    doc.insert_pdf(carddoc, start_at=2, from_page=0, to_page=0)
    page = doc[2]

    page.insert_font(
        fontname="mainfont",
        fontfile="fonts/ComingSoon-Regular.ttf"
    )
    fs = 9
    textbox(page, XY(47,10), XY(54,9), data["ancestry"], 11)
    if "ancestry_feats" in data:
        if 0 < len(data["ancestry_feats"]):
            textbox(page, XY(10,17), XY(86,16), data["ancestry_feats"][0], fs, 1.2)
        if 1 < len(data["ancestry_feats"]):
            textbox(page, XY(10,34), XY(86,16), data["ancestry_feats"][1], fs, 1.2)

    textbox(page, XY(50,64), XY(51,9), data["community"], 11)
    if "community_feat" in data:
        textbox(page, XY(11,70), XY(86,34), data["community_feat"], fs, 1.2)

    def printsubclass(page, pos, data):
        if "name" in data:
            textbox(page, XY(41, 117).add(XY(0, pos*54)), XY(55,9), data["name"], 11)
        if "basename" in data:
            textbox(page, XY(10, 134).add(XY(0, pos*54)), XY(44,8), data["basename"], fs)
        if "trait" in data:
            textbox(page, XY(56, 134).add(XY(0, pos*54)), XY(45,8), data["trait"], fs)
        if "specialization" in data:
            ap = XY(0,0)
            if 2 == data["specialization"]:
                ap = XY(15,0)
            if 3 == data["specialization"]:
                ap = XY(47,0)
            textbox(page, XY(17, 127).add(XY(0, pos*54)).add(ap), XY(5,8), 'x', fs)
        if "feature" in data:
            textbox(page, XY(11, 143).add(XY(0, pos*54)), XY(86,14), data["feature"], fs, 1.2)

    i=0
    if "subclasses" in data:
        for subclass in data["subclasses"]:
            printsubclass(page, i, subclass)
            i = i+1

    def printcard(page, gridpos, data):
        gridbase = XY(5,8)
        pos = gridbase.add(XY(gridpos.x * 100, gridpos.y * 54))

        if "name" in data:
            textbox(page, pos.add(XY(48,2 )), XY(47,9), data["name"], 11)
        if "domain" in data:
            textbox(page, pos.add(XY(6,11)), XY(47,9), data["domain"], 11)
        if "type" in data:
            textbox(page, pos.add(XY(45,11)), XY(47,9), data["type"], 11)
        if "cost" in data:
            textbox(page, pos.add(XY(85,11)), XY(86,22), data["cost"], 11)
        if "feature" in data:
            textbox(page, pos.add(XY(6,20)), XY(86,22), data["feature"], 11)

    i = 0
    for card in data["cards"][:5]:
        printcard(page, XY(1,i), card)
        i = i + 1

    i = 0
    if 5 < len(data["cards"]):
        doc.insert_pdf(carddoc, start_at=3, from_page=1, to_page=1)
        page = doc[3]
        page.insert_font(
            fontname="mainfont",
            fontfile="fonts/ComingSoon-Regular.ttf"
        )

        for card in data["cards"][5:]:
            printcard(doc[3], XY(int(i/5),i%5), card)
            i = i + 1

def page_level(doc, data):
    page = doc[1]
    page.insert_font(
        fontname="mainfont",
        fontfile="fonts/ComingSoon-Regular.ttf"
    )

    def print_level(page, pos, data):
        yposmod = 0

        if 0 < pos:
            yposmod = 63
        if 1 < pos:
            yposmod = 136

        if 1 <= data.count("attr"):
            textbox(page, XY(17,198).add(XY(yposmod, 0)), XY(10,10), "x")
        if 2 <= data.count("attr"):
            textbox(page, XY(12,198).add(XY(yposmod, 0)), XY(10,10), "x")
        if 3 <= data.count("attr"):
            textbox(page, XY( 8,198).add(XY(yposmod, 0)), XY(10,10), "x")

        if 1 <= data.count("hp"):
            textbox(page, XY(17,208).add(XY(yposmod, 0)), XY(10,10), "x")
        if 2 <= data.count("hp"):
            textbox(page, XY(12,208).add(XY(yposmod, 0)), XY(10,10), "x")

        sy = 213 if pos > 0 else 216
        if 1 <= data.count("stress"):
            textbox(page, XY(17,sy).add(XY(yposmod, 0)), XY(10,10), "x")
        if 2 <= data.count("stress"):
            textbox(page, XY(12,sy).add(XY(yposmod, 0)), XY(10,10), "x")

        fy = 1 if pos > 0 else 0
        if 1 <= data.count("exp"):
            textbox(page, XY(17,222-fy).add(XY(yposmod, 0)), XY(10,10), "x")
        if 1 <= data.count("card"):
            textbox(page, XY(17,229).add(XY(yposmod, 0)), XY(10,10), "x")
        if 1 <= data.count("evasion"):
            textbox(page, XY(17,240-fy).add(XY(yposmod, 0)), XY(10,10), "x")

        if 1 <= data.count("subclass"):
            textbox(page, XY(17,246).add(XY(yposmod, 0)), XY(10,10), "x")

        if 1 <= data.count("prof"):
            textbox(page, XY(17,259.5).add(XY(yposmod, 0)), XY(10,10), "x")
        if 2 <= data.count("prof"):
            textbox(page, XY(12,259.5).add(XY(yposmod, 0)), XY(10,10), "x")
        if 1 <= data.count("multiclass"):
            textbox(page, XY(17,264).add(XY(yposmod, 0)), XY(10,10), "x")
        if 2 <= data.count("multiclass"):
            textbox(page, XY(12,264).add(XY(yposmod, 0)), XY(10,10), "x")

    if "levels" in data:
        if "t2" in data["levels"]:
            print_level(page, 0, data["levels"]["t2"])
        if "t3" in data["levels"]:
            print_level(page, 1, data["levels"]["t3"])
        if "t4" in data["levels"]:
            print_level(page, 2, data["levels"]["t4"])

def print_sheets(filename,data):
    file = data["template"].lower()
    if file not in ['bard', 'druid', 'guardian', 'ranger', 'rouge', 'seraph', 'sorcerer', 'warrior', 'wizard'] :
        print('No template for ', data['template'])
        return
    doc = fitz.open("templates/"+ file + ".pdf")

    page_sheet(doc[0], data)
    page_cards(doc, data)
    page_level(doc, data)

    outname = os.path.splitext(filename)[0]
    print('# saving ', outname)
    doc.save("out/" + outname + ".pdf")

files = [f for f in os.listdir("chardata") if f.endswith(".yaml")]
for file in files:
    with open(os.path.join("chardata",file ), "r") as f:
        char = yaml.safe_load(f)
    print_sheets(file,char)
