# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from .items import TopSellers


class SteamspiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MySQLStorePipeline(object):

    def process_item(self, item, spider):
        if TopSellers.table_exists() == False:
            TopSellers.create_table()
        try:
            TopSellers.create(app_id=item['app_id'], name=item['name'])
        except Exception as e:
            print(e)

        return item
