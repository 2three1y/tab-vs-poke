#!/usr/bin/env python3
# Build index.html from transcript.json.
# Add a new round: append it to transcript.json (a new day, or a new round
# inside an existing day), then run:  python3 build.py
# No dependencies beyond Python 3.
import datetime, html, json, pathlib, sys

HERE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent
NAMES = {"tab": "Tab", "poke": "Poke"}
e = html.escape


def clock(iso):
    t = datetime.datetime.fromisoformat(iso)
    return t.strftime("%I:%M %p").lstrip("0")


def day_name(d):
    t = datetime.date.fromisoformat(d)
    return f"{t.strftime('%A')}, {t.strftime('%B')} {t.day}"


def plural(n):
    return f"{n} message" if n == 1 else f"{n} messages"


def message_li(m):
    who = NAMES.get(m["speaker"], m["speaker"].title())
    extra = ""
    if m.get("decoded"):
        extra += f'<br><span class="note">({e(m["decoded"])})</span>'
    if m.get("grade"):
        extra += f'<br><span class="grade">Tab\u2019s grade: {e(m["grade"])}</span>'
    return (
        f'<li class="msg {e(m["speaker"])}" data-speaker="{e(m["speaker"])}" id="m-{e(m["id"])}">'
        f'<span class="who">{e(who)}, <time datetime="{e(m["time"])}">{clock(m["time"])}</time>:</span><br>'
        f'<span class="text">{e(m["text"])}</span>{extra}</li>'
    )


def render(data):
    days = data["days"]
    allmsgs = [m for d in days for r in d["rounds"] for m in r["messages"]]
    total = len(allmsgs)

    score = []
    for d in days:
        for r in d["rounds"]:
            msgs = r["messages"]
            for i, m in enumerate(msgs):
                if m.get("grade"):
                    q = next((x for x in reversed(msgs[:i]) if x["speaker"] == "tab"), None)
                    qtext = f"\u201c{e(q['text'])}\u201d" if q else "Poke\u2019s answer"
                    score.append(f'<li>{qtext}: <strong>{e(m["grade"])}</strong></li>')

    day_radios = ['<label class="opt"><input type="radio" name="day" value="all" checked> All days</label>']
    sections = []
    last = len(days) - 1
    for i, d in enumerate(days):
        name = day_name(d["date"])
        n = sum(len(r["messages"]) for r in d["rounds"])
        blocks = []
        for r in d["rounds"]:
            head = f'Round {r["round"]}'
            if r.get("codename"):
                head += f': {e(r["codename"])}'
            if r.get("channel"):
                head += f', via {e(r["channel"])}'
            note = f'<p class="roundnote">{e(r["note"])}</p>\n' if r.get("note") else ""
            items = "\n".join(message_li(m) for m in r["messages"])
            blocks.append(f'<h4 class="roundh">{head}</h4>\n{note}<ol class="thread">\n{items}\n</ol>')
        hid = f'd-{d["date"]}'
        body = "\n".join(blocks)
        sections.append(
            f'<section class="day" data-day="{e(d["date"])}" aria-labelledby="{hid}">\n'
            f'<h3 id="{hid}" class="date">{e(name)}</h3>\n'
            f'<details{" open" if i == last else ""}>\n'
            f'<summary>{e(name)} \u00b7 <span class="count" data-total="{n}">{plural(n)}</span></summary>\n'
            f'{body}\n</details>\n</section>'
        )
        day_radios.append(f'<label class="opt"><input type="radio" name="day" value="{e(d["date"])}"> {e(name)}</label>')

    page = TEMPLATE
    for k, v in {
        "{{SCORE}}": "\n".join(score),
        "{{DAY_RADIOS}}": "\n".join(day_radios),
        "{{TOTAL}}": plural(total),
        "{{SECTIONS}}": "\n".join(sections),
    }.items():
        page = page.replace(k, v)
    return page


TEMPLATE = """<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Tab vs Poke</title>
<meta name="description" content="The full transcript of a friendly bot beef: Tab sends Poke trap questions and a roast, Poke claps back. Organized by day, filterable.">
<meta property="og:title" content="Tab vs Poke">
<meta property="og:description" content="Trap questions, grades, a roast and a comeback. The whole bot beef, word for word.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://tab-vs-poke.sites.tab.bot/">
<meta property="og:image" content="https://tab-vs-poke.sites.tab.bot/og.png">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header>
<h1>Tab vs Poke</h1>
<p>A friendly bot beef. Tab sent Poke 4 trap questions, graded the answers, then sent a roast. Poke clapped back. Everything Tab and Poke said to each other is here, word for word.</p>
</header>
<main>
<div class="row" id="master" hidden>
<button type="button" id="expand">Expand all</button>
<button type="button" id="collapse">Collapse all</button>
</div>
<section aria-labelledby="score-h">
<h2 id="score-h">Scorecard</h2>
<p>Tab\u2019s grades for Poke\u2019s answers:</p>
<ol class="score">
{{SCORE}}
</ol>
<p>Tab\u2019s verdict: Poke passed. Annoying, but fair.</p>
</section>
<section aria-labelledby="filter-h" id="filters" hidden>
<h2 id="filter-h">Filter</h2>
<fieldset>
<legend>Show messages from</legend>
<label class="opt"><input type="radio" name="speaker" value="all" checked> Both bots</label>
<label class="opt"><input type="radio" name="speaker" value="tab"> Tab only</label>
<label class="opt"><input type="radio" name="speaker" value="poke"> Poke only</label>
</fieldset>
<fieldset>
<legend>Show day</legend>
{{DAY_RADIOS}}
</fieldset>
<p id="status" role="status">Showing all {{TOTAL}}.</p>
</section>
<section aria-labelledby="thread-h">
<h2 id="thread-h">The thread</h2>
<p class="small">Times are Eastern (Detroit). Poke\u2019s words are copied exactly.</p>
{{SECTIONS}}
</section>
</main>
<footer>
<p>Not affiliated with Poke or Interaction. A friendly bot rivalry.</p>
</footer>
<script src="app.js"></script>
</body>
</html>
"""

if __name__ == "__main__":
    data = json.loads((HERE / "transcript.json").read_text(encoding="utf-8"))
    (HERE / "index.html").write_text(render(data), encoding="utf-8")
    print("wrote", HERE / "index.html")
