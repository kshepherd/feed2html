<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns="http://www.loc.gov/METS/"
    xmlns:doc="http://www.lyncode.com/xoai"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:premis="http://www.loc.gov/standards/premis"
    xmlns:mods="http://www.loc.gov/mods/v3" xsi:schemaLocation="http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-1.xsd"
    exclude-result-prefixes="mods doc xsi"
    >
    <xsl:output method="html" indent="yes"/>
    <!-- Parameters set in TransformXmlPipeline -->
    <xsl:param name="website_title"/>
    <xsl:param name="website_subtitle"/>
    <xsl:param name="path_to_assets"/>
    <xsl:param name="publication_date"/>
    <!-- Try to keep citations looking nice -->

    <!-- Main template -->
    <xsl:template match="/">
        <html lang="en">
            <head>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                <meta name="description" content="HTML document generated from OAI feed by https://github.com/kshepherd/feed2html"/>
                <title><xsl:value-of select="//mods:title" /></title>
                <link>
                    <xsl:attribute name="rel">stylesheet</xsl:attribute>
                    <xsl:attribute name="href">
                        <xsl:value-of select="$path_to_assets"/>
                        <xsl:text>/css/pure-min.css</xsl:text>
                    </xsl:attribute>
                </link>
                <link>
                    <xsl:attribute name="rel">stylesheet</xsl:attribute>
                    <xsl:attribute name="href">
                        <xsl:value-of select="$path_to_assets"/>
                        <xsl:text>/css/grids-responsive-min.css</xsl:text>
                    </xsl:attribute>
                </link>
                <link>
                    <xsl:attribute name="rel">stylesheet</xsl:attribute>
                    <xsl:attribute name="href">
                        <xsl:value-of select="$path_to_assets"/>
                        <xsl:text>/css/styles.css</xsl:text>
                    </xsl:attribute>
                </link>
            </head>
            <body>
                <div id="layout" class="pure-g">
                    <div class="sidebar pure-u-1 pure-u-md-1-4">
                        <div class="header">
                            <h1 class="brand-title"><xsl:value-of select="$website_title"/></h1>
                            <h2 class="brand-tagline"><xsl:value-of select="$website_subtitle"/></h2>
<!--                            <nav class="nav">-->
<!--                                <ul class="nav-list">-->
<!--                                    <li class="nav-item">-->
<!--                                        <a class="pure-button" href="http://purecss.io">Pure</a>-->
<!--                                    </li>-->
<!--                                </ul>-->
<!--                            </nav>-->
                        </div>
                    </div>

                    <div class="content pure-u-1 pure-u-md-3-4">
                        <div>
                            <!-- A wrapper for all the blog posts -->
                            <div class="posts">
                                <h1 class="content-subhead"><xsl:value-of select="//mods:genre" /></h1>
                                <!-- A single blog post -->
                                <section class="post">
                                    <header class="post-header">
                                        <h2 class="post-title"><xsl:value-of select="//mods:title" /></h2>
                                        <xsl:if test="$publication_date">
                                            <h3>Date</h3>
                                            <p><xsl:value-of select="$publication_date"/></p>
                                        </xsl:if>
                                    </header>
                                </section>
                                <section>
                                     <xsl:apply-templates/>
                                </section>
                            </div>

                            <div>
                                <p>
                                    <a target="_blank" href="record.xml">XML Record</a>
                                </p>
                            </div>

                            <div class="footer">
                                <div class="pure-menu pure-menu-horizontal">
                                    <ul>
                                        <li class="pure-menu-item">Generated with <a href="https://github.com/kshepherd/feed2html" class="pure-menu-link">feed2html</a></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
        </html>



    </xsl:template>

    <xsl:template match="mods:dateIssued">
        <h3>Date</h3>
        <xsl:value-of select="."/>
    </xsl:template>
    <xsl:template match="mods:dateAccessioned"></xsl:template>
    <xsl:template match="mods:dateAvailable"></xsl:template>

    <xsl:template match="mods:identifier">
        <h3>Identifiers</h3>
        <div class="post-meta">
            <xsl:for-each select="//mods:identifier">
                <xsl:choose>
                    <xsl:when test="starts-with(., 'http')">
                        <p>
                            <a>
                                <xsl:attribute name="target">_blank</xsl:attribute>
                                <xsl:attribute name="href">
                                    <xsl:value-of select="."/>
                                </xsl:attribute>
                                <xsl:value-of select="."/>
                            </a>
                        </p>
                    </xsl:when>
                    <xsl:otherwise>
                        <p><xsl:value-of select="."/></p>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:for-each>
        </div>
    </xsl:template>

    <xsl:template match="mods:topic">
        <p><b>Subject</b>: <xsl:value-of select="."/></p>
    </xsl:template>

  <!-- Template to match mods:name elements -->
    <xsl:template match="mods:name">
        <xsl:choose>
            <!-- Check if mods:roleTerm is 'author' -->
            <xsl:when test="mods:role/mods:roleTerm[text()='author']">
<!--                <xsl:message>Test passed: The name roleType is 'author'.</xsl:message>-->
                <xsl:copy>
                    <xsl:apply-templates select="mods:namePart"/>
                </xsl:copy>
            </xsl:when>
            <xsl:otherwise>

            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    <xsl:template match="mods:namePart">
        <h3>Author</h3>
        <p><xsl:value-of select="."/></p>
    </xsl:template>

    <xsl:template match="premis:object">
        <div style="display:block;">
            <a>
                <xsl:attribute name="href">
                    <xsl:value-of select="premis:objectIdentifier/premis:objectIdentifierValue"/>
                </xsl:attribute>
                <xsl:apply-templates select="premis:objectIdentifier/premis:objectIdentifierValue"/>
            </a>
            <span><xsl:apply-templates select="premis:objectCharacteristics/premis:size"/></span>
            <span> (<xsl:apply-templates select="premis:objectCharacteristics/premis:format/premis:formatDesignation/premis:formatName"/>)</span>
        </div>
    </xsl:template>

    <xsl:template match="premis:objectIdentifierValue">
        <xsl:value-of select="."/>
    </xsl:template>
    <xsl:template match="premis:size">
        <xsl:text>, </xsl:text>
        <xsl:value-of select="."/>
        <xsl:text> bytes, </xsl:text>
    </xsl:template>
    <xsl:template match="premis:formatName">
        <xsl:value-of select="."/>
    </xsl:template>

    <xsl:template match="name">
        <p><xsl:apply-templates/></p>
    </xsl:template>

<xsl:template match="text()">
</xsl:template>
    <!-- Templates to handle line break handling -->
<!--    <xsl:template match="text()">-->
<!--       <xsl:param name="text" select="."/>-->
<!--       <xsl:variable name="startText" select="substring-before(concat($text,'&#10;'),'&#10;')" />-->
<!--       <xsl:variable name="nextText" select="substring-after($text,'&#10;')"/>-->
<!--       <xsl:if test="normalize-space($startText)">-->
<!--           <xsl:value-of select="$startText"/>-->
<!--          <xsl:if test="normalize-space($nextText)">-->
<!--             <br />-->
<!--          </xsl:if>-->
<!--       </xsl:if>-->

<!--       <xsl:if test="contains($text,'&#10;')">-->
<!--          <xsl:apply-templates select=".">-->
<!--             <xsl:with-param name="text" select="$nextText"/>-->
<!--          </xsl:apply-templates>-->
<!--       </xsl:if>-->
<!--    </xsl:template>-->


</xsl:stylesheet>