# -*- coding: utf-8 -*-

# Scrapy settings for steamspider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'steamspider'

SPIDER_MODULES = ['steamspider.spiders']
NEWSPIDER_MODULE = 'steamspider.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'steamspider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 5
# RANDOMIZE_DOWNLOAD_DELAY = True
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'steamspider.middlewares.SteamspiderSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'steamspider.middlewares.SteamspiderDownloaderMiddleware': 543,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    # 'steamspider.middlewares.SeleniumMiddleware': 401,

}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'scrapy_redis.pipelines.RedisPipeline': 300
    'steamspider.pipelines.MySQLPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# ----------- scrapy redis 参数配置 -------------
SCHEDULER = "scrapy_redis.scheduler.Scheduler"      #启用redis的调度器

SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'

DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"      #redis去重
REDIS_URL = 'redis://:@127.0.0.1:6379'         #redis本地url

REDIS_PARAMS  = {}
# Use custom redis client class.
REDIS_PARAMS['db'] = '2'

SCHEDULER_PERSIST = True

SCHEDULER_FLUSH_ON_START = True

#
# # ----------- selenium 参数配置 -------------
# SELENIUM_TIMEOUT = 25           # selenium浏览器的超时时间，单位秒
# LOAD_IMAGE = False               # 是否下载图片
# WINDOW_HEIGHT = 900             # 浏览器窗口大小
# WINDOW_WIDTH = 900

# LOG_STDOUT = True  开启这个会导致部署出现找不到spider的bug
LOG_LEVEL = 'INFO'
