# steamspider

## 创建数据库

```mysql
create database steam_vgfuns character set utf8mb4;
```

## 项目采用Pipenv构建虚拟环境并安装依赖库

```bash
scrapy-fake-useragent = "*"
peewee = "*"
pymysql = "*"
scrapy = "==1.5.1"
scrapy-redis = "*"
```

## 项目目录结构

```bash 
├── Pipfile
├── Pipfile.lock
├── README.md
├── __pycache__
├── scrapy.cfg
├── scrapydweb_settings_v8.py
├── setup.py
├── steam.egg
├── steam_urls
└── steamspider
    ├── __init__.py
    ├── __pycache__
    ├── items.py
    ├── middlewares.py
    ├── pipelines.py
    ├── settings.py
    ├── spiders
    └── utils.py
```
