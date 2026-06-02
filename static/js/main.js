/**
 * 光伏行业舆情与股价关联分析系统 - 主JS文件
 */

// 全局配置
const API_BASE = '/api';

// AJAX请求封装
function apiRequest(url, options = {}) {
    const defaults = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    };

    const config = {
        ...defaults,
        ...options,
        headers: {
            ...defaults.headers,
            ...options.headers
        }
    };

    return $.ajax({
        url: url,
        ...config
    });
}

// 获取Cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 显示加载状态
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center py-5">
                <div class="loading-spinner"></div>
                <p class="mt-3 text-muted">加载中...</p>
            </div>
        `;
    }
}

// 显示空状态
function showEmpty(elementId, message = '暂无数据') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox"></i>
                <p>${message}</p>
            </div>
        `;
    }
}

// 显示错误信息
function showError(elementId, message = '加载失败，请稍后重试') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-exclamation-circle text-danger"></i>
                <p class="text-danger">${message}</p>
                <button class="btn btn-outline-primary btn-sm" onclick="location.reload()">
                    <i class="bi bi-arrow-clockwise"></i> 刷新页面
                </button>
            </div>
        `;
    }
}

// 显示提示消息
function showToast(message, type = 'success') {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// 用户登出
function logout() {
    apiRequest(`${API_BASE}/users/logout/`, {
        type: 'POST'
    }).done(() => {
        window.location.href = '/';
    }).fail(() => {
        window.location.href = '/';
    });
}

// 格式化数字
function formatNumber(num) {
    if (num >= 100000000) {
        return (num / 100000000).toFixed(2) + '亿';
    } else if (num >= 10000) {
        return (num / 10000).toFixed(2) + '万';
    }
    return num.toLocaleString();
}

// 格式化日期
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN');
}

// 获取情感标签样式
function getSentimentBadgeClass(label) {
    switch (label) {
        case 'positive': return 'badge-positive';
        case 'negative': return 'badge-negative';
        default: return 'badge-neutral';
    }
}

// 获取情感标签文本
function getSentimentText(label) {
    switch (label) {
        case 'positive': return '正面';
        case 'negative': return '负面';
        default: return '中性';
    }
}

// ECharts通用配置
const ECHARTS_THEME = {
    color: ['#4472C4', '#ED7D31', '#A5A5A5', '#FFC000', '#5B9BD5', '#70AD47'],
    backgroundColor: 'transparent',
    textStyle: {
        fontFamily: 'Microsoft YaHei, PingFang SC, Helvetica Neue, Arial, sans-serif'
    }
};

// 初始化ECharts实例
function initChart(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return null;
    return echarts.init(element, ECHARTS_THEME);
}

// 窗口大小改变时重绘图表
let resizeTimer;
$(window).on('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        // 触发所有ECharts实例的resize
        document.querySelectorAll('[data-echarts]').forEach(element => {
            const chart = echarts.getInstanceByDom(element);
            if (chart) {
                chart.resize();
            }
        });
    }, 200);
});

// 文档加载完成
$(document).ready(function() {
    // 初始化工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
