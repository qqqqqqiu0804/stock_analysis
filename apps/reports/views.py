"""
报告生成模块 - 视图
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import FileResponse
from django.utils import timezone
from datetime import datetime, timedelta
import os

from .models import Report
from .serializers import (
    ReportSerializer, ReportCreateSerializer, ReportListSerializer
)
from apps.stocks.models import StockInfo, DailyQuotes
from apps.news.models import NewsData
from apps.analysis.models import AnalysisResult, SentimentTrend
from utils.report_generator import ReportGenerator


class ReportListView(generics.ListAPIView):
    """报告列表"""
    queryset = Report.objects.select_related('stock', 'created_by').all()
    serializer_class = ReportListSerializer
    filterset_fields = ['stock__stock_code', 'report_type', 'status']


class ReportDetailView(generics.RetrieveAPIView):
    """报告详情"""
    queryset = Report.objects.select_related('stock', 'created_by').all()
    serializer_class = ReportSerializer


class ReportCreateView(APIView):
    """创建报告"""

    def post(self, request):
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stock_code = serializer.validated_data['stock_code']
        report_type = serializer.validated_data['report_type']
        days = serializer.validated_data.get('days', 90)
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')

        try:
            stock = StockInfo.objects.get(stock_code=stock_code)
        except StockInfo.DoesNotExist:
            return Response({'error': '股票不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not start_date:
            start_date = datetime.now().date() - timedelta(days=days)
        if not end_date:
            end_date = datetime.now().date()

        # 创建报告记录
        report = Report.objects.create(
            title=f"{stock.stock_name}({stock_code})分析报告",
            stock=stock,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            status='pending',
            created_by=request.user if request.user.is_authenticated else None
        )

        # 异步生成报告
        try:
            _generate_report(report)
            return Response({
                'message': '报告生成成功',
                'report': ReportSerializer(report, context={'request': request}).data
            })
        except Exception as e:
            report.status = 'failed'
            report.save()
            return Response(
                {'error': f'报告生成失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def _generate_report(report):
    """生成报告"""
    from apps.stocks.models import DailyQuotes
    from apps.news.models import NewsData
    from apps.analysis.models import SentimentTrend

    stock = report.stock
    start_date = report.start_date
    end_date = report.end_date

    # 获取数据
    quotes = DailyQuotes.objects.filter(
        stock_code=stock,
        trade_date__gte=start_date,
        trade_date__lte=end_date
    ).order_by('trade_date')

    news = NewsData.objects.filter(
        stock=stock,
        publish_time__date__gte=start_date,
        publish_time__date__lte=end_date
    ).order_by('-publish_time')[:50]

    sentiment_trends = SentimentTrend.objects.filter(
        stock=stock,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')

    analysis_results = AnalysisResult.objects.filter(
        stock=stock,
        analysis_date__gte=start_date,
        analysis_date__lte=end_date
    )

    # 准备数据
    report_data = {
        'stock': {
            'code': stock.stock_code,
            'name': stock.stock_name,
            'industry': stock.industry,
        },
        'period': f"{start_date} 至 {end_date}",
        'quotes': [
            {
                'date': q.trade_date.strftime('%Y-%m-%d'),
                'open': str(q.open_price),
                'close': str(q.close_price),
                'high': str(q.high_price),
                'low': str(q.low_price),
                'volume': q.volume,
                'change': str(q.change_pct) if q.change_pct else '0'
            }
            for q in quotes
        ],
        'news': [
            {
                'title': n.title,
                'date': n.publish_time.strftime('%Y-%m-%d'),
                'source': n.source_name or '',
                'sentiment': n.sentiment_label or 'neutral',
                'score': str(n.sentiment_score) if n.sentiment_score else 'N/A'
            }
            for n in news
        ],
        'sentiment_trend': [
            {
                'date': s.date.strftime('%Y-%m-%d'),
                'score': str(s.sentiment_score),
                'count': s.news_count
            }
            for s in sentiment_trends
        ],
        'analysis': [
            {
                'type': a.get_analysis_type_display(),
                'date': a.analysis_date.strftime('%Y-%m-%d'),
                'summary': a.analysis_summary or ''
            }
            for a in analysis_results
        ]
    }

    # 生成报告
    generator = ReportGenerator()

    if report.report_type == 'pdf':
        file_path = generator.generate_pdf(report_data, report.id)
    else:
        file_path = generator.generate_excel(report_data, report.id)

    # 更新报告状态
    report.file = file_path
    report.status = 'completed'
    report.completed_at = timezone.now()
    if os.path.exists(file_path):
        report.file_size = os.path.getsize(file_path)
    report.save()


@api_view(['GET'])
def download_report(request, report_id):
    """下载报告"""
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return Response({'error': '报告不存在'}, status=status.HTTP_404_NOT_FOUND)

    if report.status != 'completed' or not report.file:
        return Response({'error': '报告尚未完成'}, status=status.HTTP_400_BAD_REQUEST)

    if not os.path.exists(report.file.path):
        return Response({'error': '报告文件不存在'}, status=status.HTTP_404_NOT_FOUND)

    response = FileResponse(open(report.file.path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(report.file.name)}"'
    return response


@api_view(['DELETE'])
def delete_report(request, report_id):
    """删除报告"""
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return Response({'error': '报告不存在'}, status=status.HTTP_404_NOT_FOUND)

    # 删除文件
    if report.file and os.path.exists(report.file.path):
        os.remove(report.file.path)

    report.delete()
    return Response({'message': '报告已删除'})
