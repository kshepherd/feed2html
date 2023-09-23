import scrapy
from scrapy.http import Request
from scrapy.http import Response
from scrapy.selector import Selector
from feed2html.items import Feed2HtmlItem


class OaipmhDcSpider(scrapy.Spider):
    name = "oaipmh_dc"
    allowed_domains = ["dspace.mit.edu"]
    start_urls = ["https://dspace.mit.edu/oai/request?verb=ListRecords&metadataPrefix=oai_dc"]
    custom_settings = {
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'CLOSESPIDER_PAGECOUNT': 1
    }

    def parse(self, response: Response, **kwargs):
        # self.logger.info(
        #     "Hi, this is a <%s> node!: %s", self.itertag, "".join(node.getall())
        # )
        self.logger.info("thing=%s",response)
        self.logger.info(response.xpath('//record/header/identifier/text()').getall())

        item = Feed2HtmlItem()
        #self.logger.info(node.xpath('.'))
        item['id'] = response.xpath('header/identifier').extract()
        item['datestamp'] = response.xpath('header/datestamp').get()
        item['metadata'] = response.xpath('metadata').get()
        return item

    def test(self, response):
        """
        We use this special method as our item validation test so we can use scrapy check
        as part of our test-driven development process

        @url https://dspace.mit.edu/oai/request?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:dspace.mit.edu:1721.1/126771
        @returns items 1 1
        @returns requests 0 0
        @scrapes id
        @scrapes datestamp
        """
        # Adapt this response to a TextReponse and create an XML node
        response = self.adapt_response(response)
        node = Selector(response, type="xml")
        # Return the actual parsed item from the check response
        return self.parse_node(response, node)

