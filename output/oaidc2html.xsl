<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
    xmlns:doc="http://www.lyncode.com/xoai"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/"
    exclude-result-prefixes="oai_dc doc xsi dc"
    >
    <xsl:output method="html" indent="yes"/>
    <xsl:preserve-space elements="dc:identifier"/>
    <xsl:template match="/">
        <html lang="en">
            <head>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                <meta name="description" content="A layout example that shows off a blog page with a list of posts."/>
                <title><xsl:value-of select="//dc:title" /></title>
                <link rel="stylesheet" href="/tmp/css/pure-min.css"/>
                <link rel="stylesheet" href="/tmp/css/grids-responsive-min.css"/>
                <link rel="stylesheet" href="/tmp/css/styles.css"/>
            </head>
            <body>
                <div id="layout" class="pure-g">
                    <div class="sidebar pure-u-1 pure-u-md-1-4">
                        <div class="header">
                            <h1 class="brand-title">Open Access Resarch</h1>
                            <h2 class="brand-tagline">Static HTML pages and XML records</h2>

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
                                <h1 class="content-subhead"><xsl:value-of select="//dc:title" /></h1>
                                <!-- A single blog post -->
                                <section class="post">
                                    <header class="post-header">
<!--                                        <img width="48" height="48" alt="Tilo Mitra&#x27;s avatar" class="post-avatar" src="/img/common/tilo-avatar.png"/>-->

                                        <h2 class="post-title"><xsl:value-of select="//dc:title" /></h2>
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
                                        <h3>Identifiers</h3>
                                        <div class="post-meta">
                                        <xsl:for-each select="//dc:identifier">
                                            <xsl:if test="starts-with(., 'http')">
                                                <p>
                                                    <a>
                                                        <xsl:attribute name="target">_blank</xsl:attribute>
                                                        <xsl:attribute name="href">
                                                            <xsl:value-of select="."/>
                                                        </xsl:attribute>
                                                        <xsl:value-of select="."/>
                                                    </a>
                                                </p>
                                            </xsl:if>
                                        </xsl:for-each>
                                        </div>
                                    </header>
                                    <h3>Abstract</h3>
                                    <div class="post-description">
                                        <xsl:for-each select="//dc:description">
                                            <div class="abstract">
                                                <xsl:apply-templates />
                                            </div>
                                        </xsl:for-each>
                                    </div>
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
                                        <li class="pure-menu-item"><a href="http://purecss.io/" class="pure-menu-link">About</a></li>
                                        <li class="pure-menu-item"><a href="http://github.com/pure-css/pure/" class="pure-menu-link">GitHub</a></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
        </html>

    </xsl:template>

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