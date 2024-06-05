import hashlib

import pytz
from dateutil.parser import parse, ParserError
from typing import Optional, Any

import scrapy
from scrapy import Request
from scrapy.selector import Selector
from scrapy.utils.python import to_bytes

from feed2html.items import Feed2HtmlItem
import re


class MetsModsXml(scrapy.spiders.XMLFeedSpider):
    """
    Crawl an OAI-PMH XML feed and send the parsed items through configured pipelines
    Assumeing METS wrapper with MODS metadata
    """
    name = "mets"

    # Sensible default based on typical DSpace OAI PMH feeds
    identifier_xpath = 'oaipmh:header/oaipmh:identifier/text()'
    datestamp_xpath = 'oaipmh:header/oaipmh:datestamp/text()'

    extract_domain_regex = r'https?://([^/]+)'
    allowed_domains = []
    url = None
    start_urls = []
    namespaces = [
        ('oaipmh', 'http://www.openarchives.org/OAI/2.0/'),
        ('dc', 'http://purl.org/dc/elements/1.1/'),
        ('doc', 'http://www.lyncode.com/xoai'),
        ('mods', 'http://www.loc.gov/mods/v3'),
        ('mets', 'http://www.loc.gov/METS/'),
        ('premis', 'http://www.loc.gov/standards/premis')
    ]
    resumption_xpath = "//oaipmh:resumptionToken"
    record_xpath = "//oaipmh:record"
    premis_xpath = ".//premis:object"
    mods_xpath = ".//mods:mods"
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
    path_to_xsl = 'output/oaimets2html.xsl'

    file_crawl_path = '/tmp/crawls/'


    # Set up custom settings and pipelines
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'MEDIA_ALLOW_REDIRECTS': True,
        'FILES_STORE': file_crawl_path,
        #'CLOSESPIDER_PAGECOUNT': 1,
        #'CLOSESPIDER_ITEMCOUNT': 1,
        'ITEM_PIPELINES': {
            #'feed2html.pipelines.TransformXmlPipeline': 200,
            #'feed2html.pipelines.WriteToOCFLPipeline': 900,
            #'scrapy.pipelines.files.FilesPipeline': 1000
            'feed2html.pipelines.FilesRelativePipeline': 300,
            'feed2html.pipelines.ExportMarkdownPipeline': 400
        },
    }

    def __init__(self, name: Optional[str] = None,
                 url='https://your.repository.here/oai/request?verb=ListRecords&metadataPrefix=mets&set=com_123456789_1',
                 tag='oaipmh:OAI-PMH',
                 website_title='OAI-PMH Feed',
                 website_subtitle='open access research',
                 path_to_assets='/tmp',
                 path_to_ocfl='/tmp/ocfl',
                 path_to_xsl='output/oaimets2html.xsl',
                 file_crawl_path=file_crawl_path,
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

        self.file_crawl_path = file_crawl_path

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
        i = 0
        for record in records:
            if i < 10:
                yield self.parse_record(response, record)
            i = i + 1

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
        item['files_added'] = []
        item['id'] = node.xpath(self.identifier_xpath).get()
        item['datestamp'] = node.xpath(self.datestamp_xpath).get()

        # Sanitise OAI identifier so that it is a valid FS directory name
        # You might need to change this based on your own requirements and FS used
        item['ocfl_id'] = re.sub(r'[/:, ]', '_', str(item['id']))

        # METS Agent (org) name
        item['agent_name'] = node.xpath('.//mets:agent/mets:name/text()').get()

        # MODS basic metadata
        item['title'] = node.xpath('.//mods:title/text()').get()
        item['date_issued'] = node.xpath('.//mods:dateIssued/text()').get()
        item['abstract'] = node.xpath('.//mods:abstract/text()').get()
        item['identifier'] = node.xpath('.//mods:identifier/text()').extract()
        item['language'] = node.xpath('.//mods:language/mods:languageTerm/text()').get()
        item['publication_type'] = node.xpath('.//mods:genre/text()').get()

        item['access_condition'] = node.xpath('.//mods:accessCondition/text()').get()

        premis_objects = []
        files = []
        for premis_object in node.xpath(self.premis_xpath):
            premis_uri = premis_object.xpath('.//premis:objectIdentifierValue/text()').get()
            premis_size = premis_object.xpath('.//premis:size/text()').get()
            premis_md5 = premis_object.xpath('.//premis:fixity/premis:messageDigest/text()').get()
            premis_format = premis_object.xpath('.//premis:format/premis:formatDesignation/premis:formatName/text()').get()
            object = {
                'uri': premis_uri,
                'size': premis_size,
                'md5': premis_md5,
                'format': premis_format
            }
            premis_objects.append(object)

        # PREMIS might not be implemented everywhere, so also get fileSec/fileGrp
        if len(premis_objects) == 0:
            for fileGrp in node.xpath(".//fileSec/fileGrp[@USE='ORIGINAL' or @USE='reference']"):
                # Filter out any unwanted groups here? DSpace uses 'ORIGINAL', Eprints 'reference' for main files
                # and dspace uses 'TEXT' for full text
                for file in fileGrp.xpath(".//file"):
                    files.append({
                        'uri': file.xpath("FLocat[LOCTYPE='URL']").attrib('xlink:href').get(),
                        'size': file.attrib('SIZE').get(),
                        'md5': file.attrib('CHECKSUM').get(),
                        'format': file.attrib('MIMETYPE').get()
                    })
            item['files_to_download'] = files
        else:
            item['files_to_download'] = premis_objects

        item['file_urls'] = []
        for file in item['files_to_download']:
            item['file_urls'].append(file['uri'])

        # Finally store the entire XML object if we want - e.g. to pass to XSLT
        item['xml'] = node.xpath('.').get()

        # Finally finally, hash something about the item to use as a local ID / file path prefix
        item_hash = hashlib.sha1(to_bytes(item['id'])).hexdigest()
        item['hash'] = item_hash

        # Other spiders use yield here, but it screwed up our data handling (the 1996 date ending up in many items etc)
        # so we are using the more straight-forward return here, to process things in strict order and return
        # the item instead of a generator.
        return item

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

