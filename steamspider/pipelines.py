# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from .items import TagModel, AppDetailModel, PriceModel, OfferModel,PopularModel
from datetime import datetime

class MySQLPipeline(object):

    def __init__(self):
        self.switch = {'offerapp': self.option_offer, 'poplularnew': self.option_popularnew,
                       'apptags': self.option_apptags
            , 'appdetail': self.option_detail}

    def option_offer(self, item):

        if OfferModel.table_exists() == False:
            OfferModel.create_table()

        try:
            OfferModel.get(OfferModel.app_id == item['app_id'])
        except OfferModel.DoesNotExist:
            OfferModel.create(app_id=item['app_id'], app_type=item['app_type'], origin_url=item['origin_url'])

    def open_spider(self, spider):
        if spider.name == 'offerapp':
            if OfferModel.table_exists():
                OfferModel.drop_table()

        if spider.name == 'poplularnew':
            if PopularModel.table_exists():
                PopularModel.drop_table()

    def option_popularnew(self, item):
        if PopularModel.table_exists() == False:
            PopularModel.create_table()

        try:
            PopularModel.get(PopularModel.app_id == item['app_id'])
        except PopularModel.DoesNotExist:
            PopularModel.create(app_id=item['app_id'], app_type=item['app_type'], origin_url=item['origin_url'])

    def option_apptags(self, item):

        if TagModel.table_exists() == False:
            TagModel.create_table()
        try:
            TagModel.get(TagModel.tag_value == int(item['tag_value']))
        except TagModel.DoesNotExist:
            TagModel.create(tag_name=item['tag_name'], tag_value=item['tag_value'])

    def option_detail(self, item):
        if AppDetailModel.table_exists() == False:
            AppDetailModel.create_table()

        if PriceModel.table_exists() == False:
            PriceModel.create_table()

        try:
            target_app = AppDetailModel.get(AppDetailModel.app_id == item['app_id'])

            if target_app.discount != item['discount']:
                target_app.discount = item['discount']
                target_app.save()

            if target_app.final_price != item['final_price']:
                target_app.final_price = item['final_price']
                target_app.save()

                # 最终价格不同的时候往价格表里存放新数据保证是在售的app.并且之前价格表里不存在冗余数据
                if item['status'] == '0' and len(PriceModel.select().where(PriceModel.app_id == item['app_id'],
                                                                           PriceModel.final_price == item[
                                                                               'final_price'])) <= 0:
                    PriceModel.create(app_id=item['app_id'], final_price=item['final_price'])

            if target_app.discount_countdown != item['discount_countdown']:
                target_app.discount_countdown = item['discount_countdown']
                target_app.save()

            target_app.updatedAt = datetime.now()
            target_app.save()

        except AppDetailModel.DoesNotExist:
            # 经过验证如果给数据库一个不存在的item['xxx']会报error key value pipline 所以决定先小步迭代直到数据基本稳定
            AppDetailModel.create(app_id=item['app_id'],
                                  app_type=item['app_type'],
                                  status=item['status'],
                                  name=item['name'],
                                  released=item['released'],
                                  platforms=item['platforms'],
                                  origin_price=item['origin_price'],
                                  discount=item['discount'],
                                  discount_countdown=item['discount_countdown'],
                                  final_price=item['final_price'],
                                  metascore=item['metascore'],
                                  support_cn=item['support_cn'],
                                  recommended_list=item['recommended_list'],
                                  dlc_list=item['dlc_list'],
                                  tagids=item['tagids'],
                                  popular_tags=item['popular_tags'],
                                  developers=item['developers'],
                                  sys_req=item['sys_req'],
                                  thumb_url=item['thumb_url'],
                                  origin_url=item['origin_url'],
                                  short_des=item['short_des'],
                                  full_des=item['full_des'],
                                  highlight_movie=item['highlight_movie'],
                                  screenshot=item['screenshot']
                                  )
            # 这个地方得改造一下 只有在售的才会存储价格
            if item['status'] == '0' and len(PriceModel.select().where(PriceModel.app_id == item['app_id'],
                                                                       PriceModel.final_price == item[
                                                                           'final_price'])) <= 0:
                PriceModel.create(app_id=item['app_id'], final_price=item['final_price'])

    def process_item(self, item, spider):

        try:
            self.switch[spider.name](item)
        except KeyError as e:
            print('error key value pipline')

        return item
