# feed2html
Generate static HTML sites using specifications like OCFL and Bagit from various feed formats like OAI-PMH, RSS. Part of a suite of **static HTML repository tools**.

## Introduction

This project was inspired by Professor Hussein Suleman (University of Cape Town), who gave a rousing closing keynote at Open Repositories 2023 about what really makes an open access repository *accessible*, and a call to reduce complexity in digital repository/library development.

Rather than re-invent a whole repository platform, this tool is one step in that direction: using existing protocols that have served us well for years (OAI-PMH and RSS), we can harvest existing repositories on the web, no matter how complex they happen to be, and produce our own simple, file-based repositories using standards and simple document formats like HTML.


## Quick start

Right now, the tool is only tested on DSpace OAI-PMH feeds using the oai_dc (simple Dublin Core elements) metadata format.

1. Make sure you have Python 3 installed. I also recommend pyenv for virtualenv and version management.
1. Clone this repository with `git clone https://github.com/kshepherd/feed2html.git`
1. **Optional**: Create or activate a virtualenv with the standard tools or pyenv
1. Install requirements with `pip install -r requirements.txt`
1. Identify the start URL for your DSpace ListRecords OAI verb, eg. https://openaccess.myinstitution.edu/oai/request?verb=ListRecords&metadataPrefix=oai_dc
1. Give the `output/oaidc2html.xsl` stylesheet a quick check to make sure it is transforming the fields you're interested in
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

## Customising

1. Take a look at the `parse_record` method in `feed2html/spiders/oaipmh_dc_xml.py` to see how the simple item objects are constructed. This can be extended the same way as any other scrapy XML feed spider
1. If the spider does not properly follow resumption tokens (to get the next page), run the crawl in debug mode with `-L DEBUG` and compare the expected XML with the token extraction in `parse_node`

## Tools and methodologies

[Python 3](https://www.python.org/) is a popular, accessible language and is widely used by researchers, librarians and other open access practitioners.

[Scrapy](https://scrapy.org/) is a well-supported, extensible Python module which can scrape web resources and process the results through pipelines, allowing a lot of customisation while leaving the low-level HTTP, document parsing work to an existing framework which has its own open source community and can easily be extended for more advanced solutions.

The [Oxford Common File Layout (OCFL)](https://ocfl.io/) specification describes an application-independent approach to the storage of digital information in a structured, transparent, and predictable manner. It is designed to promote long-term object management best practices within digital repositories. 

[Extensible Stylesheet Language Transformations (XSLT)](https://developer.mozilla.org/en-US/docs/Web/XSLT) is an XML-based language used, in conjunction with specialized processing software, for the transformation of XML documents. It has long been popular in the library sector.

## Goals

- Turn feeds (OAI, RSS/Atom, ActivityPub) into complete static websites
    - "Put DSpace on a CD-ROM"
- Start with most basic requirements
-- OAIPMH, Dublin Core elements and terms
-- RSS 2.0 for blogs, podcasts
-- (RDF, jsonld, other formats and protocols come later)

## TODO

1. Spider
   1. [x] Build OCFL layer
   1. [x] Read XML feed with resumption tokens
1. Pipelines:
   1. [x] Initialize OCFL repository on disk
   2. [ ] Create BagIt fs structure (simpler alternative to OCFL)
   1. [ ] Search OA services (unpaywall etc) for OA links
   1. [x] Transform to HTML with XSLT
   1. [x] Create OCFL object and version and add to repository
   1. [ ] Send to search index (solr, ES, zincsearch?)
1. Documentation
   1. [ ] Complete pydoc coverage
   1. [x] Installation and usage instructions
   1. [ ] Complete this README with thorough explanation of the spider and pipelines, and advanced usage instructions
1. Release
   1. [x] Create requirements.txt and INSTALL.md
   2. [x] Create LICENSE.txt for BSD 3-Clause license.
   1. [ ] Release to PyPI (or figure out the best way to package and distribute releases) once the project is beyond prototype

## Notes

See [NOTES.md](NOTES.md) for informal notes, ideas, links, references. 