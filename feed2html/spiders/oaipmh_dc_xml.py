import pytz
from dateutil.parser import parse, ParserError
from typing import Optional, Any

import scrapy
from scrapy import Request
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
    publication_date_xpath = './/dc:date/text()'

    extract_domain_regex = r'https?://([^/]+)'
    allowed_domains = []
    url = None
    start_urls = []
    namespaces = [
        ('oaipmh', 'http://www.openarchives.org/OAI/2.0/'),
        ('dc', 'http://purl.org/dc/elements/1.1/'),
        ('doc', 'http://www.lyncode.com/xoai')
    ]
    resumption_xpath = "//oaipmh:resumptionToken"
    record_xpath = "//oaipmh:record"
    itertag = "oaipmh:OAI-PMH"
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
        'ROBOTSTXT_OBEY': False,
        #'CLOSESPIDER_PAGECOUNT': 1,
        #'CLOSESPIDER_ITEMCOUNT': 1,
        'ITEM_PIPELINES': {
            'feed2html.pipelines.TransformXmlPipeline': 200,
            'feed2html.pipelines.WriteToOCFLPipeline': 900,
        },
    }

    def __init__(self, name: Optional[str] = None,
                 url='http://localhost:4000/oai/request?verb=ListRecords&metadataPrefix=oai_dc',
                 tag='oaipmh:OAI-PMH',
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
        self.url = url
        self.start_urls = [f'{url}']
        # Set the allowed domains from the start URLs
        self.allowed_domains = re.findall(self.extract_domain_regex, url)
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
        Parse the main OAI-PMH node. We need to access the resumptionToken here which
        is why we do not simply specify oaipmh:record as our itertag and parse that way.
        The oaipmh:records are selected with xpath and then sent off to parse_record while a new request
        to the resumptionToken is also yielded

        :param response: http response
        :param node: root OAIPMH node
        :return:
        """
        records = node.xpath(f"{self.record_xpath}")
        resumption = node.xpath(f"{self.resumption_xpath}")
        size = resumption.xpath("./@completeListSize").get()
        self.logger.debug(f"completeListSize={size}")
        token = resumption.xpath("./text()").get()
        self.logger.debug(f"resumptionToken={token}")
        url = self.url.replace('&metadataPrefix=oai_dc', '')
        req = Request(f"{url}&resumptionToken={token}", callback=self._parse)

        for record in records:
            yield self.parse_record(response, record)
        yield req

    def parse_record(self, response, node):
        """
        Parse the XML node for a single OAI record
        There is not too much to do here, as the XSL stylesheet will handle most fields and values
        within the record. However, there are some things that are nice to handle in Python at this level
        such as dates, links to other resources, and so on.

        :param response: the HTTP response
        :param node: the current XML node
        :return: constructed item to send to pipelines
        """
        item = Feed2HtmlItem()
        item['id'] = node.xpath(self.identifier_xpath).extract()
        item['datestamp'] = node.xpath(self.datestamp_xpath).get()
        # Although we let XSLT handle all the other metadata fields directly, we know from experience
        # that dc:date in simple DC from DSpace can be an issue if the repository doesn't do its own
        # handling to reduce them down to a single publication date. Also, we might want some more powerful
        # parsing and formatting of date strings, and this is a lot easier to do in Python.
        # So, we have a static function that will try to guess and format the best date.
        # It will be passed to the XSLT as a parameter
        item['date'] = self.guess_date(node.xpath(self.publication_date_xpath).extract(), item['id'])
        item['xml'] = node.xpath('.').get()
        # Sanitise OAI identifier so that it is a valid FS directory name
        # You might need to change this based on your own requirements and FS used
        item['ocfl_id'] = re.sub(r'[/:, ]', '_', str(item['id'][0]))

        # Other spiders use yield here, but it screwed up our data handling (the 1996 date ending up in many items etc)
        # so we are using the more straight-forward return here, to process things in strict order and return
        # the item instead of a generator.
        return item

    def guess_date(self, dates, identifier):
        """
        Parse a date from a list of dc:date values, and guess which one might be the publication date

        :param dates: list of dates
        :param identitier: used for logging date errors which can be helpful in metadata validation
        :return: formatted date
        """
        parsed_dates = list()
        if isinstance(dates, list):
            for date in dates:
                if len(date) == 4:
                    # A date which is just a year, is probably what we are looking for.
                    return date
                # Parse the date string to a datetime object
                try:
                    parsed_date = parse(date).replace(tzinfo=pytz.UTC)
                    if parsed_date is not None:
                        parsed_dates.append(parsed_date)
                except ParserError as error:
                    self.logger.error(f"Could not parse date: {error}")
                    if date is not None and len(date) > 4:
                        try:
                            # Hm, ok, we will just extract the first 4 consecutive numbers we see
                            # and call it a date
                            year_guess = re.search(r'[0-9]{4}', date)
                            if year_guess is not None and year_guess.group():
                                parsed_date = parse(year_guess.group()).replace(tzinfo=pytz.UTC)
                                if parsed_date is not None:
                                    parsed_dates.append(parsed_date)
                        except ParserError as second_error:
                            # OK, give up and skip this date
                            self.logger.error(f"Could not parse partial date: {identifier}")

        best_guess = None

        if len(parsed_dates) > 0:
            # Get the earliest date
            best_guess = min(parsed_dates)

        if best_guess is not None:
            # Return just the year in this simple example
            return best_guess.strftime("%Y")

        return "Unknown date"

    def test(self, response):
        """
        We use this special method as our item validation test so we can use scrapy check
        as part of our test-driven development process
        TODO: This test needs rewriting to support the new root node parsing, and a reference to a live site was removed

        @url https://localhost/oai/request?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:localhost:1234
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

