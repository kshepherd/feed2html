from typing import Optional, Any

import scrapy
from scrapy.selector import Selector
from feed2html.items import Feed2HtmlItem
import re


class OaipmhDcSpider(scrapy.spiders.XMLFeedSpider):
    """
    Crawl an OAI-PMH XML feed and send the parsed items through configured pipelines
    """
    name = "oaipmh_dc_xml"

    # Sensible default based on typical DSpace OAI PMH feeds
    identifier_xpath = 'oaipmh:header/oaipmh:identifier/text()'
    datestamp_xpath = 'oaipmh:header/oaipmh:datestamp/text()'
    extract_domain_regex = r'https?://([^/]+)'
    allowed_domains = []
    start_urls = []
    namespaces = [
        ('oaipmh', 'http://www.openarchives.org/OAI/2.0/'),
        ('dc', 'http://purl.org/dc/elements/1.1/'),
        ('doc', 'http://www.lyncode.com/xoai')
    ]
    itertag = "oaipmh:record"
    iterator = 'xml'

    # Custom properties for pipelines to access when transforming or rendering documents
    # such as website name, path to assets, path to OCFL repository, etc.
    website_title = 'OAI-PMH Feed'
    website_subtitle = 'open access research'
    path_to_assets = '/tmp'
    # OCFL repository path. 'root' and 'workspace' will be initialized here.
    # Directory will be created if it does not exist.
    path_to_ocfl = '/tmp/ocfl'
    # XSL used in HTML transformation
    path_to_xsl = 'output/oaidc2html.xsl'


    # Set up custom settings and pipelines
    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 1,
        'ITEM_PIPELINES': {
            'feed2html.pipelines.TransformXmlPipeline': 200,
            'feed2html.pipelines.WriteToOCFLPipeline': 900,
        },
    }

    def __init__(self, name: Optional[str] = None,
                 start_url='https://dspace.mit.edu/oai/request?verb=ListRecords&metadataPrefix=oai_dc',
                 tag='oaipmh:record',
                 website_title='OAI-PMH Feed',
                 website_subtitle='open access research',
                 path_to_assets='/tmp',
                 path_to_ocfl='/tmp/ocfl',
                 path_to_xsl='output/oaidc2html.xsl',
                 **kwargs: Any):
        """
        Initialize this spider, setting some custom parameters from the command line to make it more reusable
        CLI arguments are set with `-a <arg>=<value>` when running scrapy crawl on this spider

        :param name: spider name
        :param start_url: Start URL (OAI ListRecords verb)
        :param tag: The tag name to use for itertag
        :param kwargs: kwargs pointer
        """
        # Set a single start URL
        self.start_urls = [f'{start_url}']
        # Set the allowed domains from the start URLs
        self.allowed_domains = re.findall(self.extract_domain_regex, start_url)
        # Set the itertag (used by XMLSpider)
        self.itertag = tag
        # Set the website title and subtitle
        self.website_title = website_title
        self.website_subtitle = website_subtitle
        # Set up paths to assets (css and so on), XSL and OCFL repo
        self.path_to_assets = path_to_assets
        self.path_to_ocfl = path_to_ocfl
        self.path_to_xsl = path_to_xsl
        # Continue with superclass initialization
        super().__init__(name, **kwargs)

    def parse_node(self, response, node):
        """
        Parse the XML node for a single OAI record
        :param response: the HTTP response
        :param node: the current XML node
        :return: constructed item to send to pipelines
        """
       # self.logger.info("thing=%s", node.xpath(self.identifier_xpath).get())

        item = Feed2HtmlItem()
        item['id'] = node.xpath(self.identifier_xpath).extract()
        item['datestamp'] = node.xpath(self.datestamp_xpath).get()
        item['xml'] = node.xpath('.').get()
        # Sanitise OAI identifier so that it is a valid FS directory name
        # You might need to change this based on your own requirements and FS used
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

