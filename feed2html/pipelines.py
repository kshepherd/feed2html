# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import logging

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

# XML and XSLT handling
from lxml import etree

# File handling
import os

# OCFL imports
from datetime import datetime, timezone
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


class Feed2HtmlPipeline:
    def process_item(self, item, spider):
        return item


class TransformXmlPipeline:
    """
    Simple pipeline that handles XSLT. The initial use case was generating HTML pages for a static
    website but this pipeline could easily be repurposed or extended to do XML-to-XML, etc...
    """

    def process_item(self, item, spider):
        # Transform the XML record to HTML
        xslt_root = etree.parse(spider.path_to_xsl)
        transform = etree.XSLT(xslt_root)
        root = etree.XML(item['xml'])
        result = transform(root,
                           website_title=transform.strparam(spider.website_title),
                           website_subtitle=transform.strparam(spider.website_subtitle),
                           path_to_assets=transform.strparam(spider.path_to_assets),
                           publication_date=transform.strparam(str(item['date']))
                           )

        # logging.info("text=%s", result.getroot().text)
        # logging.info(str(result))

        # Save HTML output to the item
        item['html'] = result

        return item


class WriteToOCFLPipeline:
    """
    Write item output to an OCFL repository using the standard ocflcore Python library.
    Make sure this pipeline is processed after all files have been transformed and saved
    to the item
    OCFL module documentation: https://ocflcore.readthedocs.io/
    """
    # OCFL repository
    repository = None

    def open_spider(self, spider):
        """
        When the spider is opened, initialise the OCFL repository
        TODO: Investigate if calling initialize on existing repository is dangerous
        :param spider: the spider supplying items to this pipeline
        :return: None
        """
        # Create OCFL repo directory if necessary
        os.makedirs(spider.path_to_ocfl, exist_ok=True)

        # OCFL properties
        ocfl_root = StorageRoot(TopLevelLayout())
        storage = FileSystemStorage(f"{spider.path_to_ocfl}/root")
        workspace_storage = FileSystemStorage(f"{spider.path_to_ocfl}/workspace")
        # Instantiate and initialize the OCFL repository
        self.repository = OCFLRepository(ocfl_root, storage, workspace_storage=workspace_storage)
        self.repository.initialize()

    def process_item(self, item, spider):
        """
        Process the item. Byte streams of the file contents and digests are
        created and added to a new object, unless it exists.
        TODO: Versioning (not yet impl in ocfl module)
        TODO: Proper "get object by ID" check (not yet impl in ocfl module)
        :param item: the item being processed
        :param spider: spider (access to per-spider settings and objects)
        :return: item
        """
        # Only add if the ID does not already exist.
        # To add versioning, we should compare digests? Or inspect how
        # this is implemented elsewhere.
        # It turns out ocflcore module has not implemented repository.get() or
        # repository.add_version()!! Perhaps look back to zimeon/ocfl-py instead
        # So for now we'll just do a quick directory check instead of
        # if not self.repository.get(item['ocfl_id']):
        if not os.path.exists(f"{spider.path_to_ocfl}/root/{item['ocfl_id']}"):
            # Write file contents and digest to new OCFL object and add
            # to the repository
            ocfl_html_file = StreamDigest(BytesIO(item['html']))
            ocfl_xml_file = StreamDigest(BytesIO(bytes(item['xml'], encoding='utf8')))
            v = OCFLVersion(datetime.now(timezone.utc))
            v.files.add("page.html", ocfl_html_file.stream, ocfl_html_file.digest)
            v.files.add("record.xml", ocfl_xml_file.stream, ocfl_xml_file.digest)
            o = OCFLObject(item['ocfl_id'])
            o.versions.append(v)
            self.repository.add(o)

        return item
