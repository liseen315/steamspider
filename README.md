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

## 爬取字段

```bash
  app_id = scrapy.Field()
  app_type = scrapy.Field()
  status = scrapy.Field() # 0在售|1即将推出2|停止销售
  name = scrapy.Field()
  c_name = scrapy.Field()
  released = scrapy.Field()
  platforms = scrapy.Field()
  origin_price = scrapy.Field()
  discount = scrapy.Field()
  discount_countdown = scrapy.Field()
  final_price = scrapy.Field()
  metascore = scrapy.Field()
  support_cn = scrapy.Field()
  recommended_list = scrapy.Field()
  dlc_list = scrapy.Field()
  tagids = scrapy.Field()
  popular_tags = scrapy.Field()
  developers = scrapy.Field()
  sys_req = scrapy.Field()
  thumb_url = scrapy.Field()
  origin_url = scrapy.Field()
  short_des = scrapy.Field()
  full_des = scrapy.Field()
  highlight_movie = scrapy.Field()
  screenshot = scrapy.Field()
```

## 数据库爬取截图


