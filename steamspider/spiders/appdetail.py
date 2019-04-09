from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from scrapy import Spider, Request
from steamspider.items import AppDetailItem
from scrapy.utils.python import to_native_str
from pydispatch import dispatcher
from scrapy.utils.project import get_project_settings
from scrapy import signals
from utils import log
import math
import time


class AppDetailSpider(Spider):
    name = 'appdetail'
    allowed_domains = ['store.steampowered.com']
    handle_httpstatus_list = [301, 302]

    def __init__(self, *args, **kwargs):
        super(AppDetailSpider, self).__init__(*args, **kwargs)

        self.page_url = 'https://store.steampowered.com/search/results?search/&l=schinese&category1=998,21,10'
        self.current_pagenum = 1
        self.total_apps = None
        self.total_pagenum = None
        self.search_url = '{url}&page={pagenum}'
        self.screenshot_path = 'https://media.st.dl.bscstorage.net/steam/apps/{appid}/'
        self.mysettings = get_project_settings()
        self.timeout = self.mysettings['SELENIUM_TIMEOUT']
        self.isLoadImage = self.mysettings['LOAD_IMAGE']
        self.windowHeight = self.mysettings['WINDOW_HEIGHT']
        self.windowWidth = self.mysettings['windowWidth']
        # 初始化chrome对象
        self.browser = webdriver.Chrome()
        if self.windowHeight and self.windowWidth:
            self.browser.set_window_size(self.windowWidth, self.windowHeight)
        self.browser.set_page_load_timeout(self.timeout)  # 页面加载超时时间
        self.wait = WebDriverWait(self.browser, 25)

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

            # detail_url = 'https://store.steampowered.com/app/323190/Frostpunk/?snr=1_7_7_230_150_1&l=schinese'

            yield Request(url=detail_url,
                          callback=self.parse_detail,
                          errback=self.error_parse,
                          meta={'app_id': app_id,
                                'name': name,
                                'released': released,
                                'tagids': tagids,
                                'thumb_url': thumb_url})

        self.current_pagenum += 1
        if (self.current_pagenum < self.total_pagenum):
            yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
                          callback=self.parse_item,errback=self.error_parse)

    def parse_detail(self, response):
        if response.status in (302,) and 'Location' in response.headers:
            log("(parse_page) Location header: %s" % response.headers['Location'])
            yield Request(
                url=to_native_str(response.headers['Location']),
                callback=self.parse_detail,
                errback= self.error_parse,
                # dont_filter=True,
                # cookies={'wants_mature_content': '1'},
                meta={'used_selenium': True,
                      'dont_redirect': True,
                      'app_id': response.meta['app_id'],
                      'name': response.meta['name'],
                      'released': response.meta['released'],
                      'tagids': response.meta['tagids'],
                      'thumb_url': response.meta['thumb_url']})

        if response.status in (200,):
            item = AppDetailItem()
            item['app_id'] = response.meta['app_id']
            item['thumb_url'] = response.meta['thumb_url']
            item['tagids'] = response.meta['tagids']
            item['name'] = response.meta['name']
            item['released'] = response.meta['released']
            des = response.xpath('//div[@id="game_area_description"]')
            desstr = des.xpath('string(.)').extract_first().strip()

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

            game_area_purchase_game_wrapper = response.xpath('//div[contains(@class,"game_area_purchase_game_wrapper")][1]')
            platform_xpath_list = game_area_purchase_game_wrapper.xpath('.//span[contains(@class,"platform_img")]/@class').extract()
            platforms = []
            for platform_item in platform_xpath_list:
                platforms.append(platform_item.split(' ')[1])

            item['platforms'] = ','.join(platforms)

            xpath_discount_countdown = response.xpath(
                '//p[@class="game_purchase_discount_countdown"]/text()').extract_first()

            # 这里会有倒计时,现在有问题
            if (xpath_discount_countdown is not None):
                item['discount_countdown'] = xpath_discount_countdown
            else:
                item['discount_countdown'] = '0'

            xpath_price_final = response.xpath(
                '//div[contains(@class,"game_purchase_discount")]/@data-price-final').extract_first()

            if (xpath_price_final is not None):
                item['final_price'] = xpath_price_final
            else:
                item['final_price'] = '0'

            xpath_discount_pct = response.xpath(
                '//div[contains(@class,"game_purchase_discount")]/div[@class="discount_pct"]/text()').extract_first()

            if (xpath_discount_pct is not None):
                item['discount'] = float(str(xpath_discount_pct).strip('%'))
            else:
                item['discount'] = '0'

            hasdiscount = len(response.xpath('//div[contains(@class,"game_purchase_discount")]'))
            has_game_wrapper = len(response.xpath('//div[contains(@class,"game_area_purchase_game_wrapper")]'))
            if (hasdiscount > 0 and has_game_wrapper == 0):
                discount = response.xpath('//div[contains(@class,"game_purchase_discount")]')
                xpath_origin_price = \
                    discount.xpath('.//div[@class="discount_original_price"]/text()').extract_first().split(' ')[1]
                item['origin_price'] = int(xpath_origin_price) * 100
            else:
                item['origin_price'] = '0'

            yield item


    def error_parse(self, faiture):
        request = faiture.request
        log('error_parse url:%s meta:%s' % (request.url, request.meta))

    def mySpiderCloseHandle(self):
        try:
            self.browser.quit()
        except Exception as e:
            pass
