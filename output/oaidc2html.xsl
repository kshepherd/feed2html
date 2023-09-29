<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
    xmlns:doc="http://www.lyncode.com/xoai"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/"
    exclude-result-prefixes="oai_dc doc xsi dc"
    >
    <xsl:output method="html" indent="yes"/>
    <!-- Parameters set in TransformXmlPipeline -->
    <xsl:param name="website_title"/>
    <xsl:param name="website_subtitle"/>
    <xsl:param name="path_to_assets"/>
    <xsl:param name="publication_date"/>
    <!-- Try to keep citations looking nice -->
    <xsl:preserve-space elements="dc:identifier"/>

    <!-- Main template -->
    <xsl:template match="/">
        <html lang="en">
            <head>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                <meta name="description" content="HTML document generated from OAI feed by https://github.com/kshepherd/feed2html"/>
                <title><xsl:value-of select="//dc:title" /></title>
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
                                <h1 class="content-subhead"><xsl:value-of select="//dc:type" /></h1>
                                <!-- A single blog post -->
                                <section class="post">
                                    <header class="post-header">
                                        <h2 class="post-title"><xsl:value-of select="//dc:title" /></h2>
                                        <xsl:if test="$publication_date">
                                            <h3>Date</h3>
                                            <p><xsl:value-of select="$publication_date"/></p>
                                        </xsl:if>
                                        <xsl:if test="//dc:creator">
                                            <h3>Authors</h3>
                                        <div class="post-meta">
                                            <xsl:for-each select="//dc:creator">
                                                <p>
                                                    <a href="#" class="post-author">
                                                        <xsl:value-of select="."/>
                                                    </a>
                                                </p>
                                            </xsl:for-each>
                                        </div>
                                        </xsl:if>
                                        <xsl:if test="//dc:identifier">
                                            <h3>Identifiers</h3>
                                            <div class="post-meta">
                                                <xsl:for-each select="//dc:identifier">
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
                                        </xsl:if>
                                    </header>
                                    <xsl:if test="//dc:description">
                                        <h3>Abstract</h3>
                                        <div class="post-description">
                                            <xsl:for-each select="//dc:description">
                                                <div class="abstract">
                                                    <xsl:apply-templates />
                                                </div>
                                            </xsl:for-each>
                                        </div>
                                    </xsl:if>
                                    <xsl:if test="//dc:subject">
                                        <h3>Subjects</h3>
                                        <div class="post-subjects">
                                            <xsl:for-each select="//dc:subject">
                                                <span class="subject-button pure-u-1-2 pure-u-sm-1-3">
                                                    <button class="button-a pure-button">
                                                        <xsl:value-of select="."/>
                                                    </button>
                                                </span>
                                            </xsl:for-each>
                                        </div>
                                    </xsl:if>
                                    <xsl:if test="//dc:publisher">
                                        <h3>Publisher</h3>
                                        <div class="post-publisher">
                                            <xsl:for-each select="//dc:publisher">
                                                <p class="publisher">
                                                    <xsl:value-of select="." />
                                                </p>
                                            </xsl:for-each>
                                        </div>
                                    </xsl:if>
                                    <xsl:if test="//dc:rights">
                                        <h3>Rights</h3>
                                        <div class="post-description">
                                            <xsl:for-each select="//dc:rights">
                                                <div class="rights">
                                                    <xsl:apply-templates />
                                                </div>
                                            </xsl:for-each>
                                        </div>
                                    </xsl:if>
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

    <!-- Templates to handle line break handling -->
    <xsl:template match="text()">
       <xsl:param name="text" select="."/>
       <xsl:variable name="startText" select="substring-before(concat($text,'&#10;'),'&#10;')" />
       <xsl:variable name="nextText" select="substring-after($text,'&#10;')"/>
       <xsl:if test="normalize-space($startText)">
           <xsl:value-of select="$startText"/>
          <xsl:if test="normalize-space($nextText)">
             <br />
          </xsl:if>
       </xsl:if>

       <xsl:if test="contains($text,'&#10;')">
          <xsl:apply-templates select=".">
             <xsl:with-param name="text" select="$nextText"/>
          </xsl:apply-templates>
       </xsl:if>
    </xsl:template>

</xsl:stylesheet>