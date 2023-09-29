# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Feed2HtmlItem(scrapy.Item):
    """
    Simple item model for parsed XML records
    """
    # Identifier
    id = scrapy.Field()
    # Datestamp (usually the crawl datestamp)
    datestamp = scrapy.Field()
    # Original crawled record
    record = scrapy.Field()
    # OA URLs (e.g. Unpaywall search results)
    oa_url = scrapy.Field()
    # Sanitized OCFL identifier
    ocfl_id = scrapy.Field()
    # Transformed HTML
    html = scrapy.Field()
    # Transformed XML
    xml = scrapy.Field()
    pass
