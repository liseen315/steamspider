from scrapy import Spider, Request, FormRequest
from steamspider.items import AppDetailItem
from scrapy.utils.python import to_native_str
from pydispatch import dispatcher
from scrapy.utils.project import get_project_settings
from utils import log
import math
import time
import re


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

            yield Request(url=detail_url,
                          callback=self.parse_detail,
                          errback=self.error_parse,
                          cookies={
                              'wants_mature_content': '1',
                          },
                          meta={
                              'dont_redirect': True,
                              'app_id': app_id,
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
            log("(parse_page) Location header: %s" % response.headers['Location'])
            yield Request(
                url=to_native_str(response.headers['Location']),
                callback=self.parse_redirect,
                errback=self.error_parse,
                cookies={
                    'wants_mature_content': '1',
                },
                meta={
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

            if u'/sub/' in response.url:
                self.parse_sub(response)
                return

            des = response.xpath('//div[@id="game_area_description"]')
            desstr = des.xpath('string(.)').extract_first().strip()

            item['short_des'] = response.xpath(
                '//div[@class="game_description_snippet"]/text()').extract_first().strip()
            item['full_des'] = desstr[6:len(desstr)].strip()

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
                    purchase_game_wrapper.xpath(
                        './/div[@class="discount_original_price"]/text()').extract_first().split(
                        ' ')[1]
                item['origin_price'] = int(origin_price) * 100
            else:
                item['origin_price'] = '0'

            yield item

    def error_parse(self, faiture):
        request = faiture.request
        log('error_parse url:%s meta:%s' % (request.url, request.meta))

    def parse_redirect(self, response):
        print('===重定向过来的===', response.url)
        if response.status in (200,):
            template_content = response.xpath('//div[@class="responsive_page_template_content"]')
            jsstr = template_content.xpath('.//script[@type="text/javascript"][2]/text()').extract_first()
            g_sessionID_str = re.search(r'g_sessionID = "\w*"', str(jsstr)).group()
            g_sessionID = g_sessionID_str[g_sessionID_str.find('"')+1:len(g_sessionID_str)-1]
            print('====sessionID====',g_sessionID)
            post_url = 'https://store.steampowered.com/agecheckset/app/%s/' % str(response.meta['app_id'])
            return FormRequest(
                url=post_url,
                method='POST',
                formdata={
                    'ageDay': str(range(1, 25)),
                    'ageMonth': 'March',
                    'ageYear': str(1900),
                    'sessionid': g_sessionID,
                },
                meta={
                    'app_id': response.meta['app_id'],
                    'name': response.meta['name'],
                    'released': response.meta['released'],
                    'tagids': response.meta['tagids'],
                    'thumb_url': response.meta['thumb_url']},
                callback=self.parse_ajax)

    def parse_ajax(self,response):
        print('==parse_ajax==',response.body)

    def parse_sub(self, response):
        print('====礼包过来的===', response.url)
