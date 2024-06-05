import scrapy

class DSpaceWeb(scrapy.spiders.CrawlSpider):
    name = "dspaceweb"

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
        'AUTO_THROTTLE_ENABLED': True,
    }

    def start_requests(self):
        """
        Start the requests for the spider. Each run, the crawler will start here
        """
        # Empty search, first page of each category.
        urls = [
            'https://repository.uwc.ac.za/browse?type=title&offset=0&etal=-1&order=ASC',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Follow links to stories
        for href in response.css('.artifact-title a::attr(href)'):
            yield response.follow(href, self.parse_item)

        for href in response.css('a.next-page-link a::attr(href)'):
            yield response.follow(href, self.parse)

    def parse_item(self, response):
        """
        Parse the actual story page. Usually this means XPath or CSS selectors to find the bits of content
        we want, and extracting the text out.
        """

        # Return the following fields as a dictionary
        yield {
            'url': response.url,
            'title': response.xpath('//meta[@name="DC.title"]/@content').get(),
            'author': response.xpath('//meta[@name="DC.creator"]/@content').get(),
            'issueDate': response.xpath('//meta[@name="DCTERMS.issued"]/@content').get(),
            'bibliographicCitation': response.xpath('//meta[@name="DCTERMS.bibliographicCitation"]/@content').get(),
            'identifier': response.xpath('//meta[@name="DC.identifier"]/@content').get(),
            'abstract': response.xpath('//meta[@name="DCTERMS.abstract"]/@content').get(),
            'language': response.xpath('//meta[@name="DC.language"]/@content').get(),
            'subject': response.xpath('//meta[@name="DC.subject"]/@content').get(),
            'type': response.xpath('//meta[@name="DC.type"]/@content').get(),
            'bitstream': response.xpath('//meta[@name="citation_pdf_url"]/@content').get(),
        }
        yield response.follow(response.xpath('//meta[@name="citation_pdf_url"]/@content').get())


