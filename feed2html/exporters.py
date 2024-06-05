from io import BytesIO

from scrapy.exporters import BaseItemExporter
from scrapy.utils.serialize import ScrapyJSONEncoder
from scrapy.utils.python import to_bytes
import frontmatter
import yaml

class MarkdownItemExporter(BaseItemExporter):
    def __init__(self, file, **kwargs):
        self._configure(kwargs, dont_fail=True)
        self.file = file
        #self.encoder = ScrapyJSONEncoder(**kwargs)
        self.first_item = True

    def start_exporting(self):
        pass

    def finish_exporting(self):
        pass

    def export_item(self, item):
        self.file.write(to_bytes('---\n', self.encoding))
        self.file.write(to_bytes(yaml.dump(
            dict(self._get_serialized_fields(item, include_empty=False))), self.encoding))
        self.file.write(to_bytes('---\n', self.encoding))
