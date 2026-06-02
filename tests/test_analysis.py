"""
分析模块测试
"""

from django.test import TestCase
from utils.sentiment_analyzer import SentimentAnalyzer
from utils.topic_extractor import TopicExtractor


class SentimentAnalyzerTest(TestCase):
    """情感分析器测试"""

    def setUp(self):
        self.analyzer = SentimentAnalyzer()

    def test_analyze_positive(self):
        """测试正面情感分析"""
        result = self.analyzer.analyze("公司业绩大幅增长，利润创新高")
        self.assertIn('score', result)
        self.assertIn('label', result)
        self.assertEqual(result['label'], 'positive')

    def test_analyze_negative(self):
        """测试负面情感分析"""
        result = self.analyzer.analyze("公司亏损严重，股价大跌")
        self.assertIn('score', result)
        self.assertIn('label', result)
        self.assertEqual(result['label'], 'negative')

    def test_analyze_neutral(self):
        """测试中性情感分析"""
        result = self.analyzer.analyze("今日召开股东大会")
        self.assertIn('score', result)
        self.assertIn('label', result)

    def test_analyze_empty(self):
        """测试空文本分析"""
        result = self.analyzer.analyze("")
        self.assertEqual(result['score'], 0.5)
        self.assertEqual(result['label'], 'neutral')

    def test_extract_keywords(self):
        """测试关键词提取"""
        keywords = self.analyzer.extract_keywords("光伏行业发展迅速，太阳能发电成为新能源重要组成部分")
        self.assertIsInstance(keywords, list)

    def test_batch_analyze(self):
        """测试批量分析"""
        texts = ["利好消息", "利空消息", "普通新闻"]
        results = self.analyzer.analyze_batch(texts)
        self.assertEqual(len(results), 3)


class TopicExtractorTest(TestCase):
    """主题提取器测试"""

    def setUp(self):
        self.extractor = TopicExtractor()

    def test_extract_topics(self):
        """测试主题提取"""
        texts = [
            "光伏行业发展迅速，太阳能发电技术不断进步",
            "新能源政策利好，光伏企业受益明显",
            "光伏组件价格下降，市场竞争加剧",
            "光伏装机量持续增长，行业前景看好",
            "光伏技术创新，转换效率提升",
        ]
        topics = self.extractor.extract_topics(texts, n_topics=2)
        self.assertIsInstance(topics, list)
        self.assertTrue(len(topics) > 0)

    def test_extract_hot_topics(self):
        """测试热门话题提取"""
        texts = ["光伏", "光伏", "新能源", "太阳能"]
        topics = self.extractor.extract_hot_topics(texts, top_k=3)
        self.assertIsInstance(topics, list)
