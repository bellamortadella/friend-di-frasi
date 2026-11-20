"""Build the Friend di Frasi companion page from the Anki sheet CSV.

Usage: python3 -I data/build.py "<path to exported CSV>"
Writes data/cards.json and friend-di-frase.html (from template.html).
Tags are one letter per card, in deck order. Add letters when you add cards.
"""
import csv, json, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# A Asking · F Feelings · O Opinions · T Plans & time · E Food & out · D Day to day · P People
TAGS = {
    "1.0": "OPAAAOAAAE" "DPDAAPPTOP" "EFEEDOFFFO" "OOOFFEOEDO" "OFOFTTDATE"
           "AOAFOOAETF" "TOOOOOOTTT" "TTTTTTFFFT" "FOFAFAEAAO",
    "1.1": "OTDDATAFEF" "DDOAFADFPE" "TODPOAPTPA" "FAEDPTTFOP" "OODDDDTDDD"
           "FTAPOOOPFD" "EOEFDDDPPP" "DEDFAOPDTF" "DODPTTFPOT" "FPF",
    "1.2": "EATFTTDDDO" "TOPAOTTDPA" "EOEFTOODEO" "OOOTDDEOFA" "OPFAAFFODD"
           "DOTEEADOOT" "PPPPEPPPDP" "FPPPTOADPO" "EPFAEEP",
}

# Rows whose sheet content looks wrong. Shown with a small "check in sheet" note.
CHECK = {
    ("1.1", 72): "English and Italian don't match in the sheet.",
    ("1.2", 80): "The Italian cell holds the English sentence.",
    ("1.2", 81): "The Italian is the film sentence from the card above.",
}
MISSING = {("1.0", 76)}  # Italian cell holds unrelated text; hide it.


def main(path):
    rows = list(csv.reader(open(path, encoding="utf-8")))
    decks = []
    for name, off in [("1.0", 0), ("1.1", 6), ("1.2", 12)]:
        cards = []
        for r in rows[1:]:
            r = r + [""] * 20
            en, it, _pr, ex, no = [x.strip() for x in r[off:off + 5]]
            if not (en or it):
                continue
            n = len(cards) + 1
            if (name, n) in MISSING:
                it = ""
            c = {"n": n, "en": en, "it": it}
            if ex: c["ex"] = ex
            if no: c["no"] = no
            if (name, n) in CHECK: c["chk"] = CHECK[(name, n)]
            cards.append(c)
        tags = TAGS[name]
        assert len(tags) == len(cards), f"{name}: {len(tags)} tags for {len(cards)} cards"
        for c, t in zip(cards, tags):
            c["t"] = t
        decks.append({"id": name, "cards": cards})

    json.dump(decks, open(os.path.join(HERE, "cards.json"), "w"), ensure_ascii=False, indent=1)
    tpl = open(os.path.join(ROOT, "template.html"), encoding="utf-8").read()
    data = json.dumps(decks, ensure_ascii=False).replace("</", "<\\/")
    out = tpl.replace("/*__DATA__*/[]", data)
    open(os.path.join(ROOT, "friend-di-frase.html"), "w", encoding="utf-8").write(out)
    # Standalone copy with a full document head, for hosting outside claude.ai (e.g. GitHub Pages).
    head = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="apple-mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-title" content="Frasi">\n'
            '<style>:root{padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}'
            'body{margin:0}[hidden]{display:none!important}</style>\n</head>\n<body>\n')
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(head + out + "\n</body>\n</html>\n")
    print("built:", ", ".join(f"{d['id']}={len(d['cards'])}" for d in decks))


if __name__ == "__main__":
    main(sys.argv[1])
