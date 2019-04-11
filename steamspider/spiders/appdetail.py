from scrapy import Spider, Request
from utils import log
from steamspider.items import AppDetailItem
import math
import re


class AppDetailSpider(Spider):
    name = 'appdetail'
    allowed_domains = ['store.steampowered.com']
    handle_httpstatus_list = [301, 302]

    def __init__(self, *args, **kwargs):
        super(AppDetailSpider, self).__init__(*args, **kwargs)

        self.page_url = 'https://store.steampowered.com/search/results?search/&l=schinese&category1=10,998,21'
        self.current_pagenum = 1
        self.total_apps = 0
        self.total_pagenum = 0
        self.search_url = '{url}&page={pagenum}'
        self.media_path = 'https://media.st.dl.bscstorage.net/steam/{type}/{appid}/header_292x136.jpg'
        self.parse_switch = {'app':self.parse_app,'subs':self.parse_sub}

    def start_requests(self):
        yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
                      callback=self.parse_page)

    def parse_page(self, response):
        total_pagestr = response.xpath('//div[@class="search_pagination_left"]/text()').extract_first().strip()
        self.total_apps = int(total_pagestr[total_pagestr.rfind('共') + 1:total_pagestr.rfind('个')].strip())
        self.total_pagenum = math.ceil(self.total_apps / 25)

        print('=======parse_page=====', self.total_apps, self.total_pagenum, self.current_pagenum)

        applist = response.xpath('//a[contains(@class,"search_result_row")]')

        for app_item in applist:

            detail_url = app_item.xpath('@href').extract_first() + '&l=schinese'
            app_id, app_type = self.get_id(detail_url)

            if app_id and app_type is not 'error':

                xpath_tag = app_item.xpath('@data-ds-tagids')
                if len(xpath_tag) > 0:
                    tagids = xpath_tag.extract_first()[1:len(xpath_tag) - 1]

                thumb_url = self.media_path.format(type=app_type,appid=app_id)

                yield Request(url=detail_url,
                              callback=self.parse_switch[app_type],
                              errback=self.parse_error,
                              cookies={'wants_mature_content': '1',
                                       "birthtime": "725817601",
                                       "lastagecheckage": "1-January-1993"},
                              meta={'app_id': app_id,
                                    'app_type': app_type,
                                    'tagids': tagids,
                                    'thumb_url': thumb_url})

        self.current_pagenum += 1
        # if (self.current_pagenum < self.total_pagenum):
        #     yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
        #                   callback=self.parse_page,errback=self.error_parse)

    # 解析普通的app
    def parse_app(self,response):
        if response.status in (200,):
            item = AppDetailItem()
            # 强行设置一堆默认空字符串
            item.set_defalut('')

            item['app_id'] = response.meta['app_id']
            item['app_type'] = response.meta['app_type']
            item['name'] = response.xpath('//div[@class="apphub_AppName"]/text()').extract_first()
            # 发行日期
            release = response.xpath('//div[@class="release_date"]')
            if len(release) > 0:
                item['released'] = release.xpath('.//div[@class="date"]/text()').extract_first()

            # 获取预售大节点
            xpath_purchase = response.xpath('//div[@id="game_area_purchase"]')

            # 支持平台
            if len(xpath_purchase.xpath('.//div[@class="game_area_purchase_platform"]')) > 0:
                xpath_platform_list = xpath_purchase.xpath('.//div[@class="game_area_purchase_platform"]')[0].xpath('.//span/@class').extract()
                platforms = []
                for platform_item in xpath_platform_list:
                    platforms.append(platform_item.split(' ')[1])

                item['platforms'] = ','.join(platforms)

            # 原始价格
            xpath_original_price = xpath_purchase.xpath('.//div[@class="discount_original_price"]')
            if len(xpath_original_price) > 0:
                origin_price = xpath_original_price[0].xpath('text()').extract_first().split(' ')[1]
                item['origin_price'] = str(int(origin_price) * 100)

            # 折扣
            xpath_discount_pct = xpath_purchase.xpath('.//div[@class="discount_pct"]')
            if len(xpath_discount_pct) > 0:
                item['discount']=xpath_discount_pct[0].xpath('text()').extract_first().strip('%')

            # 折扣截至
            xpath_discount_countdown = xpath_purchase.xpath('.//p[@class="game_purchase_discount_countdown"]')
            if len(xpath_discount_countdown) > 0:
                pattern = re.compile('/(\d+)月(\d+)日/', re.S)
                str_countdown = xpath_discount_countdown[0].xpath('text()').extract_first()
                item['discount_countdown']= re.search(pattern,str_countdown).groups(1)

            # 现价
            xpath_final_price = xpath_purchase.xpath('.//@data-price-final')
            if len(xpath_final_price) > 0:
                item['final_price'] = xpath_final_price[0].extract()

            yield item

    # 解析礼品包
    def parse_sub(self,response):
        pass

    def parse_error(self, error):
        request = error.request
        log('error_parse url:%s meta:%s' % (request.url, request.meta))

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
            log('get_id other url:%s' % url)

        id = re.search(pattern, url)
        if id:
            id = id.group(1)
            return id, app_type

        log('get_id error url:%s' % url)
        return 0, 'error'
