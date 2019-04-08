from scrapy import Spider, Request
from steamspider.items import AppDetailItem
import math
import time


class AppDetailSpider(Spider):
    name = 'appdetail'
    allowed_domains = ['store.steampowered.com']

    def __init__(self, *args, **kwargs):
        super(AppDetailSpider, self).__init__(*args, **kwargs)

        self.page_url = 'https://store.steampowered.com/search/results?search/&l=schinese&category1=998,21,10'
        self.current_pagenum = 1
        self.total_apps = None
        self.total_pagenum = None
        self.search_url = '{url}&page={pagenum}'
        self.screenshot_path = 'https://media.st.dl.bscstorage.net/steam/apps/{appid}/'

    def start_requests(self):
        yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
                      callback=self.parse_item)

    def parse_item(self, response):
        total_pagestr = response.xpath('//div[@class="search_pagination_left"]/text()').extract_first().strip()
        self.total_apps = int(total_pagestr[total_pagestr.rfind('共') + 1:total_pagestr.rfind('个')].strip())
        self.total_pagenum = math.ceil(self.total_apps / 25)
        applist = response.xpath('//a[contains(@class,"search_result_row")]')

        for app_item in applist:
            detail_url = app_item.xpath('@href').extract_first() + '&l=schinese'
            name = app_item.xpath('.//span[@class="title"]/text()').extract_first()
            tag_xpath = app_item.xpath('@data-ds-tagids').extract_first()
            tagids = tag_xpath[1:len(tag_xpath) - 1]
            released = app_item.xpath('.//div[contains(@class,"search_released")]/text()').extract_first()
            app_id = ''
            thumb_url = ''
            if (app_item.xpath('@data-ds-packageid').extract_first() is None):
                app_id = app_item.xpath('@data-ds-appid').extract_first()
                thumb_url = 'https://media.st.dl.bscstorage.net/steam/apps/{appid}/header_292x136.jpg'.format(
                    appid=app_item.xpath('@data-ds-appid').extract_first())
            else:
                app_id = app_item.xpath('@data-ds-packageid').extract_first()
                thumb_url = 'https://media.st.dl.bscstorage.net/steam/subs/{appid}/header_292x136.jpg'.format(
                    appid=app_item.xpath('@data-ds-packageid').extract_first())

            yield Request(url=detail_url, callback=self.parse_detail,
                          meta={'app_id': app_id, 'name': name, 'released': released, 'tagids': tagids,
                                'thumb_url': thumb_url})

        self.current_pagenum += 1
        # if (self.current_pagenum < self.total_pagenum):
        #     yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
        #                   callback=self.parse_item)

    def parse_detail(self, response):
        item = AppDetailItem()
        item['app_id'] = response.meta['app_id']
        item['thumb_url'] = response.meta['thumb_url']
        item['tagids'] = response.meta['tagids']
        item['name'] = response.meta['name']
        item['released'] = response.meta['released']
        des = response.xpath('//div[@id="game_area_description"]')
        desstr = des.xpath('string(.)').extract_first().strip()
        # 缺少剔除关于这款游戏或者直接抓html存储.待定
        item['des'] = desstr[6:len(desstr)].strip()
        # 轮播视频
        item['highlight_movie'] = response.xpath('//div[contains(@id,"highlight_movie_")]')[0].xpath(
            '@data-mp4-source').extract_first()
        # 轮播图
        screen_path_list = response.xpath('//div[contains(@class,"highlight_screenshot")]/@id').extract()
        screen_list = []

        for sitem in screen_path_list:
            conver_url = self.screenshot_path.format(appid=response.meta['app_id']) + sitem[
                                                                                      sitem.index('ss_'):len(sitem)]
            screen_list.append(conver_url)
        item['screenshot'] = ','.join(screen_list)

        item['developers'] = response.xpath('//div[contains(@id,"developers_list")]/a/text()').extract_first()

        popular_tags_xpath = response.xpath(
            '//div[contains(@class,"popular_tags_ctn")]//div[contains(@class,"popular_tags")]/a/text()').extract()

        popular_taglist = []
        for poular_tag_item in popular_tags_xpath:
            popular_taglist.append(poular_tag_item.strip())

        item['popular_tags'] = ','.join(popular_taglist)

        game_score = response.xpath(
            '//div[contains(@id,"game_area_metascore")]/div[contains(@class,"score")]/text()').extract_first()
        if (game_score is None):
            item['game_area_metascore'] = 0
        else:
            item['game_area_metascore'] = game_score.strip()

        platform_xpath_list = response.xpath('//span[contains(@class,"platform_img")]/@class').extract()
        platforms = []
        for platform_item in platform_xpath_list:
            platforms.append(platform_item.split(' ')[1])

        item['platforms'] = platforms


        yield item
