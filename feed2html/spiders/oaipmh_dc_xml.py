from typing import Optional, Any

import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from feed2html.items import Feed2HtmlItem
import re
from io import BytesIO
from ocflcore import (
    FileSystemStorage,
    OCFLRepository,
    OCFLObject,
    OCFLVersion,
    StorageRoot,
    StreamDigest,
    TopLevelLayout,
)

class OaipmhDcSpider(scrapy.spiders.XMLFeedSpider):
    name = "oaipmh_dc_xml"
    allowed_domains = ["dspace.mit.edu"]
    start_urls = ["https://dspace.mit.edu/oai/request?verb=ListRecords&metadataPrefix=oai_dc"]
    namespaces = [
        ('oaipmh', 'http://www.openarchives.org/OAI/2.0/'),
        ('dc', 'http://purl.org/dc/elements/1.1/'),
        ('doc', 'http://www.lyncode.com/xoai')
    ]
    iterator = 'xml'
    #iterator = 'xml'
    itertag = "oaipmh:record"
    custom_settings = {
        #'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'CLOSESPIDER_PAGECOUNT': 1,
        'ITEM_PIPELINES': {
                'feed2html.pipelines.TransformXmlPipeline': 900,
        },
    }
    # OCFL properties
    ocfl_root = StorageRoot(TopLevelLayout())
    storage = FileSystemStorage("root")
    workspace_storage = FileSystemStorage("workspace")
    repository = OCFLRepository(ocfl_root, storage,
                                workspace_storage=workspace_storage)

    def __init__(self, name: Optional[str] = None, **kwargs: Any):
        super().__init__(name, **kwargs)

    def parse_node(self, response, node):
        # self.logger.info(
        #     "Hi, this is a <%s> node!: %s", self.itertag, "".join(node.getall())
        # )

       # self.logger.info("thing=%s", node.xpath('oaipmh:header/oaipmh:identifier/text()').get())

        item = Feed2HtmlItem()
        #self.logger.info(node.xpath('.'))
        item['id'] = node.xpath('oaipmh:header/oaipmh:identifier/text()').extract()
        item['datestamp'] = node.xpath('oaipmh:header/oaipmh:datestamp/text()').get()
        item['record'] = node.xpath('.').get()
        item['ocfl_id'] = re.sub(r'[/:, ]', '_', str(item['id'][0]))
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

