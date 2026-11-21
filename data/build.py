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

# Corrections layered over the sheet (data/fixes.json). Once a fix is also made in the
# sheet, its entry is harmless; delete it whenever convenient.
FIXES = json.load(open(os.path.join(HERE, "fixes.json"), encoding="utf-8"))
FIXES.pop("_about", None)


def main(path):
    rows = list(csv.reader(open(path, encoding="utf-8")))
    decks, used, log = [], set(), []
    for name, off in [("1.0", 0), ("1.1", 6), ("1.2", 12)]:
        cards = []
        for r in rows[1:]:
            r = r + [""] * 20
            en, it, _pr, ex, no = [x.strip() for x in r[off:off + 5]]
            if not (en or it):
                continue
            n = len(cards) + 1
            fx = FIXES.get(f"{name}|{en}")
            if fx:
                used.add(f"{name}|{en}")
                old = {"en": en, "it": it, "ex": ex}
                en = fx["en"] if "en" in fx else en
                it = fx["it"] if "it" in fx else it
                ex = (fx["ex"] or "") if "ex" in fx else ex
                log.append((name, n, old, {"en": en, "it": it, "ex": ex}, fx.get("why", "")))
            c = {"n": n, "en": en, "it": it}
            if ex: c["ex"] = ex
            if no: c["no"] = no
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
    write_fix_list(log)
    for k in sorted(set(FIXES) - used):
        print("fix not applied (row changed or already fixed in sheet?):", k)
    print("built:", ", ".join(f"{d['id']}={len(d['cards'])}" for d in decks), f"| {len(log)} fixes applied")


def write_fix_list(log):
    """sheet-fixes.md: what to change in the Google Sheet / Anki so they match the app."""
    out = ["# Sheet fixes", "",
           "Corrections the app applies on top of the sheet. Copy them into the sheet (and Anki) to keep everything in sync.", ""]
    for deck in ("1.0", "1.1", "1.2"):
        rows = [x for x in log if x[0] == deck]
        if not rows:
            continue
        out += [f"## Deck {deck}", ""]
        for _, n, old, new, why in rows:
            out.append(f"**#{n} · {new['en']}** — {why}")
            for f, label in (("en", "English"), ("it", "Italian"), ("ex", "E.g.")):
                if old[f] != new[f]:
                    out.append(f"- {label}: ~~{old[f] or '(empty)'}~~ → {new[f] or '(remove)'}")
            out.append("")
    open(os.path.join(ROOT, "sheet-fixes.md"), "w", encoding="utf-8").write("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
