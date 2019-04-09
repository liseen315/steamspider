# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from steamspider.items import TopSellersItem
from utils import log
import math
import time


class TopSellersSpider(Spider):
    name = 'topsellers'
    allowed_domains = ['store.steampowered.com']

    def __init__(self, *args, **kwargs):
        super(TopSellersSpider, self).__init__(*args, **kwargs)

        self.page_url = 'https://store.steampowered.com/search/results?l=schinese&filter=globaltopsellers&category1=998,21,10'
        self.current_pagenum = 1
        self.total_apps = None
        self.total_pagenum = None
        self.search_url = '{url}&page={pagenum}'

    def start_requests(self):
        yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
                      callback=self.parse_item, errback=self.error_parse)

    def parse_item(self, response):
        total_pagestr = response.xpath('//div[@class="search_pagination_left"]/text()').extract_first().strip()
        self.total_apps = int(total_pagestr[total_pagestr.rfind('共') + 1:total_pagestr.rfind('个')].strip())
        self.total_pagenum = math.ceil(self.total_apps / 25)
        applist = response.xpath('//a[contains(@class,"search_result_row")]')

        for app_item in applist:
            item = self.create_item()
            item['name'] = app_item.xpath('.//span[@class="title"]/text()').extract_first()
            tag_xpath = app_item.xpath('@data-ds-tagids').extract_first()
            item['tagids'] = tag_xpath[1:len(tag_xpath) - 1]
            # steam 时间格式还不统一..我先不转换了..
            # timetuple = time.strptime(
            #     app_item.xpath('.//div[contains(@class,"search_released")]/text()').extract_first(), "%Y年%m月%d日")
            # item['released'] = int(time.mktime(timetuple))
            item['released'] = app_item.xpath('.//div[contains(@class,"search_released")]/text()').extract_first()
            if (app_item.xpath('@data-ds-packageid').extract_first() is None):
                item['thumb_url'] = 'https://media.st.dl.bscstorage.net/steam/apps/{appid}/header_292x136.jpg'.format(
                    appid=app_item.xpath('@data-ds-appid').extract_first())
                item['app_id'] = app_item.xpath('@data-ds-appid').extract_first()
            else:
                item['thumb_url'] = 'https://media.st.dl.bscstorage.net/steam/subs/{appid}/header_292x136.jpg'.format(
                    appid=app_item.xpath('@data-ds-packageid').extract_first())
                item['app_id'] = app_item.xpath('@data-ds-packageid').extract_first()

            item['final_price'] = app_item.xpath(
                './/div[contains(@class,"search_price_discount_combined")]/@data-price-final').extract_first()

            if (app_item.xpath('.//div[contains(@class,"search_discount")]/span/text()').extract_first() is None):
                item['discount'] = '0'
                # item['origin_price'] = int(item['final_price']) * int(item['discount'])
            else:
                item['discount'] = app_item.xpath(
                    './/div[contains(@class,"search_discount")]/span/text()').extract_first()

                percent_num = float(str(item['discount']).strip('%'))
                # item['origin_price'] = round(int(item['final_price']) * (abs(percent_num / 100)))

            yield item

        self.current_pagenum += 1
        if (self.current_pagenum < self.total_pagenum):
            yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
                          callback=self.parse_item, errback=self.error_parse)

    def create_item(self):
        return TopSellersItem()

    def error_parse(self, faiture):
        request = faiture.request
        utils.log('error_parse url:%s meta:%s' % (request.url, request.meta))
