# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from .items import TopSellers, PopularNews, Tag, AppDetail


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
        if Tag.table_exists() == False:
            Tag.create_table()
        try:
            Tag.get(Tag.tag_value == int(item['tag_value']))
        except Tag.DoesNotExist:
            Tag.create(tag_name=item['tag_name'], tag_value=item['tag_value'])

    def option_detail(self, item):
        if AppDetail.table_exists() == False:
            AppDetail.create_table()

        try:
            target_app = AppDetail.get(AppDetail.app_id == item['app_id'])

            if target_app.discount != item['discount']:
                AppDetail.update(discount=item['discount']).where(AppDetail.app_id == item['app_id']).execute()

            if target_app.final_price != item['final_price']:
                AppDetail.update(final_price=item['final_price']).where(
                    AppDetail.app_id == item['app_id']).execute()

        except AppDetail.DoesNotExist:
            AppDetail.create(app_id=item['app_id'],
                             name=item['name'],
                             released=item['released'],
                             platforms=item['platforms']
                             )

    def process_item(self, item, spider):

        try:
            self.switch[spider.name](item)
        except KeyError as e:
            print('error key value pipline')

        return item
