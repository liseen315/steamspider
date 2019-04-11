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


class AppDetailItem(scrapy.Item):
    app_id = scrapy.Field()
    name = scrapy.Field()
    c_name = scrapy.Field()
    released = scrapy.Field()
    platforms = scrapy.Field()
    origin_price = scrapy.Field()
    discount = scrapy.Field()
    discount_countdown = scrapy.Field()
    final_price = scrapy.Field()
    game_area_metascore = scrapy.Field()
    tagids = scrapy.Field()
    popular_tags = scrapy.Field()
    developers = scrapy.Field()
    thumb_url = scrapy.Field()
    origin_url = scrapy.Field()
    short_des = scrapy.Field()
    full_des = scrapy.Field()
    highlight_movie = scrapy.Field()
    screenshot = scrapy.Field()



class TopSellersItem(AppDetailItem):
    pass


class PopularNewsItem(AppDetailItem):
    pass


class TagModel(Model):
    tag_name = CharField(verbose_name='标签名称')
    tag_value = IntegerField(verbose_name='标签值')

    class Meta:
        database = db


class AppDetailModel(Model):
    app_id = CharField(verbose_name='app唯一id', unique=True, index=True)
    name = CharField(verbose_name='app名称')
    c_name = CharField(verbose_name='app中文名', default='')
    released = CharField(verbose_name='发布日期', default='')
    platforms = CharField(verbose_name='平台', default='')

    # tagids = CharField(verbose_name='标签分类',null=True)
    # popular_tags = CharField(verbose_name='热门标签', null=True)
    # developers = CharField(verbose_name='开发商', null=True)
    # metascore = IntegerField(verbose_name='meta评分', default=0)
    # origin_price = IntegerField(verbose_name='原始价格', default=0)
    # discount = CharField(verbose_name='降价百分比', null=True)
    #
    # thumb_url = CharField(verbose_name='封面url', null=False)
    # origin_url = CharField(verbose_name='详情url', null=False)
    #
    # short_des = TextField(verbose_name='简短描述', null=True)
    # full_des = TextField(verbose_name='详细描述', null=True)
    # highlight_movie = CharField(verbose_name='焦点图视频',null=True)
    # screenshot = TextField(verbose_name='焦点图地址列表',null=True)
    #
    #
    # metascore = IntegerField(verbose_name='meta评分',default=0)
    # discount = CharField(verbose_name='降价百分比', null=True)
    # discount_countdown = IntegerField(verbose_name='降价截至时间', default=0)
    # final_price = CharField(verbose_name='最终价格', null=True)

    class Meta:
        database = db


class TopSellers(AppDetailModel):
    pass


class PopularNews(AppDetailModel):
    pass
