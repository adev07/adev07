"""Render animated SVG cards for the profile README from live GitHub data.

Run: GITHUB_TOKEN=... python scripts/render_cards.py   (writes ./cards/*.svg)
"""
import json, os, urllib.request
from collections import defaultdict
from datetime import date, datetime, timezone
from html import escape

LOGIN = "adev07"
NAME = "Aditya Anand"
ROLE = "Full-stack developer · Bangalore"
TAGLINE = "I build fast, friendly web apps: clean frontends, solid backends."
STACK = ["React", "Next.js", "TypeScript", "Node.js", "MongoDB", "Tailwind"]

BG, PANEL, LINE = "#0b1020", "#111933", "#1e2a4a"
TEXT, MUTED = "#e6edf7", "#8b9bb8"
BRAND, VIOLET, AMBER = "#61dafb", "#a78bfa", "#fbbf24"
SANS = "ui-sans-serif,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

# Each card is its own <img>, so stagger start times to play top to bottom.
T_HERO, T_TILES, T_ACTIVITY, T_REPOS, T_HEAT = 0.0, 0.6, 1.2, 1.8, 2.2

QUERY = """query($login:String!){user(login:$login){
 publicRepos: repositories(privacy:PUBLIC){totalCount}
 contributionsCollection{contributionCalendar{totalContributions
   weeks{contributionDays{date contributionCount}}}}
 repositories(first:5,ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,
   orderBy:{field:PUSHED_AT,direction:DESC}){nodes{
   name description url pushedAt primaryLanguage{name color}}}}}"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"},
    )
    body = json.load(urllib.request.urlopen(req))
    if "errors" in body:
        raise SystemExit(body["errors"])
    return body["data"]["user"]


def streaks(days):
    """days: list of (date, count) ascending. Returns (current, longest)."""
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur = 0
    # Today may not have activity yet; don't break the streak for it.
    tail = days[:-1] if days and days[-1][1] == 0 else days
    for _, c in reversed(tail):
        if not c:
            break
        cur += 1
    return cur, longest


STYLE = f"""<style>
text{{font-family:{SANS};fill:{TEXT}}}
.mono{{font-family:{MONO}}} .muted{{fill:{MUTED}}}
.fade{{animation:fade .6s ease-out both}}
.rise{{transform-box:fill-box;transform-origin:center;animation:rise .9s cubic-bezier(.2,.9,.3,1.3) both}}
.grow{{transform-box:fill-box;transform-origin:bottom;animation:grow .8s cubic-bezier(.2,.8,.2,1) both}}
.pop{{transform-box:fill-box;transform-origin:center;animation:pop .35s ease-out both}}
.pulse{{transform-box:fill-box;transform-origin:center;animation:pulse 2.6s ease-out infinite}}
.shine{{animation:shine 5s ease-in-out infinite}}
@keyframes fade{{from{{opacity:0;transform:translateY(6px)}}}}
@keyframes rise{{0%{{opacity:0;transform:translateY(28px) rotate(-4deg)}}70%{{transform:translateY(-4px) rotate(1deg)}}}}
@keyframes grow{{from{{transform:scaleY(0)}}}}
@keyframes pop{{0%{{transform:scale(0);opacity:0}}70%{{transform:scale(1.3)}}}}
@keyframes pulse{{from{{transform:scale(.6);opacity:.9}}to{{transform:scale(1.8);opacity:0}}}}
@keyframes shine{{0%,60%{{transform:translateX(-400px)}}100%{{transform:translateX(400px)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}">{STYLE}'
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="14" fill="{BG}" stroke="{LINE}"/>{body}</svg>')


def d(t):
    return f'style="animation-delay:{t:.2f}s"'


def hero():
    chips, x = [], 40
    for i, s in enumerate(STACK):
        w = 22 + 7.6 * len(s)
        chips.append(f'<g class="fade" {d(T_HERO + 1.0 + i * .08)}><rect x="{x}" y="176" width="{w:.0f}" height="26" rx="13" '
                     f'fill="{PANEL}" stroke="{LINE}"/><text x="{x + w/2:.0f}" y="193.5" font-size="12.5" text-anchor="middle" class="mono">{escape(s)}</text></g>')
        x += w + 8
    initials = "".join(p[0] for p in NAME.split())
    body = f"""<defs><linearGradient id="g" x1="0" x2="1" spreadMethod="reflect">
<stop offset="0" stop-color="{BRAND}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{BRAND}"/>
<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="2 0" dur="6s" repeatCount="indefinite"/></linearGradient></defs>
<text x="40" y="58" font-size="14" class="mono muted fade" {d(T_HERO)}>hi, i'm</text>
<text x="38" y="112" font-size="56" font-weight="800" fill="url(#g)" style="fill:url(#g);animation-delay:{T_HERO + .15}s" class="fade">{escape(NAME)}</text>
<text x="40" y="142" font-size="17" class="fade" {d(T_HERO + .45)}>{escape(ROLE)}</text>
<text x="40" y="164" font-size="14" class="muted fade" {d(T_HERO + .7)}>{escape(TAGLINE)}</text>
{''.join(chips)}
<g transform="translate(790 110)">
<circle r="46" fill="none" stroke="{BRAND}" stroke-width="2" class="pulse"/>
<circle r="46" fill="none" stroke="{VIOLET}" stroke-width="2" class="pulse" style="animation-delay:1.3s"/>
<circle r="44" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>
<text y="11" font-size="30" font-weight="800" text-anchor="middle" fill="url(#g)" style="fill:url(#g)">{initials}</text></g>"""
    return svg(900, 225, body, f"{NAME}, {ROLE}")


def count_up(x, y, value, t0, size=44, color=TEXT, frames=18, dur=.9):
    """CSS can't change text, so swap through SMIL <set> frames, then show the final value."""
    out = []
    for i in range(frames):
        v = round(value * (1 - (1 - i / frames) ** 3))
        b, e = t0 + dur * i / frames, t0 + dur * (i + 1) / frames
        out.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="800" fill="{color}" style="fill:{color}" visibility="hidden">'
                   f'{v:,}<set attributeName="visibility" to="visible" begin="{b:.3f}s" end="{e:.3f}s"/></text>')
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="800" fill="{color}" style="fill:{color}">{value:,}'
               f'<set attributeName="visibility" to="hidden" begin="0s" end="{t0 + dur:.3f}s"/></text>')
    return "".join(out)


def tile(i, label, value, caption, color):
    t = T_TILES + i * .15
    body = f"""<defs><linearGradient id="s" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>
<stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<g class="rise" {d(t)}>
<text x="28" y="44" font-size="13" class="mono muted">{escape(label)}</text>
{count_up(26, 104, value, t + .3, color=color)}
<text x="28" y="138" font-size="13" class="muted">{escape(caption)}</text>
<circle cx="262" cy="40" r="7" fill="{color}"/><circle cx="262" cy="40" r="7" fill="none" stroke="{color}" class="pulse" style="animation-delay:{t + i * .4:.2f}s"/>
</g><rect width="160" height="170" fill="url(#s)" class="shine" style="animation-delay:{3 + i}s"/>"""
    return svg(300, 170, body, f"{label}: {value} {caption}")


def activity(days):
    by_month = defaultdict(int)
    for dt, c in days:
        by_month[dt.strftime("%Y-%m")] += c
    months = sorted(by_month)[-12:]
    vals = [by_month[m] for m in months]
    top = max(vals) or 1
    best = vals.index(max(vals))
    active = sum(1 for _, c in days if c)
    busiest = max(days, key=lambda x: x[1])
    x0, base, h, step = 40, 220, 140, 47
    bars = []
    for i, (m, v) in enumerate(zip(months, vals)):
        bh = max(3, v / top * h)
        x = x0 + i * step
        col = AMBER if i == best else BRAND
        bars.append(f'<rect x="{x}" y="{base - bh:.1f}" width="30" height="{bh:.1f}" rx="5" fill="{col}" '
                    f'fill-opacity="{1 if i == best else .75}" class="grow" {d(T_ACTIVITY + .2 + i * .06)}/>'
                    f'<text x="{x + 15}" y="{base + 20}" font-size="11" text-anchor="middle" class="mono muted">'
                    f'{datetime.strptime(m, "%Y-%m").strftime("%b")}</text>')
    bx = x0 + best * step + 15
    bars.append(f'<text x="{bx}" y="{base - vals[best] / top * h - 10:.1f}" font-size="13" font-weight="700" '
                f'text-anchor="middle" class="fade" style="fill:{AMBER};animation-delay:{T_ACTIVITY + 1.2:.2f}s">{vals[best]}</text>')
    stats = [("active days", f"{active}"), ("busiest day", f"{busiest[1]} on {busiest[0]:%b %-d}"),
             ("best month", datetime.strptime(months[best], "%Y-%m").strftime("%B %Y"))]
    side = "".join(f'<g class="fade" {d(T_ACTIVITY + .5 + i * .15)}><text x="640" y="{92 + i * 56}" font-size="12" class="mono muted">{k}</text>'
                   f'<text x="640" y="{116 + i * 56}" font-size="20" font-weight="700">{escape(v)}</text></g>'
                   for i, (k, v) in enumerate(stats))
    body = f"""<text x="40" y="44" font-size="18" font-weight="700" class="fade" {d(T_ACTIVITY)}>Contributions · last 12 months</text>
<line x1="{x0 - 6}" x2="{x0 + 12 * step - 10}" y1="{base}" y2="{base}" stroke="{LINE}"/>
<line x1="616" x2="616" y1="70" y2="232" stroke="{LINE}"/>{''.join(bars)}{side}"""
    return svg(900, 260, body, f"{sum(vals)} contributions in the last 12 months")


def repo_card(i, r):
    lang = r["primaryLanguage"] or {"name": "Code", "color": MUTED}
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(r["pushedAt"].replace("Z", "+00:00"))).days
    when = "today" if age == 0 else f"{age} day{'s' * (age != 1)} ago" if age < 60 else f"{age // 30} months ago"
    desc = r["description"] or f"{lang['name']} project"
    if len(desc) > 58:
        desc = desc[:55] + "…"
    t = T_REPOS + i * .12
    body = f"""<g class="rise" {d(t)}>
<text x="24" y="40" font-size="12" class="mono muted">{LOGIN} /</text>
<text x="24" y="66" font-size="21" font-weight="700">{escape(r['name'])}</text>
<text x="24" y="92" font-size="13" class="muted">{escape(desc)}</text>
<circle cx="30" cy="114" r="6" fill="{lang['color'] or MUTED}"/>
<text x="42" y="118.5" font-size="12.5" class="mono">{escape(lang['name'])}</text>
<text x="420" y="118.5" font-size="12" text-anchor="end" class="mono muted">updated {when}</text>
<path d="M404 46 l10 -10 m-8 0 h8 v8" stroke="{BRAND}" stroke-width="2" fill="none" class="fade" {d(t + .5)}/></g>"""
    return svg(445, 140, body, f"Repository {r['name']}")


def heatmap(weeks, total):
    counts = sorted(c["contributionCount"] for w in weeks for c in w["contributionDays"] if c["contributionCount"])
    cuts = [counts[int(len(counts) * q)] for q in (.25, .5, .75)] if counts else [1, 2, 3]
    shades = ["#16203a", "#0e4a5c", "#1a7f99", "#3fb6d6", BRAND]
    cells = []
    for wx, w in enumerate(weeks):
        for c in w["contributionDays"]:
            n = c["contributionCount"]
            lvl = 0 if not n else 1 + sum(n > k for k in cuts)
            dy = date.fromisoformat(c["date"]).isoweekday() % 7
            cls = f' class="pop" {d(T_HEAT + .3 + wx * .018)}' if n else ""
            cells.append(f'<rect x="{30 + wx * 16}" y="{60 + dy * 16}" width="12" height="12" rx="3" fill="{shades[lvl]}"{cls}/>')
    legend = "".join(f'<rect x="{760 + i * 16}" y="34" width="12" height="12" rx="3" fill="{s}"/>' for i, s in enumerate(shades))
    body = f"""<text x="30" y="44" font-size="18" font-weight="700" class="fade" {d(T_HEAT)}>{total:,} contributions in the last year</text>
<text x="752" y="44" font-size="11" text-anchor="end" class="mono muted">less</text>{legend}
<text x="844" y="44" font-size="11" class="mono muted">more</text>{''.join(cells)}"""
    return svg(900, 190, body, f"Contribution graph, {total} contributions in the last year")


def main():
    u = fetch()
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [(date.fromisoformat(c["date"]), c["contributionCount"]) for w in cal["weeks"] for c in w["contributionDays"]]
    cur, longest = streaks(days)
    cards = {
        "hero": hero(),
        "tile-contributions": tile(0, "contributions", cal["totalContributions"], "in the last year", BRAND),
        "tile-streak": tile(1, "longest streak", longest, f"days · current {cur}", AMBER),
        "tile-repos": tile(2, "public repos", u["publicRepos"]["totalCount"], "and counting", VIOLET),
        "activity": activity(days),
        "heatmap": heatmap(cal["weeks"], cal["totalContributions"]),
    }
    repos = [r for r in u["repositories"]["nodes"] if r["name"] != LOGIN][:4]
    for i, r in enumerate(repos):
        cards[f"repo-{i + 1}"] = repo_card(i, r)
    os.makedirs("cards", exist_ok=True)
    for name, s in cards.items():
        with open(f"cards/{name}.svg", "w") as f:
            f.write(s)
    print("wrote", ", ".join(cards))


if __name__ == "__main__":
    # ponytail: tiny self-check for the only branchy logic
    t = date.today()
    assert streaks([(t, 1), (t, 1), (t, 0), (t, 2), (t, 3), (t, 0)]) == (2, 2)
    assert streaks([(t, 1), (t, 1), (t, 1)]) == (3, 3)
    main()
