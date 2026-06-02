"""
主题分析工具模块
基于jieba分词和LDA主题模型
"""

import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TopicExtractor:
    """主题提取器"""

    def __init__(self):
        self._jieba = None
        self._stopwords = self._load_stopwords()

    @property
    def jieba(self):
        if self._jieba is None:
            try:
                import jieba
                self._jieba = jieba
            except ImportError:
                logger.warning("jieba未安装，主题分析功能不可用")
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
            '记者', '报道', '新闻', '消息', '据悉', '了解', '表示', '认为',
            '公司', '企业', '集团', '股份', '有限', '发展', '市场', '行业',
        }

    def extract_topics(self, texts: List[str], n_topics: int = 5,
                       n_words: int = 10) -> List[Dict]:
        """提取主题"""
        if len(texts) < 3:
            return self._extract_keywords_simple(texts, n_words)

        try:
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.decomposition import LatentDirichletAllocation

            # 文本预处理和分词
            processed_texts = []
            for text in texts:
                words = self._tokenize(text)
                if words:
                    processed_texts.append(' '.join(words))

            if len(processed_texts) < 3:
                return self._extract_keywords_simple(texts, n_words)

            # 构建词频矩阵
            vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=1000)
            tf = vectorizer.fit_transform(processed_texts)

            # LDA模型
            lda = LatentDirichletAllocation(
                n_components=min(n_topics, len(processed_texts)),
                random_state=42,
                max_iter=20
            )
            lda.fit(tf)

            # 提取主题词
            feature_names = vectorizer.get_feature_names_out()
            topics = []
            for topic_idx, topic in enumerate(lda.components_):
                top_word_indices = topic.argsort()[:-n_words - 1:-1]
                top_words = [feature_names[i] for i in top_word_indices]
                topics.append({
                    'topic_id': topic_idx,
                    'topic_name': f"主题{topic_idx + 1}",
                    'words': top_words,
                    'weight': round(float(topic.max()), 4)
                })

            return topics

        except ImportError:
            logger.warning("sklearn未安装，使用简单主题提取")
            return self._extract_keywords_simple(texts, n_words)
        except Exception as e:
            logger.error(f"主题提取失败: {e}")
            return self._extract_keywords_simple(texts, n_words)

    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        if not self.jieba:
            return []

        # 文本预处理
        text = re.sub(r'[^一-龥a-zA-Z0-9]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        words = self.jieba.lcut(text)
        # 过滤停用词和短词
        words = [w for w in words if w not in self._stopwords and len(w) > 1]
        return words

    def _extract_keywords_simple(self, texts: List[str], n_words: int = 10) -> List[Dict]:
        """简单的关键词提取（不使用LDA）"""
        word_count = {}

        for text in texts:
            words = self._tokenize(text)
            for word in words:
                word_count[word] = word_count.get(word, 0) + 1

        # 按词频排序
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

        # 分成几个主题组
        topics = []
        words_per_topic = max(1, len(sorted_words) // 5)

        for i in range(0, min(len(sorted_words), n_words * 5), words_per_topic):
            group = sorted_words[i:i + words_per_topic]
            if group:
                topics.append({
                    'topic_id': len(topics),
                    'topic_name': f"主题{len(topics) + 1}",
                    'words': [w for w, c in group],
                    'weight': round(group[0][1] / len(texts), 4) if group else 0
                })

        return topics[:5]  # 最多返回5个主题

    def extract_hot_topics(self, texts: List[str], top_k: int = 10) -> List[Dict]:
        """提取热门话题"""
        word_count = {}

        for text in texts:
            words = self._tokenize(text)
            for word in words:
                word_count[word] = word_count.get(word, 0) + 1

        # 按词频排序
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

        topics = []
        for word, count in sorted_words[:top_k]:
            topics.append({
                'topic_name': word,
                'count': count,
                'weight': round(count / len(texts), 4) if texts else 0
            })

        return topics

    def get_word_frequency(self, texts: List[str], top_k: int = 50) -> List[Dict]:
        """获取词频统计"""
        word_count = {}

        for text in texts:
            words = self._tokenize(text)
            for word in words:
                word_count[word] = word_count.get(word, 0) + 1

        # 按词频排序
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

        return [{'name': w, 'value': c} for w, c in sorted_words[:top_k]]
