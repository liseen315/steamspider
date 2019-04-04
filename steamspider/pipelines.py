# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from .items import TopSellers, PopularNews


class MySQLPipeline(object):

    def process_item(self, item, spider):

        if (spider.name == 'topsellers'):

            if TopSellers.table_exists() == False:
                TopSellers.create_table()

            try:
                TopSellers.get(TopSellers.app_id == item['app_id'])
            except TopSellers.DoesNotExist:
                TopSellers.create(app_id=item['app_id'], name=item['name'], thumb_url=item['thumb_url'],
                                  released=item['released'], discount=item['discount'], final_price=item['final_price'],
                                  origin_price=item['origin_price'])
        elif (spider.name == 'poplularnew'):
            pass

        return item
