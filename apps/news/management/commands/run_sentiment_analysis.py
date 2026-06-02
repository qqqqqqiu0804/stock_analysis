"""
对新闻数据运行情感分析
"""

import jieba
from django.core.management.base import BaseCommand
from apps.news.models import NewsData
from utils.sentiment_analyzer import SentimentAnalyzer


class Command(BaseCommand):
    help = '对未分析的新闻运行情感分析'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100, help='处理数量限制')

    def handle(self, *args, **options):
        limit = options.get('limit', 100)

        news_list = NewsData.objects.filter(is_processed=False)[:limit]

        if not news_list.exists():
            self.stdout.write(self.style.SUCCESS('没有需要分析的新闻'))
            return

        self.stdout.write(f'需要分析 {news_list.count()} 条新闻...')

        analyzer = SentimentAnalyzer()
        count = 0

        for news in news_list:
            text = news.title
            if news.content:
                text += ' ' + news.content[:200]

            result = analyzer.analyze(text)
            news.sentiment_score = result['score']
            news.sentiment_label = result['label']

            # 生成关键词
            words = jieba.lcut(news.title)
            stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都',
                         '一', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着',
                         '没有', '看', '好', '自己', '这', '他', '她', '它', '们', '那',
                         '被', '从', '把', '让', '用', '为', '以', '但', '还', '与', '或',
                         '及', '等', '个', '中', '对', '之', '其', '公司', '股份', '有限'}
            import json
            keywords = [w for w in words if len(w) > 1 and w not in stopwords][:10]
            news.keywords = json.dumps(keywords, ensure_ascii=False)

            news.is_processed = True
            news.save()
            count += 1

        self.stdout.write(self.style.SUCCESS(f'情感分析完成！处理了 {count} 条新闻'))

        # 提示生成趋势数据
        self.stdout.write('\n下一步：生成情感趋势数据')
        self.stdout.write('  python manage.py generate_sentiment_trend')
