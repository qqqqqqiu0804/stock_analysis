"""
报告生成模块 - 序列化器
"""

from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    """报告序列化器"""
    stock_code = serializers.CharField(source='stock.stock_code', read_only=True)
    stock_name = serializers.CharField(source='stock.stock_name', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['id', 'title', 'stock', 'stock_code', 'stock_name', 'report_type',
                  'report_type_display', 'start_date', 'end_date', 'status', 'status_display',
                  'file', 'file_url', 'file_size', 'description', 'created_by', 'created_by_name',
                  'created_at', 'completed_at']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class ReportCreateSerializer(serializers.Serializer):
    """报告创建序列化器"""
    stock_code = serializers.CharField(required=True)
    report_type = serializers.ChoiceField(choices=['pdf', 'excel'], required=True)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    days = serializers.IntegerField(required=False, default=90)


class ReportListSerializer(serializers.ModelSerializer):
    """报告列表序列化器（简化版）"""
    stock_code = serializers.CharField(source='stock.stock_code', read_only=True)
    stock_name = serializers.CharField(source='stock.stock_name', read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'title', 'stock_code', 'stock_name', 'report_type',
                  'status', 'created_at']
