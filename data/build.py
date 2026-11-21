"""Build the Friend di Frasi companion page from the Anki sheet CSV exports.

Usage: python3 -I data/build.py [CSV ...]   (default: every CSV in data/sheets/)
Each CSV holds three decks side by side; deck names come from the "English x.y" headers.
Writes data/cards.json, friend-di-frase.html (claude.ai) and index.html (GitHub Pages).
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
    "1.3": "DFOAFDOTAO" "DPDDTODDFD" "PTOFODOOOF" "FDPPFPPTDD" "DOTPPFFDAP"
           "EPPFDTAODD" "PTOADDAOPP" "DPDDDFEEOA" "AAFFTTTTFF",
    "1.4": "FOODFADOPO" "TDDFEPPPFP" "OAAATTOETP" "EPPAAEEEAA" "DTOEAFAPTT"
           "OAPTAADDPD" "FEDFFFFDDD" "DPDDOOODDT" "FDDDFDDTDD",
    "1.5": "FTODDPODFP" "DTOETOFAOD" "FAFAODEDPP" "OTFTOFPOOE" "DOPDTEFFPD"
           "FAODEOOPAF" "TT",
}

# Corrections layered over the sheet (data/fixes.json). Once a fix is also made in the
# sheet, its entry is harmless; delete it whenever convenient.
FIXES = json.load(open(os.path.join(HERE, "fixes.json"), encoding="utf-8"))
FIXES.pop("_about", None)


def deck_columns(path):
    """Yield (deck name, column offset, rows) for each 'English x.y' block in a CSV."""
    rows = list(csv.reader(open(path, encoding="utf-8")))
    for off, h in enumerate(rows[0]):
        if h.strip().startswith("English "):
            yield h.strip().split()[-1], off, rows


def main(paths):
    blocks = sorted((b for p in paths for b in deck_columns(p)), key=lambda b: [int(x) for x in b[0].split(".")])
    decks, used, log = [], set(), []
    for name, off, rows in blocks:
        ex_label = "Alt" if rows[0][off + 3].strip().startswith("Bonus") and name >= "1.3" else "E.g."
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
        decks.append({"id": name, "exLabel": ex_label, "cards": cards})

    json.dump(decks, open(os.path.join(HERE, "cards.json"), "w"), ensure_ascii=False, indent=1)
    tpl = open(os.path.join(ROOT, "template.html"), encoding="utf-8").read()
    data = json.dumps(decks, ensure_ascii=False).replace("</", "<\\/")
    out = tpl.replace("/*__DATA__*/[]", data)
    open(os.path.join(ROOT, "friend-di-frase.html"), "w", encoding="utf-8").write(out)
    # Standalone copy with a full document head, for hosting outside claude.ai (e.g. GitHub Pages).
    head = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="description" content="My Italian Anki decks at a glance.">\n'
            '<link rel="manifest" href="manifest.webmanifest">\n'
            '<meta name="theme-color" content="#eef0f3" media="(prefers-color-scheme: light)">\n'
            '<meta name="theme-color" content="#0f131a" media="(prefers-color-scheme: dark)">\n'
            '<link rel="icon" type="image/png" href="icons/favicon-64.png">\n'
            '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">\n'
            '<meta name="mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-title" content="Frasi">\n'
            '<script>if ("serviceWorker" in navigator) addEventListener("load", () => '
            'navigator.serviceWorker.register("sw.js").catch(() => {}));</script>\n'
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
    for deck in sorted({x[0] for x in log}, key=lambda d: [int(v) for v in d.split(".")]):
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
    args = sys.argv[1:] or sorted(
        os.path.join(HERE, "sheets", f) for f in os.listdir(os.path.join(HERE, "sheets")) if f.endswith(".csv"))
    main(args)
