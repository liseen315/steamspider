# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from steamspider.items import TopSellersItem
import math


class TopSellersSpider(Spider):
    name = 'topsellers'
    allowed_domains = ['store.steampowered.com']

    def __init__(self, *args, **kwargs):
        super(TopSellersSpider, self).__init__(*args, **kwargs)
        self.page_url = 'https://store.steampowered.com/search/results?l=schinese&filter=topsellers&category1=998,21,10'
        self.current_pagenum = 1
        self.total_apps = None
        self.total_pagenum = None
        self.search_url = '{url}&page={pagenum}'

    def start_requests(self):
        yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
                      callback=self.parse_topsellers)

    def parse_topsellers(self, response):
        self.current_pagenum += 1
        total_pagestr = response.xpath('//div[@class="search_pagination_left"]/text()').extract_first().strip()
        self.total_apps = int(total_pagestr[total_pagestr.rfind('共') + 1:total_pagestr.rfind('个')].strip())
        self.total_pagenum = math.ceil(self.total_apps / 25)

        applist = response.xpath('//a[contains(@class,"search_result_row")]')

        for app_item in applist:
            item = TopSellersItem()
            item['detail_url'] = app_item.xpath('@href').extract_first()
            item['app_id'] = app_item.xpath('@data-ds-appid').extract_first()
            tagids = app_item.xpath('@data-ds-tagids').extract_first()
            item['tag_ids'] = tagids[1:len(tagids) - 1]
            # item['descids'] = app_item.xpath('@data-ds-crtrids').extract_first()
            item['thumb_url'] = app_item.xpath('div[contains(@class,"search_capsule")]/img/@src').extract_first()
            item['name'] = app_item.xpath(
                'div[contains(@class,"responsive_search_name_combined")]/div/span[contains(@class,"title")]/text()').extract_first()
            item['released'] = app_item.xpath(
                'div[contains(@class,"responsive_search_name_combined")]/div[contains(@class,"search_released")]/text()').extract_first()
            item['discount'] = 0
            item['final_price'] = app_item.xpath(
                'div[contains(@class,"responsive_search_name_combined")]/div[contains(@class,"search_price_discount_combined")]/@data-price-final').extract_first()

            yield item
        #
        # yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
        #               callback=self.parse_topsellers)
