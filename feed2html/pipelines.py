# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from lxml import etree

class Feed2HtmlPipeline:
    def process_item(self, item, spider):
        return item

class TransformXmlPipeline:
    def process_item(self, item, spider):
        xslt_root = etree.XML('''
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
    xmlns:doc="http://www.lyncode.com/xoai"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/"
    exclude-result-prefixes="oai_dc doc xsi dc"
    >
    <xsl:output method="html" indent="yes"/>
    <xsl:template match="/">
        <html>
            <header>
                <title><xsl:value-of select="//dc:title" /></title>
            </header>
            <body>
                <h1><xsl:value-of select="//dc:title" /></h1>
                <xsl:for-each select="//dc:identifier">
                    <p><xsl:value-of select="."/></p>
                </xsl:for-each>
                
                <xsl:for-each select="//dc:description">
                    <xsl:value-of select="."/>
                </xsl:for-each>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
        ''')
        """
                        <xsl:for-each select="//dc:description">
                    <p><xsl:value-of select="."/></p>
                </xsl:for-each>"""
        xslt_root = etree.parse('output/oaidc2html.xsl')
        transform = etree.XSLT(xslt_root)
        root = etree.XML(item['record'])
        result = transform(root)
        logging.info("text=%s", result.getroot().text)
        logging.info(str(result))
        file = open("output/output.html", "w")
        file.write(str(result))
        file.close()
        return item