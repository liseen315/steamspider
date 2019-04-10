# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from scrapy.http import HtmlResponse
from scrapy import signals
from utils import log, get_platform
import time


class SteamspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SteamspiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SeleniumMiddleware(object):

    def process_request(self, request, spider):

        if spider.name == 'appdetail':
            used_selenium = request.meta.get('used_selenium',False)
            if used_selenium:
                try:
                    spider.browser.get(request.url)
                    submit = spider.wait.until(
                        EC.presence_of_element_located((By.XPATH, '//a[contains(@class,"btnv6_blue_hoverfade btn_medium")][1]')))

                    spider.browser.implicitly_wait(1)
                    day = spider.browser.find_element_by_xpath('//select[@name="ageDay"]/option[text()="15"]')
                    spider.browser.implicitly_wait(1)
                    day.click()

                    month = spider.browser.find_element_by_xpath('//select[@name="ageMonth"]/option[text()="March"]')
                    spider.browser.implicitly_wait(1)
                    month.click()

                    year = spider.browser.find_element_by_xpath('//select[@name="ageYear"]/option[text()="1985"]')

                    spider.browser.implicitly_wait(1)
                    year.click()

                    spider.browser.implicitly_wait(1)
                    submit.click()

                    try:
                        element = WebDriverWait(spider.browser, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@id="game_area_description"]')))

                        page_source = spider.browser.page_source

                        return HtmlResponse(url=request.url, body=page_source, request=request,
                                            encoding='utf-8', status=200,meta=request.meta)

                    except TimeoutException as e:
                        return HtmlResponse(url=request.url, status=500, request=request)

                except Exception as e:
                    return HtmlResponse(url=request.url, status=500, request=request)


    def process_response(self, request, response, spider):

        # if spider.name == 'appdetail':
        #     print('==process_response==', response)
        return response