# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from peewee import *

db = MySQLDatabase("steam_vgfuns", host='127.0.0.1', port=3306, user='root', passwd='Liseen315song', charset='utf8')


class TopSellersItem(scrapy.Item):
    detail_url = scrapy.Field()
    app_id = scrapy.Field()
    tag_ids = scrapy.Field()
    crtrids = scrapy.Field()
    thumb_url = scrapy.Field()
    name = scrapy.Field()
    released = scrapy.Field()
    discount = scrapy.Field()
    final_price = scrapy.Field()


class TopSellers(Model):
    app_id = CharField(verbose_name='app_id', max_length=50)
    name = CharField(verbose_name='name')

    class Meta:
        database = db


class AppDetailItem(scrapy.Item):
    app_id = scrapy.Field()
