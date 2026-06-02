"""
为新闻数据生成关键词
"""

import jieba
from django.core.management.base import BaseCommand
from apps.news.models import NewsData


class Command(BaseCommand):
    help = '为新闻数据生成关键词'

    def handle(self, *args, **options):
        stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都',
                     '一', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着',
                     '没有', '看', '好', '自己', '这', '他', '她', '它', '们', '那',
                     '被', '从', '把', '让', '用', '为', '以', '但', '还', '与', '或',
                     '及', '等', '个', '中', '对', '之', '其', '公司', '股份', '有限'}

        news_list = NewsData.objects.filter(keywords__isnull=True)
        self.stdout.write(f'需要处理 {news_list.count()} 条新闻...')

        import json
        count = 0
        for news in news_list:
            words = jieba.lcut(news.title)
            keywords = [w for w in words if len(w) > 1 and w not in stopwords][:10]
            news.keywords = json.dumps(keywords, ensure_ascii=False)
            news.save()
            count += 1

        self.stdout.write(self.style.SUCCESS(f'完成！处理了 {count} 条新闻'))
