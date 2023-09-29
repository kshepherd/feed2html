# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Feed2HtmlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    datestamp = scrapy.Field()
    record = scrapy.Field()
    oa_url = scrapy.Field()
    ocfl_id = scrapy.Field()
    html = scrapy.Field()
    pass
