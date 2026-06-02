"""
情感分析工具模块
基于SnowNLP的中文情感分析
"""

import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """情感分析器"""

    def __init__(self):
        self._snownlp = None
        self._jieba = None
        self._stopwords = self._load_stopwords()

    @property
    def snownlp(self):
        if self._snownlp is None:
            try:
                from snownlp import SnowNLP
                self._snownlp = SnowNLP
            except ImportError:
                logger.warning("snownlp未安装，情感分析功能不可用")
        return self._snownlp

    @property
    def jieba(self):
        if self._jieba is None:
            try:
                import jieba
                self._jieba = jieba
            except ImportError:
                logger.warning("jieba未安装，分词功能不可用")
        return self._jieba

    def _load_stopwords(self) -> set:
        """加载停用词表"""
        return {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都',
            '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会',
            '着', '没有', '看', '好', '自己', '这', '他', '她', '它', '们',
            '那', '被', '从', '把', '让', '用', '为', '以', '但', '还',
            '与', '或', '及', '等', '个', '中', '对', '被', '之', '其',
            '这个', '那个', '什么', '怎么', '可以', '可能', '已经', '正在',
        }

    def analyze(self, text: str) -> Dict:
        """分析文本情感倾向"""
        if not text or not text.strip():
            return {'score': 0.5, 'label': 'neutral'}

        if not self.snownlp:
            return self._simple_analyze(text)

        try:
            # 文本预处理
            cleaned_text = self._preprocess(text)

            # 使用SnowNLP进行情感分析
            s = self.snownlp(cleaned_text)
            score = s.sentiments

            # 判断情感标签
            if score > 0.6:
                label = 'positive'
            elif score < 0.4:
                label = 'negative'
            else:
                label = 'neutral'

            return {
                'score': round(score, 4),
                'label': label
            }
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return {'score': 0.5, 'label': 'neutral'}

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """批量分析文本情感"""
        results = []
        for text in texts:
            results.append(self.analyze(text))
        return results

    def _preprocess(self, text: str) -> str:
        """文本预处理"""
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 去除URL
        text = re.sub(r'http[s]?://\S+', '', text)
        # 去除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _simple_analyze(self, text: str) -> Dict:
        """简单的情感分析（基于关键词）"""
        positive_words = {
            '增长', '上涨', '利好', '突破', '创新', '盈利', '增长', '提升',
            '看好', '推荐', '买入', '强势', '涨停', '大涨', '利润', '收益',
            '优秀', '领先', '龙头', '冠军', '第一', '最佳', '突破', '成功'
        }

        negative_words = {
            '下跌', '下跌', '利空', '亏损', '下滑', '减少', '下降', '风险',
            '减持', '卖出', '弱势', '跌停', '大跌', '亏损', '负债', '危机',
            '落后', '失败', '问题', '困难', '挑战', '担忧', '恐慌', '抛售'
        }

        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)

        total = pos_count + neg_count
        if total == 0:
            return {'score': 0.5, 'label': 'neutral'}

        score = pos_count / total
        if score > 0.6:
            label = 'positive'
        elif score < 0.4:
            label = 'negative'
        else:
            label = 'neutral'

        return {'score': round(score, 4), 'label': label}

    def extract_keywords(self, text: str, top_k: int = 10) -> List[tuple]:
        """提取关键词"""
        if not self.jieba:
            return []

        try:
            words = self.jieba.lcut(text)
            # 过滤停用词和短词
            words = [w for w in words if w not in self._stopwords and len(w) > 1]

            # 统计词频
            word_count = {}
            for word in words:
                word_count[word] = word_count.get(word, 0) + 1

            # 排序
            sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
            return sorted_words[:top_k]
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return []

    def get_sentiment_distribution(self, scores: List[float]) -> Dict:
        """获取情感分布统计"""
        positive = sum(1 for s in scores if s > 0.6)
        negative = sum(1 for s in scores if s < 0.4)
        neutral = len(scores) - positive - negative

        return {
            'total': len(scores),
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'positive_ratio': round(positive / len(scores) * 100, 2) if scores else 0,
            'negative_ratio': round(negative / len(scores) * 100, 2) if scores else 0,
            'neutral_ratio': round(neutral / len(scores) * 100, 2) if scores else 0,
            'average_score': round(sum(scores) / len(scores), 4) if scores else 0
        }
