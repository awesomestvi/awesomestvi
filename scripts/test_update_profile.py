import unittest

from update_profile import parse_public_calendar


def calendar_html(total=3, second_label='3 contributions on September 29th.'):
    # GitHub emits calendar cells by weekday; tooltips refer to the cells by ID.
    return f'''<h2 id="js-contribution-activity-description">
      {total} contributions in the last year
    </h2>
    <td id="monday" data-date="2026-09-29"></td>
    <td id="sunday" data-date="2026-09-28"></td>
    <tool-tip for="sunday">No contributions on September 28th.</tool-tip>
    <tool-tip for="monday">{second_label}</tool-tip>'''


class PublicCalendarTests(unittest.TestCase):
    def test_preserves_profile_counts_and_sorts_dates(self):
        result = parse_public_calendar(calendar_html())
        self.assertEqual(result['totalContributions'], 3)
        self.assertEqual(result['weeks'], [{'contributionDays': [
            {'date': '2026-09-28', 'contributionCount': 0, 'weekday': 1},
            {'date': '2026-09-29', 'contributionCount': 3, 'weekday': 2},
        ]}])

    def test_rejects_changed_or_missing_daily_labels(self):
        with self.assertRaisesRegex(ValueError, 'missing the count'):
            parse_public_calendar(calendar_html(second_label=''))

    def test_rejects_inconsistent_total(self):
        with self.assertRaisesRegex(ValueError, 'do not match'):
            parse_public_calendar(calendar_html(total=4))


if __name__ == '__main__':
    unittest.main()
