# 光伏行业舆情与股价关联分析系统

## 项目简介

本系统是一个基于Django的光伏行业舆情与股价关联分析平台，通过采集光伏行业上市公司的舆情数据和股价数据，研究舆情对股价波动的影响机制。

## 功能特性

- 多源数据采集：股票行情数据、财经新闻舆情数据
- 情感分析：基于SnowNLP的中文情感分析
- 主题分析：基于LDA的主题模型分析
- 相关性分析：舆情情感与股价波动的关联分析
- 数据可视化：K线图、情感趋势图、词云图等
- 报告生成：PDF/Excel格式的分析报告

## 技术栈

- **后端**：Python 3.8+ / Django 4.x / DRF / Celery
- **前端**：Bootstrap 5 / ECharts 5 / jQuery
- **数据库**：MySQL 8.0 / Redis
- **数据分析**：Pandas / NumPy / jieba / SnowNLP / scikit-learn

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置

修改 `stock_analysis/settings.py` 中的数据库配置：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stock_analysis',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 3. 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE stock_analysis CHARACTER SET utf8mb4;"

# 执行迁移
python manage.py makemigrations
python manage.py migrate

# 创建管理员
python manage.py createsuperuser
```

### 4. 启动服务

```bash
# 启动Django服务
python manage.py runserver

# 启动Celery（另开终端）
celery -A stock_analysis worker -l info
```

访问 http://127.0.0.1:8000/ 即可使用系统。

## 项目结构

```
stock_analysis/
├── manage.py
├── requirements.txt
├── README.md
├── stock_analysis/      # 项目配置
├── apps/                # 应用模块
│   ├── users/           # 用户管理
│   ├── stocks/          # 股票数据
│   ├── news/            # 舆情数据
│   ├── analysis/        # 分析模块
│   └── reports/         # 报告生成
├── templates/           # 模板文件
├── static/              # 静态文件
├── utils/               # 工具模块
└── tests/               # 测试文件
```
