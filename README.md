# feed2html
Generate static HTML sites using specifications like OCFL and Bagit from various feed formats like OAI-PMH, RSS. Part of a suite of **static HTML repository tools**.

## Introduction

This project was inspired by Professor Hussein Suleman (University of Cape Town), who gave a rousing closing keynote at Open Repositories 2023 about what really makes an open access repository *accessible*, and a call to reduce complexity in digital repository/library development.

Rather than re-invent a whole repository platform, this tool is one step in that direction: using existing protocols that have served us well for years (OAI-PMH and RSS), we can harvest existing repositories on the web, no matter how complex they happen to be, and produce our own simple, file-based repositories using standards and simple document formats like HTML.


## Quick start

Right now, the tool is only tested on DSpace OAI-PMH feeds using the oai_dc (simple Dublin Core elements) metadata format.

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
   2. [ ]
   1. [x] Installation and usage instructions
   1. [ ] Complete this README with thorough explanation of the spider and pipelines, and advanced usage instructions
1. Release
   1. [x] Create requirements.txt and INSTALL.md
   2. [x] Create LICENSE.txt for BSD 3-Clause license.
   1. [ ] Release to PyPI (or figure out the best way to package and distribute releases) once the project is beyond prototype

## Notes

Initial prototypes of this project use DSpace OAI feeds to try and collate open access metadata records and convert to a static HTML catalogue. Unfortunately it is hard to get really good metadata, or file links this way but I'm going with a "basics first" approach. METS is ideal.

With a directory structure (even if it is not OCFL to begin with) of well-formatted HTML files, users can use normal file search tools to work with the whole set offline.

Index HTML can be generated, including simple browse pages that offer lists of documents by author, title, subject, etc.

Of the typical DSpace metadata formats, METS is probably the best - it provides manifest, acce
ss conditions, metadata, etc.

However, starting with oai_dc DSpace for now to get some HTML to look at and play with

RDF/metadata in HTML: https://www.w3.org/2001/sw/RDFCore/20031212-rdfinhtml/ (currently leaning toward link rel (schema) and meta elements in html head, like DSpace does, for a simple and tried+true approach which search engines also tend to understand)

### Python OCFL:
https://github.com/zimeon/ocfl-py  https://pypi.org/project/ocfl-py/ 
https://github.com/inveniosoftware/ocflcore
https://github.com/OCFL/spec/wiki/Implementations
https://ocflcore.readthedocs.io/en/latest/

I am using ocflcore but it is only partially implemented. We really want repository.get() and repository.add_version()!!

### Search

Still thinking about different ways to do search.

At the conference talk, it was noted that most modern computers and browsers can happily handle a lot of text and use the meta-F built-in search to find things in an index page! Keep it simple...

What's more, most operating systems or file managers can search over the whole directory structure, including fulltext search of some document formats.

However, it would be nice to use Solr, too, for a bit of extra power. It would not be hard to include in a portable repository, but running it would require a few extra steps, user permissions,  and host machine dependencies. It would mean a bit of javascript (to run the search bar) and a bundled jar or something.

(is generating some HTML search controls with client-side javascript considered "static HTML"?)

Documents can be sent to the search engine in a new Scrapy pipeline.

An alternative to a search engine pipeline is a separate tool which iterates an OCFL root and indexes to solr. This means we can take advantage of the manifest and do full text extraction, with the extracted text being inserted into the same solr doc as the record, etc.

### Pipelines vs post-crawl tools

An alternative to a search engine pipeline is a separate tool which iterates an OCFL root and indexes to solr. This means we can take advantage of the manifest and do full text extraction, with the extracted text being inserted into the same solr doc as the record, etc.

Generating index HTML pages (eg browse by title/subject/year/author) and a landing page would also be a tool run over the repository dir once crawl is complete.

### Metadata validation

As usual, any OAI harvester implementation accidentally turns into a tool that also validates metadata! We can produce reports for post-crawl analysis.

### PDF (and other doc) handling

Processing files: 
https://docs.scrapy.org/en/latest/topics/media-pipeline.html for processing files

### Enhancing with OA links / files

Unpaywall and OpenAlex take 100k API calls per day. This might be OK, the alternative is to d
ownload and put into a data warehouse.

### Tests

* Scrapy Unit Testing (stackoverflow):
    * https://docs.scrapy.org/en/latest/topics/contracts.html
    * https://stackoverflow.com/questions/6456304/scrapy-unit-testing
