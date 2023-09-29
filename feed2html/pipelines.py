# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from lxml import etree

# OCFL
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

    def process_item(self, item, spider):
        # Transform the XML record to HTML
        xslt_root = etree.parse('output/oaidc2html.xsl')
        transform = etree.XSLT(xslt_root)
        root = etree.XML(item['record'])
        result = transform(root)

        # logging.info("text=%s", result.getroot().text)
        # logging.info(str(result))

        # Save HTML output to the item
        item['html'] = str(result)

        return item


class WriteToOCFLPipeline:

    def open_spider(self, spider):
        spider.repository.initialize()

    def process_item(self, item, spider):
        if not spider.repository.get(item['ocfl_id']):
            ocfl_html_file = StreamDigest(BytesIO(result))
            ocfl_xml_file = StreamDigest(BytesIO(bytes(item['record'], encoding='utf8')))
            v = OCFLVersion(datetime.now(timezone.utc))
            v.files.add("page.html", ocfl_html_file.stream, ocfl_html_file.digest)
            v.files.add("record.xml", ocfl_xml_file.stream, ocfl_xml_file.digest)
            o = OCFLObject(item['ocfl_id'])
            o.versions.append(v)
            spider.repository.add(o)

        return item