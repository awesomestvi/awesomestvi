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
W, H = 1200, 840
BG, CARD, LINE = '#0a0a0a', '#151517', '#343436'
WHITE, MUTED, ORANGE, AMBER = '#fafafa', '#a1a1aa', '#f97316', '#ffbd7a'
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

FONTS = {(s, b, m): font(s,b,m) for s in [11,12,13,14,15,16,18,20,22,26,32,42,50,62] for b in [False,True] for m in [False,True]}


def level(count):
    return 0 if not count else min(4, 1+int(math.log2(count)))


def render(phase):
    im = Image.new('RGB', (W,H), BG)
    d = ImageDraw.Draw(im)
    def txt(x,y,value,size=14,color=WHITE,bold=False,mono=False):
        d.text((x,y), str(value), font=FONTS[size,bold,mono], fill=color)
    def card(box):
        d.rounded_rectangle(box,28,fill=CARD,outline=LINE,width=1)
    txt(34,22,'@awesomestvi',13,MUTED)
    txt(32,46,'Vishal Chauhan',32,bold=True)
    txt(34,91,'Frontend developer & UI/UX designer',14,MUTED)
    txt(964,31,'GitHub activity',13,MUTED)
    stats=[(COLLECTION['totalCommitContributions'],'Commits',ORANGE),
           (COLLECTION['totalPullRequestContributions'],'Pull requests',WHITE),
           (ACTIVE,'Active days',WHITE),
           (STREAK,'Longest streak',WHITE)]
    for j,(value,label,col) in enumerate(stats):
        x=30+j*291
        card((x,226,x+276,348))
        txt(x+20,240,label,14,WHITE,True)
        txt(x+20,262,'Past year',12,MUTED)
        txt(x+20,289,f'{value:,}'+(' days' if j==3 else ''),32,col,True)
    card((30,364,1170,604))
    txt(54,384,'Contributions',20,bold=True)
    txt(849,389,f"{CAL['totalContributions']:,} contributions / past year",13,ORANGE)
    gx, gy, step, size = 58, 448, 20.3, 15
    last_month=None
    # Same week/day placement as GitHub. Future cells are left empty.
    for wi,week in enumerate(WEEKS):
        first=date.fromisoformat(week['contributionDays'][0]['date'])
        if first.month != last_month and wi < len(WEEKS)-2 and not (wi == 0 and first.day > 21):
            txt(gx+wi*step,420,first.strftime('%b'),11,MUTED)
            last_month=first.month
        for day in week['contributionDays']:
            x,y=gx+wi*step,gy+day['weekday']*17
            count=day['contributionCount']
            d.rounded_rectangle((x,y,x+size,y+13),3,fill=PALETTE[level(count)])
    # A lilac comet snakes through the recent six months of the actual grid.
    trail = [(gx+wi*step+size/2, gy+row*17+6.5)
             for wi in range(max(0,len(WEEKS)-27),len(WEEKS))
             for row in (range(7) if wi%2 == 0 else range(6,-1,-1))
             if any(day['weekday']==row for day in WEEKS[wi]['contributionDays'])]
    head = phase*(len(trail)-1)
    for offset in range(14,0,-1):
        idx=head-offset
        if idx<0:
            continue
        i=min(len(trail)-2,int(idx)); t=idx-i
        x=trail[i][0]*(1-t)+trail[i+1][0]*t
        y=trail[i][1]*(1-t)+trail[i+1][1]*t
        col='#8a5334' if offset>8 else '#e29b63' if offset>3 else AMBER
        d.ellipse((x-2,y-2,x+2,y+2),fill=col)
    i=min(len(trail)-2,int(head)); t=head-i
    x=trail[i][0]*(1-t)+trail[i+1][0]*t
    y=trail[i][1]*(1-t)+trail[i+1][1]*t
    d.ellipse((x-4,y-4,x+4,y+4),fill=WHITE)
    txt(55,574, f"{DAYS[0]['date']}  —  {DAYS[-1]['date']}",11,MUTED,mono=True)
    txt(991,575,'LESS',11,MUTED,mono=True)
    for j,col in enumerate(PALETTE):
        d.rounded_rectangle((1032+j*18,576,1044+j*18,587),2,fill=col)
    txt(1129,575,'+',11,MUTED,mono=True)
    card((30,620,730,785))
    txt(54,638,'Weekly activity',18,bold=True)
    txt(548,641,'Per week',11,MUTED,mono=True)
    vals=[sum(day['contributionCount'] for day in week['contributionDays']) for week in WEEKS]
    maximum=max(vals) or 1
    points=[(56+i*12.4,750-v/maximum*66) for i,v in enumerate(vals)]
    d.polygon(points+[(points[-1][0],752),(56,752)],fill='#3d2b26')
    d.line(points, fill=ORANGE,width=2)
    idx=phase*(len(points)-1)
    lo=min(len(points)-2,int(idx)); t=idx-lo
    x=points[lo][0]*(1-t)+points[lo+1][0]*t; y=points[lo][1]*(1-t)+points[lo+1][1]*t
    d.ellipse((x-7,y-7,x+7,y+7),outline='#9c5b31',width=2)
    d.ellipse((x-3,y-3,x+3,y+3),fill=WHITE)
    txt(54,763,'Each point shows one week’s contribution total.',11,MUTED)
    card((746,620,1170,785))
    txt(770,638,'Languages',18,bold=True)
    langs=DATA['languages'][:3]
    total=sum(lang['bytes'] for lang in DATA['languages']) or 1
    cols=[ORANGE,AMBER,'#f5ba7e']
    x=770
    for j,lang in enumerate(DATA['languages']):
        width=376*lang['bytes']/total
        d.rectangle((x,682,x+width,691),fill=cols[j] if j<3 else '#48536c');x+=width
    for j,lang in enumerate(langs):
        y=703+j*21
        d.ellipse((771,y+5,777,y+11), fill=cols[j])
        txt(787,y,lang['name'],12)
        txt(1098,y,f"{lang['bytes']/total:.0%}",12,MUTED,mono=True)
    txt(770,766,'Public repository bytes · excluding forks',11,MUTED)
    txt(33,809,f"{DATA['repositories']['totalCount']} public repos  /  {DATA['stars']} stars  /  {DATA['followers']['totalCount']} followers",12,MUTED,mono=True)
    txt(714,810,f"GITHUB SNAPSHOT {DATA['updatedAt'][:10]}  ·  BUILDING NAVET",11,MUTED,mono=True)
    compact=Image.new('RGB',(W,H-96),BG)
    compact.paste(im.crop((0,0,W,126)),(0,0))
    compact.paste(im.crop((0,222,W,H)),(0,126))
    return compact


if __name__=='__main__':
    still=render(.68)
    still.save(ROOT/'assets/dashboard.png', optimize=True)
    palette=still.quantize(colors=192)
    frames=[render(i/80).quantize(palette=palette,dither=Image.Dither.NONE) for i in range(80)]
    frames[0].save(ROOT/'assets/dashboard.gif',save_all=True,append_images=frames[1:],duration=80,loop=0,optimize=True,disposal=1)
    print(f"Rendered 80-frame activity dashboard: {(ROOT/'assets/dashboard.gif').stat().st_size:,} bytes")
