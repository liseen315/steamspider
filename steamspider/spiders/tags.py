from scrapy import Spider, Request
from steamspider.items import TagsItem


class TagSpider(Spider):
    name = 'apptags'
    allowed_domains = ['store.steampowered.com']

    def __init__(self, *args, **kwargs):
        super(TagSpider, self).__init__(*args, **kwargs)

        self.page_url = 'https://store.steampowered.com/search/?l=schinese&category1=998,21,10'
        self.current_pagenum = 1
        self.total_apps = None
        self.total_pagenum = None
        self.search_url = '{url}&page={pagenum}'

    def start_requests(self):
        yield Request(url=self.search_url.format(url=self.page_url, pagenum=self.current_pagenum),
                      callback=self.parse_tags)

    def parse_tags(self, response):
        tag_list = response.xpath('//div[contains(@data-param,"tags")]')
        for tag_item in tag_list:
            item = TagsItem()
            item['tag_name'] = tag_item.xpath('@data-loc').extract_first()
            item['tag_value'] = tag_item.xpath('@data-value').extract_first()
            yield item
