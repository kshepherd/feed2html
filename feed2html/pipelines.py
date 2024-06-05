# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import logging
import mimetypes
import shutil
from contextlib import suppress
from pathlib import Path
from scrapy.utils.python import to_bytes

import scrapy.pipelines.files
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
from scrapy.utils.request import referer_str

from feed2html.exporters import MarkdownItemExporter

logger = logging.getLogger(__name__)

def get_file_paths(item):
    prefix = item['hash']
    if len(item['hash']) >= 2:
        prefix = item['hash'][:2]

    file_path = f"{prefix}/{item['hash']}"
    return file_path

class Feed2HtmlPipeline:
    def process_item(self, item, spider):
        return item

class ExportMarkdownPipeline(object):
    def __init__(self):
        self.exporter = None

    def open_spider(self, spider):
        print('Custom export spider opened')

    def process_item(self, item, spider):
        if item is not None:
            file_path = f"/home/kim/projects/feed2html/feed2html/crawls/{get_file_paths(item)}"
            # Opening file in binary-write mode
            os.makedirs(file_path, exist_ok=True)
            file = open(f"{file_path}/metadata.md", 'wb')
            #file = open(f"crawls/test.md", 'wb')
            self.file_handle = file

            # Creating a FanItemExporter object and initiating export
            self.exporter = MarkdownItemExporter(file, fields_to_export=['hash', 'id', 'title',
                                                                         'identifier',
                                                                         'publication_type',
                                                                         'abstract',
                                                                         'date_issued',
                                                                         'subject',
                                                                         'language',
                                                                         'files',
                                                                         ],
                                                 )
            self.exporter.start_exporting()
            logger.info(f"ABOUT TO EXPORT FOR {item['hash']}")
            self.exporter.export_item(item)
            # Ending the export to file from FanItemExport object
            self.exporter.finish_exporting()

        return item

    def close_spider(self, spider):
        print('Custom Exporter closed')



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
                           publication_date=transform.strparam(str(item['date_issued']))
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
        shutil.rmtree(spider.path_to_ocfl)
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
        logging.error("PROCESSING OCFL PIPELINE")
        # Only add if the ID does not already exist.
        # To add versioning, we should compare digests? Or inspect how
        # this is implemented elsewhere.
        # It turns out ocflcore module has not implemented repository.get() or
        # repository.add_version()!! Perhaps look back to zimeon/ocfl-py instead
        # So for now we'll just do a quick directory check instead of
        if not os.path.exists(f"{spider.path_to_ocfl}/root/{item['ocfl_id']}"):
            # Write file contents and digest to new OCFL object and add
            # to the repository
            ocfl_html_file = StreamDigest(BytesIO(item['html']))
            ocfl_xml_file = StreamDigest(BytesIO(bytes(item['xml'], encoding='utf8')))
            v = OCFLVersion(datetime.now(timezone.utc))
            v.files.add("page.html", ocfl_html_file.stream, ocfl_html_file.digest)
            v.files.add("record.xml", ocfl_xml_file.stream, ocfl_xml_file.digest)

            # Handle downloaded files
            for file_added in item['files']:
                full_path = f"{spider.file_crawl_path}/{file_added['path']}"
                bin_file = StreamDigest(open(full_path, 'rb'))
                filepath, filename = os.path.split(file_added['path'])
                logger.warning(f"Adding {filename} file")
                v.files.add(filename, bin_file.stream, bin_file.digest)

            o = OCFLObject(item['ocfl_id'])
            o.versions.append(v)
            self.repository.add(o)

        item.pop('xml', None)
        item.pop('html', None)

        return item

class FilesRelativePipeline(scrapy.pipelines.files.FilesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        media_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        media_ext = Path(request.url).suffix
        # Handles empty and wild extensions by trying to guess the
        # mime type then extension or default to empty string otherwise
        if media_ext not in mimetypes.types_map:
            media_ext = ""
            media_type = mimetypes.guess_type(request.url)[0]
            if media_type:
                media_ext = mimetypes.guess_extension(media_type)

        return f"{get_file_paths(item)}/contents/{media_guid}{media_ext}"
        #return f"{item['ocfl_id']}/contents/{media_guid}{media_ext}"

    def media_downloaded(self, response, request, info, *, item=None):
        referer = referer_str(request)

        if response.status != 200:
            scrapy.logger.warning(
                "File (code: %(status)s): Error downloading file from "
                "%(request)s referred in <%(referer)s>",
                {"status": response.status, "request": request, "referer": referer},
                extra={"spider": info.spider},
            )
            raise scrapy.pipelines.files.FileException("download-error")

        if not response.body:
            logger.warning(
                "File (empty-content): Empty file from %(request)s referred "
                "in <%(referer)s>: no-content",
                {"request": request, "referer": referer},
                extra={"spider": info.spider},
            )
            raise scrapy.FileException("empty-content")

        status = "cached" if "cached" in response.flags else "downloaded"
        logger.debug(
            "File (%(status)s): Downloaded file from %(request)s referred in "
            "<%(referer)s>",
            {"status": status, "request": request, "referer": referer},
            extra={"spider": info.spider},
        )
        self.inc_stats(info.spider, status)

        try:
            path = self.file_path(request, response=response, info=info, item=item)
            checksum = self.file_downloaded(response, request, info, item=item)
        except scrapy.pipelines.files.FileException as exc:
            logger.warning(
                "File (error): Error processing file from %(request)s "
                "referred in <%(referer)s>: %(errormsg)s",
                {"request": request, "referer": referer, "errormsg": str(exc)},
                extra={"spider": info.spider},
                exc_info=True,
            )
            raise
        except Exception as exc:
            logger.error(
                "File (unknown-error): Error processing file from %(request)s "
                "referred in <%(referer)s>",
                {"request": request, "referer": referer},
                exc_info=True,
                extra={"spider": info.spider},
            )
            raise scrapy.pipelines.files.FileException(str(exc))

        # If we made it here, we got OK right?
        file_added = {
            "url": request.url,
            "path": path,
            "checksum": checksum,
            "status": status,
        }

        item['files_added'].append(file_added)

        return file_added

    def item_completed(self, results, item, info):
        with suppress(KeyError):
            ItemAdapter(item)[self.files_result_field] = [x for ok, x in results if ok]
        return item
# bagit
