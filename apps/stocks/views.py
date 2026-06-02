"""
股票数据模块 - 视图
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from datetime import datetime, timedelta

from .models import StockInfo, DailyQuotes
from .serializers import (
    StockInfoSerializer, StockListSerializer, DailyQuotesSerializer,
    StockQuoteQuerySerializer, StockSearchSerializer
)


class StockListView(generics.ListAPIView):
    """股票列表"""
    queryset = StockInfo.objects.filter(is_active=True)
    serializer_class = StockListSerializer
    search_fields = ['stock_code', 'stock_name', 'industry']
    ordering_fields = ['stock_code', 'stock_name']


class StockDetailView(generics.RetrieveAPIView):
    """股票详情"""
    queryset = StockInfo.objects.all()
    serializer_class = StockInfoSerializer
    lookup_field = 'stock_code'


class StockQuotesView(APIView):
    """股票行情数据"""

    def get(self, request):
        serializer = StockQuoteQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        stock_code = serializer.validated_data['stock_code']
        days = serializer.validated_data.get('days', 30)

        try:
            stock = StockInfo.objects.get(stock_code=stock_code)
        except StockInfo.DoesNotExist:
            return Response({'error': '股票不存在'}, status=status.HTTP_404_NOT_FOUND)

        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')

        if not start_date:
            start_date = datetime.now().date() - timedelta(days=days)
        if not end_date:
            end_date = datetime.now().date()

        quotes = DailyQuotes.objects.filter(
            stock_code=stock,
            trade_date__gte=start_date,
            trade_date__lte=end_date
        ).order_by('trade_date')

        return Response({
            'stock': StockInfoSerializer(stock).data,
            'quotes': DailyQuotesSerializer(quotes, many=True).data,
            'count': quotes.count()
        })


class StockSearchView(APIView):
    """股票搜索"""

    def get(self, request):
        serializer = StockSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        keyword = serializer.validated_data['keyword']
        stocks = StockInfo.objects.filter(
            Q(stock_code__icontains=keyword) | Q(stock_name__icontains=keyword)
        )[:20]

        return Response(StockListSerializer(stocks, many=True).data)


@api_view(['GET'])
def stock_list_summary(request):
    """股票列表摘要（带最新行情）"""
    stocks = StockInfo.objects.filter(is_active=True)
    result = []

    for stock in stocks[:50]:
        latest_quote = DailyQuotes.objects.filter(stock_code=stock).order_by('-trade_date').first()
        data = StockInfoSerializer(stock).data
        if latest_quote:
            data['latest_price'] = str(latest_quote.close_price)
            data['latest_change'] = str(latest_quote.change_pct) if latest_quote.change_pct else None
            data['latest_date'] = latest_quote.trade_date
        result.append(data)

    return Response(result)


@api_view(['GET'])
def kline_data(request, stock_code):
    """K线图数据"""
    days = int(request.query_params.get('days', 60))

    try:
        stock = StockInfo.objects.get(stock_code=stock_code)
    except StockInfo.DoesNotExist:
        return Response({'error': '股票不存在'}, status=status.HTTP_404_NOT_FOUND)

    quotes = DailyQuotes.objects.filter(
        stock_code=stock
    ).order_by('-trade_date')[:days]

    quotes = quotes[::-1]  # 按日期正序

    data = {
        'stock': StockInfoSerializer(stock).data,
        'dates': [q.trade_date.strftime('%Y-%m-%d') for q in quotes],
        'kline_data': [[str(q.open_price), str(q.close_price), str(q.low_price), str(q.high_price)] for q in quotes],
        'volumes': [q.volume for q in quotes],
        'amounts': [str(q.amount) for q in quotes],
    }

    # 计算均线
    closes = [float(q.close_price) for q in quotes]
    data['ma5'] = _calculate_ma(closes, 5)
    data['ma10'] = _calculate_ma(closes, 10)
    data['ma20'] = _calculate_ma(closes, 20)
    data['ma30'] = _calculate_ma(closes, 30)

    return Response(data)


def _calculate_ma(data, period):
    """计算移动平均线"""
    ma = []
    for i in range(len(data)):
        if i < period - 1:
            ma.append(None)
        else:
            ma.append(round(sum(data[i - period + 1:i + 1]) / period, 2))
    return ma
