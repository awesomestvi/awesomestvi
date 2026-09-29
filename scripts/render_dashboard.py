"""Render real GitHub activity into a looping GIF and still image (Pillow).
Optional PROFILE_FONT_REGULAR / PROFILE_FONT_BOLD override the portable fonts.
Motion decorates the data; values always come from data/profile.json.
"""
import json
import math
import os
from datetime import date
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT/'data/profile.json').read_text())
COLLECTION = DATA['contributionsCollection']
CAL = COLLECTION['contributionCalendar']
WEEKS = CAL['weeks']
DAYS = [day for week in WEEKS for day in week['contributionDays']]
ACTIVE = sum(day['contributionCount'] > 0 for day in DAYS)
STREAK = RUN = 0
for day in DAYS:
    RUN = RUN + 1 if day['contributionCount'] else 0
    STREAK = max(STREAK, RUN)
W, H = 1000, 620
CARD, LINE = '#151517', '#343436'
WHITE, MUTED, ORANGE, AMBER = '#fafafa', '#c4c4cc', '#f97316', '#ffbd7a'
PALETTE = ['#262b40', '#4d3026', '#8a4728', '#c5652b', ORANGE]


def font(size, bold=False, mono=False):
    paths = ([os.environ.get('PROFILE_FONT_BOLD' if bold else 'PROFILE_FONT_REGULAR'),
              str(ROOT/'assets/fonts/inter.ttf'), '/System/Library/Fonts/Avenir Next.ttc',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
             if not mono else ['/System/Library/Fonts/Menlo.ttc', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'])
    for path in paths:
        if path and Path(path).exists():
            loaded = ImageFont.truetype(path, size, index=(0 if bold else 7) if 'Avenir' in path else 0)
            if 'inter.ttf' in path:
                loaded.set_variation_by_axes([700 if bold else 400])
            return loaded
    return ImageFont.load_default(size=size)

FONTS = {(s, b, m): font(s,b,m) for s in [17,18,20,22,24,26,44] for b in [False,True] for m in [False,True]}


def level(count):
    return 0 if not count else min(4, 1+int(math.log2(count)))


def render(phase):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def txt(x, y, value, size=20, color=WHITE, bold=False):
        d.text((x, y), str(value), font=FONTS[size, bold, False], fill=color)

    def right(x, y, value, size=18, color=MUTED):
        width = d.textlength(str(value), font=FONTS[size, False, False])
        txt(x-width, y, value, size, color)

    def card(box):
        d.rounded_rectangle(box, 22, fill=CARD, outline=LINE, width=1)

    stats = [(COLLECTION['totalCommitContributions'], 'Commits', ORANGE),
             (COLLECTION['totalPullRequestContributions'], 'Pull requests', WHITE),
             (ACTIVE, 'Active days', WHITE),
             (STREAK, 'Longest streak', WHITE)]
    for j, (value, label, color) in enumerate(stats):
        x = j*254
        card((x, 0, x+237, 133))
        txt(x+20, 16, label, 22, bold=True)
        txt(x+20, 47, 'Past year', 18, MUTED)
        txt(x+20, 74, f'{value:,}'+(' days' if j == 3 else ''), 44, color, True)

    card((0, 150, W-1, 394))
    txt(22, 168, 'Contributions', 26, bold=True)
    right(976, 174, f"{CAL['totalContributions']:,} contributions · past year", color=ORANGE)
    gx, gy, step, size, row_step = 24, 238, 952/len(WEEKS), 13, 17
    last_month = None
    for wi, week in enumerate(WEEKS):
        first = date.fromisoformat(week['contributionDays'][0]['date'])
        if first.month != last_month and wi < len(WEEKS)-2 and not (wi == 0 and first.day > 21):
            txt(gx+wi*step, 210, first.strftime('%b'), 17, MUTED)
            last_month = first.month
        for day in week['contributionDays']:
            x, y = gx+wi*step, gy+day['weekday']*row_step
            d.rounded_rectangle((x, y, x+size, y+13), 3,
                                fill=PALETTE[level(day['contributionCount'])])

    trail = [(gx+wi*step+size/2, gy+row*row_step+6.5)
             for wi in range(max(0, len(WEEKS)-27), len(WEEKS))
             for row in (range(7) if wi%2 == 0 else range(6, -1, -1))
             if any(day['weekday'] == row for day in WEEKS[wi]['contributionDays'])]
    head = phase*(len(trail)-1)
    for offset in range(14, 0, -1):
        idx = head-offset
        if idx < 0:
            continue
        i = min(len(trail)-2, int(idx)); t = idx-i
        x = trail[i][0]*(1-t)+trail[i+1][0]*t
        y = trail[i][1]*(1-t)+trail[i+1][1]*t
        color = '#8a5334' if offset > 8 else '#e29b63' if offset > 3 else AMBER
        d.ellipse((x-2, y-2, x+2, y+2), fill=color)
    i = min(len(trail)-2, int(head)); t = head-i
    x = trail[i][0]*(1-t)+trail[i+1][0]*t
    y = trail[i][1]*(1-t)+trail[i+1][1]*t
    d.ellipse((x-4, y-4, x+4, y+4), fill=WHITE)
    txt(24, 363, f"{DAYS[0]['date']} — {DAYS[-1]['date']}", 17, MUTED)
    txt(778, 363, 'Less', 17, MUTED)
    for j, color in enumerate(PALETTE):
        d.rounded_rectangle((824+j*20, 366, 838+j*20, 380), 2, fill=color)
    txt(930, 363, 'More', 17, MUTED)

    card((0, 411, 579, H-1))
    txt(22, 429, 'Weekly activity', 26, bold=True)
    right(556, 435, 'Per week')
    vals = [sum(day['contributionCount'] for day in week['contributionDays']) for week in WEEKS]
    maximum = max(vals) or 1
    points = [(24+i*530/(len(vals)-1), 568-v/maximum*85) for i, v in enumerate(vals)]
    d.polygon(points+[(points[-1][0], 570), (24, 570)], fill='#3d2b26')
    d.line(points, fill=ORANGE, width=3)
    idx = phase*(len(points)-1)
    lo = min(len(points)-2, int(idx)); t = idx-lo
    x = points[lo][0]*(1-t)+points[lo+1][0]*t
    y = points[lo][1]*(1-t)+points[lo+1][1]*t
    d.ellipse((x-7, y-7, x+7, y+7), outline='#9c5b31', width=2)
    d.ellipse((x-3, y-3, x+3, y+3), fill=WHITE)
    txt(24, 587, f"Updated {DATA['updatedAt'][:10]}", 17, MUTED)

    card((596, 411, W-1, H-1))
    txt(618, 429, 'Languages', 26, bold=True)
    total = sum(lang['bytes'] for lang in DATA['languages']) or 1
    colors = [ORANGE, AMBER, '#f5ba7e']
    x = 620
    for j, lang in enumerate(DATA['languages']):
        width = 356*lang['bytes']/total
        d.rectangle((x, 479, x+width, 490), fill=colors[j] if j < 3 else '#48536c')
        x += width
    for j, lang in enumerate(DATA['languages'][:3]):
        y = 505+j*27
        d.ellipse((620, y+8, 627, y+15), fill=colors[j])
        txt(638, y, lang['name'], 20)
        right(976, y, f"{lang['bytes']/total:.0%}", 20)
    txt(620, 590, 'Public repos · excluding forks', 17, MUTED)
    return im


def gif_frame(frame, palette):
    # Reserve one palette entry for transparent space around the cards.
    indexed = frame.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE)
    indexed.paste(255, mask=frame.getchannel('A').point(lambda a: 255 if a == 0 else 0))
    indexed.info['transparency'] = 255
    return indexed


if __name__ == '__main__':
    still = render(.68)
    still.save(ROOT/'assets/dashboard.png', optimize=True)
    palette = still.convert('RGB').quantize(colors=192)
    frames = [gif_frame(render(i/80), palette) for i in range(80)]
    frames[0].save(ROOT/'assets/dashboard.gif', save_all=True,
                   append_images=frames[1:], duration=80, loop=0,
                   optimize=False, transparency=255, disposal=1)
    print(f"Rendered 80-frame activity dashboard: {(ROOT/'assets/dashboard.gif').stat().st_size:,} bytes")
