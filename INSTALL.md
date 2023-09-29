# Installation instructions

1. Make sure you have Python 3 installed. I also recommend pyenv for virtualenv and version management.
1. Clone this repository with `git clone https://github.com/kshepherd/feed2html.git`
1. Optional: Create or activate a virtualenv with the standard tools or pyenv
1. Install requirements with `pip install -r requirements`
1. Identify the start URL for your DSpace ListRecords OAI verb, eg. https://openaccess.myinstitution.edu/oai/request?verb=ListRecords&metadataPrefix=oai_dc
1. Give the `output/oaidc2html.xsl` stylesheet a quick check to make sure it is 
1. Set up a base directory for your OCFL repository and css files and note the full path
1. Copy or symlink `output/css` to this base directory
1. Begin a crawl! Let's go with that example URL and a base dir of /tmp/site
```
scrapy crawl oaipmh_dc_xml \
   -a url="https://openaccess.myinstitution.edu/oai/request?verb=ListRecords&metadataPrefix=oai_dc" \
   -a website_title="Test" \
   -a website_subtitle="open access research" \
   -a path_to_assets="/tmp/site" \
   -a path_to_ocfl="/tmp/site/repository" \
   -L INFO
```

To test just the first page of the OAI results, uncomment `CLOSESPIDER_ITEMCOUNT` in `feed2html/spiders/oaipmh_dc_xml.py`
