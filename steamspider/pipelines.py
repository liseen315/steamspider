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
            TopSellers.create(app_id=item['app_id'],
                              name=item['name'],
                              thumb_url=item['thumb_url'],
                              released=item['released'],
                              discount=item['discount'],
                              final_price=item['final_price'],
                              origin_price=item['origin_price'])

    def option_popularnew(self, item):
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
            PopularNews.create(app_id=item['app_id'],
                               name=item['name'],
                               thumb_url=item['thumb_url'],
                               released=item['released'],
                               discount=item['discount'],
                               final_price=item['final_price'],
                               origin_price=item['origin_price'])

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
            # print('=====DoesNotExist===',item)
            AppDetail.create(app_id=item['app_id'],
                             name=item['name'],
                             tagids=item['tagids'],
                             released=item['released'],
                             discount = item['discount'],
                             final_price = item['final_price'],
                             short_des=item['short_des'],
                             full_des = item['full_des'],
                             highlight_movie=item['highlight_movie'],
                             screenshot=item['screenshot'],
                             developers=item['developers'],
                             popular_tags=item['popular_tags'],
                             game_area_metascore=item['game_area_metascore'],
                             platforms=item['platforms'],
                             discount_countdown=item['discount_countdown'],
                             origin_price=item['origin_price'])

    def process_item(self, item, spider):

        try:
            self.switch[spider.name](item)
        except KeyError as e:
            print('error key value pipline')

        return item
