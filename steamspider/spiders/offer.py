from scrapy import Spider,Request
from steamspider.items import OfferItem

# 优惠
class OfferSpider(Spider):
    name = 'offerapp'

    def __init__(self, *args, **kwargs):
        super(OfferSpider, self).__init__(*args, **kwargs)
        self.page_url = 'https://store.steampowered.com/search/?category1=21,998,10&specials=1&l=schinese'
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
            app_id, app_type = self.get_id(detail_url)

            if app_id and app_type is not 'error':
                item = OfferItem()
                item['app_id'] = app_id
                item['app_type'] = app_type
                yield item

        self.current_pagenum += 1
        if (self.current_pagenum < self.total_pagenum):
            yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
                          callback=self.parse_page, errback=self.parse_error)


    def parse_error(self, error):
        request = error.request
        self.logger.log('WARNING','error_parse url:%s meta:%s' % (request.url, request.meta))


    # 这种通用的工具方法应该抽离走
    def get_id(self, url):
        app_type = ''
        if '/sub/' in url:
            # 礼包
            pattern = re.compile('/sub/(\d+)/',re.S)
            app_type = 'subs'
        elif '/app/' in url:
            # app
            pattern = re.compile('/app/(\d+)/', re.S)
            app_type = 'app'
        elif '/bundle/' in url:
            # 捆绑包
            pattern = re.compile('/bundle/(\d+)/', re.S)
            app_type = 'bundle'
        else:
            pattern = re.compile('/(\d+)/', re.S)
            app_type = 'other'
            self.logger.log('WARNING','get_id other url:%s' % url)

        id = re.search(pattern, url)
        if id:
            id = id.group(1)
            return id, app_type
        self.logger.log('WARNING', 'get_id error url:%s' % url)
        return 0, 'error'