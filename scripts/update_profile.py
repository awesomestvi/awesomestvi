"""Fetch GitHub-reported activity using gh's existing authentication.

In Actions, gh reads GH_TOKEN from the job environment. Never writes a token.
The snapshot contains counts, dates, and public repository language totals.
"""
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data/profile.json').write_text(json.dumps(user, indent=2)+'\n')
    print(f"Updated @{user['login']}: {user['contributionsCollection']['contributionCalendar']['totalContributions']} contributions")
