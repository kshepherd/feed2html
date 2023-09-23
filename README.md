# feed2html
Generate static HTML sites from various feed formats like OAI-PMH, RSS

## Introduction

This project was inspired by Professor Hussein Suleman (University of Cape Town), who gave a rousing closing keynote at Open Repositories 2023 about what really makes an open access repository *accessible*.

An OCFL implementation in Python is a secondary goal

## Tools and methodologies

Python is a popular, accessible language and is widely used by researchers, librarians and other open access practitioners.

Scrapy is a well-supported, extensible Python module which can scrape web resources and process the results through pipelines, allowing a lot of customisation while leaving the low-level HTTP, document parsing work to an existing framework which has its own open source community and can easily be extended for more advanced solutions.

## Goals

- Turn feeds (OAI, RSS/Atom, ActivityPub) into complete static websites
    - "Put DSpace on a CD-ROM"
- Start with most basic requirements
-- OAIPMH, Dublin Core elements and terms
-- RSS 2.0 for blogs, podcasts
-- (RDF, jsonld, other protocols come later)

1. Build OCFL layer
1. Read XML feed with any resumption tokens/last page/oldest date params
1. Pipelines:
   1. Create OCFL fs structure
   1. Search OA services (unpaywall etc) for OA links
   1. Transform to HTML with XSLT and write to disk
   1. Create manifest, other final things for OCFL
   1. Send to index (solr, ES, zincsearch)?
   1. Build HTML pages with XSL
1. Documentation
   1. Continue updating README as development progresses
   1. Walkthrough of installation and usage instructions
1. Release
   1. Create requirements.txt and INSTALL.md
   1. Release to PyPI once project is beyond prototype

## Notes

Initial prototypes of this project use DSpace OAI feeds to try and collate open access metadata records and convert to a static HTML catalogue. Unfortunately it is hard to get really good metadata, or file links this way but I'm going with a "basics first" approach. METS is ideal.

With a directory structure (even if it is not OCFL to begin with) of well-formatted HTML files, users can use normal file search tools to work with the whole set offline.

Index HTML can be generated, including simple browse pages that offer lists of documents by author, title, subject, etc.

Of the typical DSpace metadata formats, METS is probably the best - it provides manifest, acce
ss conditions, metadata, etc.

However, starting with oai_dc DSpace for now to get some HTML to look at and play with

### Search

Perhaps a better alternative to a search engine pipeline is a separate tool which iterates an OCFL root and indexes to solr. This means we can take advantage of the manifest and do full text extraction, with the extracted text being inserted into the same solr doc as the record, etc.

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
