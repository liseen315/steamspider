# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from peewee import *

db = MySQLDatabase("steam_vgfuns", host='127.0.0.1', port=3306, user='root', passwd='Liseen315song', charset='utf8')


class TopSellersItem(scrapy.Item):
    app_id = scrapy.Field()
    thumb_url = scrapy.Field()
    name = scrapy.Field()
    released = scrapy.Field()
    discount = scrapy.Field()
    final_price = scrapy.Field()
    origin_price = scrapy.Field()

class PopularNewsItem(TopSellersItem):
    pass

class AppDetailItem(TopSellersItem):
    pass


class TopSellers(Model):
    app_id = CharField(verbose_name='app唯一id', null=False, unique=True)
    name = CharField(verbose_name='app名称', null=False)
    thumb_url = CharField(verbose_name='封面url', null=False)
    released = CharField(verbose_name='发布日期', null=False)
    discount = CharField(verbose_name='讲价百分比', null=False)
    final_price = CharField(verbose_name='最终价格', null=False)
    origin_price = CharField(verbose_name='原始价格', null=False)

    class Meta:
        database = db

class PopularNews(TopSellers):
    pass
