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
    # Publication date - simple DC in OAI often has multiple dc:date values
    # and guessing the publication date is easier to do in Python than in XSLT
    date = scrapy.Field()
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
