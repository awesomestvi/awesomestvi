"""Fetch GitHub-reported activity using gh's existing authentication.

In Actions, gh reads GH_TOKEN from the job environment. Never writes a token.
The snapshot contains counts, dates, and public repository language totals.
"""
import json
import re
import subprocess
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CALENDAR_URL = 'https://github.com/users/awesomestvi/contributions'
QUERY = '''query($cursor: String) {
  user(login: "awesomestvi") {
    login name createdAt followers { totalCount }
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, privacy: PUBLIC) {
      totalCount pageInfo { hasNextPage endCursor }
      nodes { stargazerCount isFork languages(first: 10) { edges { size node { name color } } } }
    }
    contributionsCollection {
      totalCommitContributions totalPullRequestContributions totalIssueContributions
      totalPullRequestReviewContributions
      contributionCalendar { totalContributions weeks {
        contributionDays { date contributionCount weekday }
      } }
    }
  }
}'''


def fetch(cursor=None):
    args = ['gh', 'api', 'graphql', '-f', 'query='+QUERY]
    if cursor:
        args.extend(['-f', 'cursor='+cursor])
    response = json.loads(subprocess.check_output(args, text=True))
    if response.get('errors'):
        raise RuntimeError('GitHub could not return the profile snapshot')
    return response['data']['user']


class PublicCalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.labels = {}
        self.label_target = None
        self.in_heading = False
        self.heading = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and 'data-date' in attrs:
            day = attrs['data-date']
            if day in self.cells:
                raise ValueError('Duplicate date in GitHub contribution calendar')
            self.cells[day] = attrs['id']
        elif tag == 'tool-tip':
            self.label_target = attrs.get('for')
        elif tag == 'h2' and attrs.get('id') == 'js-contribution-activity-description':
            self.in_heading = True

    def handle_data(self, text):
        if self.label_target:
            target = self.label_target
            self.labels[target] = self.labels.get(target, '') + text
        if self.in_heading:
            self.heading += text

    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.label_target = None
        elif tag == 'h2':
            self.in_heading = False


def parse_public_calendar(html):
    parser = PublicCalendarParser()
    parser.feed(html)
    heading = ' '.join(parser.heading.split())
    match = re.fullmatch(r'([\d,]+) contributions in the last year', heading)
    if not match or not parser.cells:
        raise ValueError('GitHub contribution calendar is missing its total or daily cells')
    total = int(match[1].replace(',', ''))
    weeks = {}
    previous = None
    for day, target in sorted(parser.cells.items()):
        current = date.fromisoformat(day)
        if previous and current != previous + timedelta(days=1):
            raise ValueError('GitHub contribution calendar has missing dates')
        previous = current
        label = parser.labels.get(target, '').strip()
        count_match = re.match(r'^(No|[\d,]+) contributions? on ', label)
        if not count_match:
            raise ValueError(f'GitHub contribution calendar is missing the count for {day}')
        count = 0 if count_match[1] == 'No' else int(count_match[1].replace(',', ''))
        weekday = (current.weekday() + 1) % 7
        week = current - timedelta(days=weekday)
        weeks.setdefault(week, []).append({'date': day, 'contributionCount': count, 'weekday': weekday})
    if sum(day['contributionCount'] for days in weeks.values() for day in days) != total:
        raise ValueError('GitHub contribution calendar daily counts do not match its total')
    return {'totalContributions': total,
            'weeks': [{'contributionDays': days} for days in weeks.values()]}


def fetch_public_calendar():
    html = subprocess.check_output(['curl', '--fail', '--silent', '--show-error',
                                    '--location', '--max-time', '30', CALENDAR_URL], text=True)
    return parse_public_calendar(html)


if __name__ == '__main__':
    user = fetch()
    repos = user['repositories']
    nodes = list(repos['nodes'])
    while repos['pageInfo']['hasNextPage']:
        repos = fetch(repos['pageInfo']['endCursor'])['repositories']
        nodes.extend(repos['nodes'])
    languages, colors = Counter(), {}
    for repo in nodes:
        if not repo['isFork']:
            for edge in repo['languages']['edges']:
                languages[edge['node']['name']] += edge['size']
                colors[edge['node']['name']] = edge['node']['color'] or '#bca6ff'
    user['repositories'] = {'totalCount': user['repositories']['totalCount']}
    user['stars'] = sum(repo['stargazerCount'] for repo in nodes if not repo['isFork'])
    user['languages'] = [{'name': name, 'bytes': size, 'color': colors[name]}
                         for name, size in languages.most_common()]
    user['updatedAt'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    # Use the same daily counts and total shown on the public profile, rather than
    # the API calendar, which can report a different contribution total.
    user['contributionsCollection']['contributionCalendar'] = fetch_public_calendar()
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data/profile.json').write_text(json.dumps(user, indent=2)+'\n')
    print(f"Updated @{user['login']}: {user['contributionsCollection']['contributionCalendar']['totalContributions']} contributions")
