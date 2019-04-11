# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from .items import TagModel, AppDetailModel


class MySQLPipeline(object):

    def __init__(self):
        self.switch = {'topsellers': self.option_topsellers, 'poplularnew': self.option_popularnew,
                       'apptags': self.option_apptags
            , 'appdetail': self.option_detail}

    def option_topsellers(self, item):
        pass

    def option_popularnew(self, item):
        pass

    def option_apptags(self, item):

        if TagModel.table_exists() == False:
            TagModel.create_table()
        try:
            TagModel.get(TagModel.tag_value == int(item['tag_value']))
        except Tag.DoesNotExist:
            TagModel.create(tag_name=item['tag_name'], tag_value=item['tag_value'])

    def option_detail(self, item):
        if AppDetailModel.table_exists() == False:
            AppDetailModel.create_table()

        try:
            target_app = AppDetailModel.get(AppDetailModel.app_id == item['app_id'])

            # if target_app.discount != item['discount']:
            #     AppDetail.update(discount=item['discount']).where(AppDetail.app_id == item['app_id']).execute()
            #
            # if target_app.final_price != item['final_price']:
            #     AppDetail.update(final_price=item['final_price']).where(
            #         AppDetail.app_id == item['app_id']).execute()

        except AppDetailModel.DoesNotExist:
            # 经过验证如果给数据库一个不存在的item['xxx']会报error key value pipline 所以决定先小步迭代直到数据基本稳定
            AppDetailModel.create(app_id=item['app_id'],
                                  app_type=item['app_type'],
                                  name=item['name'],
                                  released=item['released'],
                                  platforms=item['platforms'],
                                  origin_price=item['origin_price'],
                                  discount=item['discount'],
                                  discount_countdown=item['discount_countdown'],
                                  final_price=item['final_price'],
                                  metascore=item['metascore'],
                                  tagids=item['tagids'],
                                  popular_tags=item['popular_tags'],
                                  developers=item['developers'],
                                  thumb_url=item['thumb_url'],
                                  origin_url=item['origin_url'],
                                  short_des=item['short_des'],
                                  full_des=item['full_des'],
                                  highlight_movie=item['highlight_movie'],
                                  screenshot=item['screenshot']
                                  )

    def process_item(self, item, spider):

        try:
            self.switch[spider.name](item)
        except KeyError as e:
            print('error key value pipline')

        return item
