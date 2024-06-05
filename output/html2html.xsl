<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="html" indent="yes"/>

    <xsl:template match="/">
        <html>
            <head>
                <title>Metadata Display</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .metadata { margin-bottom: 10px; }
                    .label { font-weight: bold; }
                </style>
            </head>
            <body>
                <h1>Descriptive Metadata</h1>
                <xsl:apply-templates select="//meta"/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="meta">
        <div class="metadata">
            <span class="label">
                <xsl:choose>
                    <xsl:when test="starts-with(@name, 'DC.')">
                        <xsl:value-of select="substring-after(@name, 'DC.')"/>
                    </xsl:when>
                    <xsl:when test="starts-with(@name, 'DCTERMS.')">
                        <xsl:value-of select="substring-after(@name, 'DCTERMS.')"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="@name"/>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:if test="@scheme"> (<xsl:value-of select="@scheme"/>)</xsl:if>:
            </span>
            <span class="value"><xsl:value-of select="@content"/></span>
        </div>
    </xsl:template>
</xsl:stylesheet>