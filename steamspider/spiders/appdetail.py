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
        # 当详情爬虫爬完了关闭掉浏览器
        dispatcher.connect(receiver=self.mySpiderCloseHandle,
                           signal=signals.spider_closed
                           )

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
                          cookies={'wants_mature_content': '1', "birthtime": "725817601",
                                   "lastagecheckage": "1-January-1993"},
                          meta={'app_id': app_id,
                                'name': name,
                                'released': released,
                                'tagids': tagids,
                                'thumb_url': thumb_url})

        self.current_pagenum += 1
        if (self.current_pagenum < self.total_pagenum):
            yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
                          callback=self.parse_item, errback=self.error_parse)

    def parse_detail(self, response):

        if response.status in (302,) and 'Location' in response.headers:
            log("请求重定向==111111==: %s" % response.headers['Location'])
            yield Request(
                url=to_native_str(response.headers['Location']),
                callback=self.parse_detail,
                errback=self.error_parse,
                # dont_filter=True,
                cookies={'wants_mature_content': '1'},
                meta={'used_selenium': True,
                      # 'dont_redirect': True,
                      'app_id': response.meta['app_id'],
                      'name': response.meta['name'],
                      'released': response.meta['released'],
                      'tagids': response.meta['tagids'],
                      'thumb_url': response.meta['thumb_url']})

        if response.status in (200,):
            print('=====response==200==url=====', response.url)
            if "agecheck" in response.url:
                return

            if "49520" in response.url:
                from scrapy.shell import inspect_response
                inspect_response(response, self)

            if u'/sub/' in response.url:
                # 礼包
                self.parse_sub(response)
                return
            item = AppDetailItem()
            item['app_id'] = response.meta['app_id']
            item['thumb_url'] = response.meta['thumb_url']
            item['tagids'] = response.meta['tagids']
            item['name'] = response.meta['name']
            item['released'] = response.meta['released']

            des = response.xpath('//div[@id="game_area_description"]')
            if len(des) > 0:
                desstr = des.xpath('string(.)').extract_first().strip()

            item['short_des'] = response.xpath(
                '//div[@class="game_description_snippet"]/text()').extract_first().strip()
            item['full_des'] = ''

            xpath_highlight_movie = response.xpath('//div[contains(@id,"highlight_movie_")]')
            if len(xpath_highlight_movie) > 0:
                # 轮播视频
                item['highlight_movie'] = response.xpath('//div[contains(@id,"highlight_movie_")]')[0].xpath(
                    '@data-mp4-source').extract_first()
            # 轮播图
            screen_path_list = response.xpath('//div[contains(@class,"highlight_screenshot")]/@id').extract()
            screen_list = []

            for sitem in screen_path_list:
                conver_url = self.screenshot_path.format(appid=response.meta['app_id']) + sitem[
                                                                                          len('thumb_screenshot_'):len(
                                                                                              sitem)]
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

            purchase_game_wrapper = response.xpath('//div[contains(@class,"game_area_purchase_game_wrapper")][1]')
            platform_xpath_list = purchase_game_wrapper.xpath(
                './/span[contains(@class,"platform_img")]/@class').extract()
            platforms = []
            for platform_item in platform_xpath_list:
                platforms.append(platform_item.split(' ')[1])

            item['platforms'] = ','.join(platforms)

            # 这里会有倒计时,现在有问题
            if (len(purchase_game_wrapper.xpath('.//p[@class="game_purchase_discount_countdown"]/text()')) > 0):
                item['discount_countdown'] = purchase_game_wrapper.xpath(
                    './/p[@class="game_purchase_discount_countdown"]/text()').extract_first()
            else:
                item['discount_countdown'] = '0'

            if (len(purchase_game_wrapper.xpath(
                    './/div[@class="discount_block game_purchase_discount"]/@data-price-final')) > 0):
                item['final_price'] = purchase_game_wrapper.xpath(
                    './/div[@class="discount_block game_purchase_discount"]/@data-price-final').extract_first()
            else:
                item['final_price'] = '0'

            xpath_discount_pct = purchase_game_wrapper.xpath(
                './/div[@class="discount_pct"]/text()').extract_first()

            if (len(purchase_game_wrapper.xpath('.//div[@class="discount_pct"]/text()')) > 0):
                item['discount'] = float(
                    str(purchase_game_wrapper.xpath('.//div[@class="discount_pct"]/text()').extract_first()).strip('%'))
            else:
                item['discount'] = '0'

            if (len(purchase_game_wrapper.xpath('.//div[@class="discount_original_price"]/text()')) > 0):
                origin_price = \
                purchase_game_wrapper.xpath('.//div[@class="discount_original_price"]/text()').extract_first().split(
                    ' ')[1]
                item['origin_price'] = int(origin_price) * 100
            else:
                item['origin_price'] = '0'

            yield item

    def error_parse(self, faiture):
        request = faiture.request
        log('error_parse url:%s meta:%s' % (request.url, request.meta))

    def parse_sub(self, response):
        pass

    def mySpiderCloseHandle(self):
        try:
            self.browser.quit()
        except Exception as e:
            pass
