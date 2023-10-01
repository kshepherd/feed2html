# Notes

This page is an informal collection of thoughts, ideas, notes, links to keep the README nice and tidy

## Use cases

### Simple catalogue or collection from existing repo

This was the first thing I thought of when thinking "DSpace on a CDROM"

### Cultural heritage

Collections and exhibitions of images or other media is an obvious candidate for static websites since the delivery works really well with simple HTML, and public libraries and museums often don't have big budgets for running digital library systems.

Exhibitions in particular have very specific requirements and need to be created from a larger set of existing resources/records and then preserved.

https://minicomp.github.io/wiki/wax/ is another static website project for collections and exhibitions

### Dataset as website

pt has done some work with this in the ROCrate tools using popular unix tools to produce websites. I think this is a cool example compared to eg. a datasets collection or catalogue because the static customisable website makes sense where the researcher or curator is able to produce something that works for a specific dataset and doesn't need to be tied to any other RDM systems

### Simple publication repositories

One of the first use cases I had in mind while developing feed2html, just because it's closest to my current dayjob and is usually what sits behind OAI feeds.

However, harder to pitch to institutions since they are probably already tied into complex digital repositories and workflows, and I don't see any real demand for simple solutions from universities at least - but council libraries or small research groups may be interested.

## Post-crawl pipelines

Obviously, nobody wants to perform another OAI-PMH harvest or web crawl just because they have updated the XSLT or other HTML template parts... so we can have a nice wrapper for standard XSLT over the files.

Should we then even bother to do HTML at the point of the feed? Uh oh, maybe I named this thing too hastily.

It is easy to come  up with a wishlist of transformation tools ti sticki into their own pipeline, which would be either outside scrapy, or in a (counter-intuitive?) scrapy spider that only "crawls" (ie processes) the OCFL back from disk.

* Generating index HTML pages to support browse, galleries, collections
* Media format transformation
* Fulltext extraction from doc
* Thumbnail generation for images, videos, documents
* IIIF manifest and tile generation
* json-ld / RDF generation to describe linked resources

Processing files: 
https://docs.scrapy.org/en/latest/topics/media-pipeline.html for processing files

Unpaywall and OpenAlex take 100k API calls per day. This might be OK, the alternative is to d
ownload and put into a data warehouse.

## Search and browse

### Search

Still thinking about different ways to do search.

At the conference talk, it was noted that most modern computers and browsers can happily handle a lot of text and use the meta-F built-in search to find things in an index page! Keep it simple...

What's more, most operating systems or file managers can search over the whole directory structure, including fulltext search of some document formats.

If the site is published on the web, a good sitemap and SEO practices could mean Duckduckgo, Google, Bing can offer decent search without anything needed in the site itself.

However, for some cases, it would be nice to use Solr for a bit of extra power. It would not be hard to include in a portable repository, but running it would require a few extra steps, user permissions,  and host machine dependencies. It would mean a bit of javascript (to run the search bar) and a bundled jar or something.

(is generating some HTML search controls with client-side javascript considered "static HTML"?)

Documents can be sent to the search engine in a new Scrapy pipeline.

An alternative to a search engine pipeline is a separate tool which iterates an OCFL root and indexes to solr. This means we can take advantage of the manifest and do full text extraction, with the extracted text being inserted into the same solr doc as the record, etc.


## Versioning, and separation of content from delivery?

OCFL expects versioning. So if we re-ran XSLT after the repo was already published, a new version would be in order? Or, am I mixing up representation from original content now - the harvested XML records and media/data resources (ie. actual content) go into a nice OCFL repo, and the HTML is always generated outside into a BagIt or plain file structure, as a representation/discovery layer into that content.

## Standards and specifications

HTML version? Pre-5? What is best tradeoff of compatibility, preservation, and feature support?

OCFL partially supported now, but see previous section. BagIt and other standards to come.

Don't forget PCDM for modelling of eg. collections, exhibits, books, data sets, etc:
https://pcdm.org/2016/04/18/models

## "Static"

Can we use JS as long as it is purely client-side? Stick to a particular ECMA spec so that browsers from year X can run it? Make sure a nojs browser still has a good experience?

### Bundled servers

Even though the fs should be portable anyway, it could be nice to ship with a simple bundled webserver (which coudl concievably include solr) - "collection on a cd-rom" or "collection on a raspberry pi" for distribution offline. Depending on implementation, this introduces new system reqs.

### Metadata validation

As usual, any OAI harvester implementation accidentally turns into a tool that also validates metadata! We can produce reports for post-crawl analysis.

## Testing (unit, integration)

* Scrapy Unit Testing (stackoverflow):
    * https://docs.scrapy.org/en/latest/topics/contracts.html
    * https://stackoverflow.com/questions/6456304/scrapy-unit-testing

## Other Links

### Python OCFL:
https://github.com/zimeon/ocfl-py  https://pypi.org/project/ocfl-py/ 
https://github.com/inveniosoftware/ocflcore
https://github.com/OCFL/spec/wiki/Implementations
https://ocflcore.readthedocs.io/en/latest/

### RDF/metadata in HTML:

https://www.w3.org/2001/sw/RDFCore/20031212-rdfinhtml/ 

(currently leaning toward link rel (schema) and meta elements in html head, like DSpace does, for a simple and tried+true approach which search engines also tend to understand)

