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
    # List of bitstreams
    files = scrapy.Field()
    file_urls = scrapy.Field()

    # METS
    agent_name = scrapy.Field()

    # MODS
    title = scrapy.Field()
    abstract = scrapy.Field()
    author = scrapy.Field()
    date_issued = scrapy.Field()
    language = scrapy.Field()
    identifier = scrapy.Field()
    subject = scrapy.Field()
    publication_type = scrapy.Field()

    # MODS access
    access_condition = scrapy.Field()

    files_added = scrapy.Field()
    files_to_download = scrapy.Field()

    # Special unique hash
    hash = scrapy.Field()

    pass
