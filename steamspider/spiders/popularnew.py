from scrapy import Spider,Request
from steamspider.items import PopularNewItem
from steamspider.utils import get_id
import math
import logging

# 热门新品

class PoppularNewSpider(Spider):
    name = 'poplularnew'

    def __init__(self, *args, **kwargs):
        super(PoppularNewSpider, self).__init__(*args, **kwargs)
        self.page_url = 'https://store.steampowered.com/search/?category1=998,21&os=win&filter=popularnew&sort_by=Released_DESC&l=schinese'
        self.current_pagenum = 1
        self.total_apps = 0
        self.total_pagenum = 0
        self.search_url = '{url}&page={pagenum}'

    def start_requests(self):
        yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
                      callback=self.parse_page)

    def parse_page(self,response):
        if not self.total_apps and not self.total_pagenum:
            total_pagestr = response.xpath('//div[@class="search_pagination_left"]/text()').extract_first().strip()
            self.total_apps = int(total_pagestr[total_pagestr.rfind('共') + 1:total_pagestr.rfind('个')].strip())
            self.total_pagenum = math.ceil(self.total_apps / 25)

        print('=======parse_offer_page=====', self.total_apps, self.total_pagenum, self.current_pagenum)

        applist = response.xpath('//a[contains(@class,"search_result_row")]')
        for app_item in applist:
            detail_url = app_item.xpath('@href').extract_first() + '&l=schinese'
            app_id, app_type = get_id(detail_url)

            if app_id and app_type is not 'error':
                item = PopularNewItem()
                item['app_id'] = app_id
                item['app_type'] = app_type
                item['origin_url'] = detail_url
                yield item

        self.current_pagenum += 1
        if (self.current_pagenum <= self.total_pagenum):
            yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
                          callback=self.parse_page, errback=self.parse_error)

    def parse_error(self, error):
        request = error.request
        logging.warning('error_parse url:%s meta:%s' % (request.url, request.meta))
