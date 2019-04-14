# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from peewee import *

db = MySQLDatabase("steam_vgfuns", host='127.0.0.1', port=3306, user='root', passwd='Liseen315song', charset='utf8mb4')


class TagsItem(scrapy.Item):
    tag_name = scrapy.Field()
    tag_value = scrapy.Field()


class AppDetailItem(scrapy.Item):
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

    def set_defalut(self, value):
        intcoup = ('origin_price','discount','discount_countdown','final_price','metascore')
        for keys, _ in self.fields.items():
            if keys in intcoup:
                self[keys] = '0'
            else:
                self[keys] = value

class PriceItem(scrapy.Item):
    app_id = scrapy.Field()
    final_price = scrapy.Field()

class OfferItem(scrapy.Item):
    app_id = scrapy.Field()
    app_type = scrapy.Field()
    origin_url = scrapy.Field()

class PopularNewItem(OfferItem):
    pass

class TagModel(Model):
    tag_name = CharField(verbose_name='标签名称')
    tag_value = IntegerField(verbose_name='标签值')

    class Meta:
        table_name = 'app_tags'
        database = db


class AppDetailModel(Model):
    app_id = CharField(verbose_name='app唯一id', unique=True, index=True)
    app_type = CharField(verbose_name='app类型')
    status = CharField(verbose_name='当前销售状态',default='0')
    name = CharField(verbose_name='app名称')
    c_name = CharField(verbose_name='app中文名',default='')
    released = CharField(verbose_name='发布日期')
    platforms = CharField(verbose_name='平台')
    origin_price = CharField(verbose_name='原始价格', default='0')
    discount = CharField(verbose_name='降价百分比', default='0')
    discount_countdown = CharField(verbose_name='降价截至时间', default='0')
    final_price = CharField(verbose_name='最终价格', default='0')
    metascore = CharField(verbose_name='meta评分', default='0')
    support_cn = CharField(verbose_name='是否支持中文',default='')
    recommended_list = CharField(verbose_name='相关推荐',default='')
    dlc_list = TextField(verbose_name='dlc列表',default='')
    tagids = CharField(verbose_name='标签分类',default='')
    popular_tags = CharField(verbose_name='热门标签分类',default='')
    developers = CharField(verbose_name='开发商',default='')
    sys_req = TextField(verbose_name='windows系统要求',default='')
    thumb_url = CharField(verbose_name='封面url',default='')
    origin_url = CharField(verbose_name='源url',default='')
    short_des = TextField(verbose_name='简介',default='')
    full_des = TextField(verbose_name='详情描述',default='')
    highlight_movie = TextField(verbose_name='轮播图视频',default='')
    screenshot = TextField(verbose_name='轮播图图片',default='')

    class Meta:
        table_name = 'app_detail'
        database = db

class PriceModel(Model):
    app_id = CharField(verbose_name='app唯一id', index=True)
    final_price = CharField(verbose_name='最终价格', default='0')

    class Meta:
        table_name = 'app_price'
        database = db

class OfferModel(Model):
    app_id = CharField(verbose_name='app唯一id', unique=True, index=True)
    app_type = CharField(verbose_name='app类型')
    origin_url = CharField(verbose_name='源url', default='')
    class Meta:
        table_name = 'offer_apps'
        database = db

class PopularModel(OfferModel):
    app_id = CharField(verbose_name='app唯一id', unique=True, index=True)
    app_type = CharField(verbose_name='app类型')
    origin_url = CharField(verbose_name='源url', default='')

    class Meta:
        table_name = 'popularnew'
        database = db

