from scrapy import Spider, Request
from steamspider.items import PopularNewsItem
import math
import time
from .topsellers import TopSellersSpider

class PopularNewSpider(TopSellersSpider):
    name = 'poplularnew'
    allowed_domains = ['store.steampowered.com']

    def __init__(self, *args, **kwargs):
        super(PopularNewSpider, self).__init__(*args, **kwargs)
        self.page_url = 'https://store.steampowered.com/search/results?l=schinese&filter=popularnew&sort_by=Released_DESC&category1=998,21,10'

    def create_item(self):
        return PopularNewsItem()
