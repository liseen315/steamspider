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
                target_app = TopSellers.get(TopSellers.app_id == item['app_id'])
                if target_app.discount != item['discount']:
                    TopSellers.update(discount=item['discount']).where(TopSellers.app_id == item['app_id']).execute()

                if target_app.final_price != item['final_price']:
                    TopSellers.update(final_price=item['final_price']).where(
                        TopSellers.app_id == item['app_id']).execute()

            except TopSellers.DoesNotExist:
                TopSellers.create(app_id=item['app_id'], name=item['name'], thumb_url=item['thumb_url'],
                                  released=item['released'], discount=item['discount'], final_price=item['final_price'],
                                  origin_price=item['origin_price'])

        elif (spider.name == 'poplularnew'):
            if PopularNews.table_exists() == False:
                PopularNews.create_table()

            try:
                target_app = PopularNews.get(PopularNews.app_id == item['app_id'])

                if target_app.discount != item['discount']:
                    PopularNews.update(discount=item['discount']).where(PopularNews.app_id == item['app_id']).execute()

                if target_app.final_price != item['final_price']:
                    PopularNews.update(final_price=item['final_price']).where(
                        PopularNews.app_id == item['app_id']).execute()

            except PopularNews.DoesNotExist:
                PopularNews.create(app_id=item['app_id'], name=item['name'], thumb_url=item['thumb_url'],
                                   released=item['released'], discount=item['discount'],
                                   final_price=item['final_price'],
                                   origin_price=item['origin_price'])

        return item
