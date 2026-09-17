import unittest
from twin.feeds import parse_feed
from twin.rank import score_story
from twin.config import load_profile
from twin.digest import _is_research_source

RSS=b'''<?xml version="1.0"?><rss version="2.0"><channel><item><title>Anthropic launches new AI hardware research initiative</title><link>https://example.com/a</link><description>Researchers explore semiconductor accelerators and machine learning.</description><pubDate>Fri, 14 Aug 2026 12:00:00 GMT</pubDate></item></channel></rss>'''

class SmokeTest(unittest.TestCase):
    def test_feed_and_rank(self):
        items=parse_feed(RSS,"Fixture")
        self.assertEqual(len(items),1)
        score,detail,topics,entities,why=score_story(items[0],load_profile())
        self.assertGreater(score,50)
        self.assertIn("artificial_intelligence",topics)
        self.assertIn("Anthropic",entities)
        self.assertTrue(why)

    def test_research_sources_have_a_dedicated_lane(self):
        self.assertTrue(_is_research_source({'source':'arXiv AI'}))
        self.assertTrue(_is_research_source({'source':'Nature'}))
        self.assertFalse(_is_research_source({'source':'Bloomberg'}))

if __name__ == "__main__": unittest.main()
