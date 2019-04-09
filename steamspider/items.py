# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from peewee import *

db = MySQLDatabase("steam_vgfuns", host='127.0.0.1', port=3306, user='root', passwd='Liseen315song', charset='utf8')


class TagsItem(scrapy.Item):
    tag_name = scrapy.Field()
    tag_value = scrapy.Field()


class TopSellersItem(scrapy.Item):
    app_id = scrapy.Field()
    thumb_url = scrapy.Field()
    tagids = scrapy.Field()
    name = scrapy.Field()
    released = scrapy.Field()
    discount = scrapy.Field()
    final_price = scrapy.Field()
    # origin_price = scrapy.Field()


class PopularNewsItem(TopSellersItem):
    pass


class AppDetailItem(TopSellersItem):
    des = scrapy.Field()
    highlight_movie = scrapy.Field()
    screenshot = scrapy.Field()
    developers = scrapy.Field()
    popular_tags = scrapy.Field()
    game_area_metascore = scrapy.Field()
    platforms = scrapy.Field()
    # 降价截至日期
    discount_countdown = scrapy.Field()
    origin_price = scrapy.Field()


class Tag(Model):
    tag_name = CharField(verbose_name='标签名称')
    tag_value = IntegerField(verbose_name='标签值')

    class Meta:
        database = db


class TopSellers(Model):
    app_id = CharField(verbose_name='app唯一id', null=False, unique=True)
    name = CharField(verbose_name='app名称', null=False)
    c_name = CharField(verbose_name='app中文名', null=True)
    thumb_url = CharField(verbose_name='封面url', null=True)
    tagids = CharField(verbose_name='标签')
    released = CharField(verbose_name='发布日期', null=False)
    discount = CharField(verbose_name='降价百分比', null=False, default='0')
    final_price = CharField(verbose_name='最终价格', null=False, default='0')

    class Meta:
        database = db


class PopularNews(TopSellers):
    pass


class AppDetail(TopSellers):
    des = TextField(verbose_name='描述', null=True)
    highlight_movie = CharField(verbose_name='焦点图视频')
    screenshot = TextField(verbose_name='焦点图地址列表')
    developers = CharField(verbose_name='开发商')
    popular_tags = CharField(verbose_name='热门标签')
    game_area_metascore = CharField(verbose_name='meta评分')
    platforms = CharField(verbose_name='平台',null=False,default='')
    discount_countdown = CharField(verbose_name='降价截至日期', null=False, default='0')
    origin_price = CharField(verbose_name='原始价格', null=False, default='0')
