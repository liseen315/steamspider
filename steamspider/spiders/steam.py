# -*- coding: utf-8 -*-
import scrapy


class SteamSpider(scrapy.Spider):
    name = 'steam'
    allowed_domains = ['store.steampowered.com']
    start_urls = ['https://store.steampowered.com/']

    def parse(self, response):
        print(response)
