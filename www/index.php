<!DOCTYPE HTML>
<html lang="en">
<head>
    <title>TITLE</title>
    <link rel="icon" type="image/png" href="http://interactive.nydailynews.com/favicons.png">
    <!-- DEFAULT -->
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-status-bar-style" content="black" />
    <link rel="apple-touch-icon" href="">
    <meta name="format-detection" content="telephone=no" />
    <meta http-equiv="X-UA-Compatible" content="IE=Edge" />

    <!-- Titles -->
    <meta property="og:title" content='TITLE' />
    <meta name="twitter:title" content='TITLE' />

    <!-- DESCRIPTION -->
    <meta name="description" content="DESC" />
    <meta property="og:description" content="DESC" />
    <meta name="twitter:description" content="DESC" />

    <!-- KEYWORD -->
    <meta name="keywords" content="TAGS" />
    <meta name="news_keywords" content="TAGS" />

    <!-- LINK -->
    <link rel="canonical" href="CANONICAL">
    <meta property="og:url" content="CANONICAL" />
    <meta name="twitter:url" content="CANONICAL" />

    <!-- THUMBNAIL IMAGE-->
    <meta property="og:image" content="static/img/share.png" />
    <meta name="twitter:image" content="static/img/share.png" />
    <meta name="twitter:image:alt" content="A description of the twitter image" />
    <meta property="og:image:width" content="1024" />
    <meta property="og:image:height" content="512" />

    <!-- PARSELY -->
    <script type="application/ld+json">
        {
            "@context": "http://schema.org",
            "@type": "NewsArticle",
            "headline": "TITLE",
            "url": "CANONICAL",
            "thumbnailUrl": "static/img/share.png",
            "dateCreated": "2017-07-12T06:00:00Z",
            "articleSection": "Interactive",
            "creator": ["Joe Murphy", "Kelli R. Parker", "Interactive Project"],
            "keywords": ["interactive project","interactive"]
        }
    </script>

    <!-- NO NEED TO FILL -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:domain" content="http://interactive.nydailynews.com"/>
    <meta name="twitter:site" content="@nydailynews">
    <meta name="twitter:creator" content="@nydailynews">
    <meta name="decorator" content="responsive" />
    <meta name="nydn_section" content="NY Daily News" />
    <meta name="msvalidate.01" content="02916AAC0DA8B068EFE01D721E03ED7E" />
    <meta name="p:domain_verify" content="78efe4f5c9935744af497772f68a0ee7" />
    <meta property="fb:app_id" content="107464888913" />
    <meta property="fb:admins" content="1594068001" />
    <meta property="fb:pages" content="268914272540" />
    <meta property="og:type" content="article" />
    <meta property="og:site_name" content="NY Daily News" />
    <meta property="article:publisher" content="https://www.facebook.com/NYDailyNews/" />
    <meta name="localeCountry" content="US"/>
    <meta name="localeLanguage" content="en" />

    <!-- ADOBE ANALYTICS -->
    <script src="//assets.adobedtm.com/4fc527d6fda921c80e462d11a29deae2e4cf7514/satelliteLib-c91fdc6ac624c6cbcd50250f79786de339793801.js"></script>

    <link href='https://fonts.googleapis.com/css?family=Open%20Sans|Open+Sans+Condensed:300,700|PT+Serif' rel='stylesheet' type='text/css'>
    <script data-main="http://assets.nydailynews.com/nydn/js/rh.js?r=20170405001" src="http://assets.nydailynews.com/nydn/js/require.js?r=2016LIST" defer></script>
      
    <script>
        var nydn = nydn || {
            "section": "NYDailyNews",
            "subsection": "news",
            "template": "article",
            "revision": "201609014009",
            "bidder": { contains: function() {} },
            "targetPath": document.location.pathname
        };
        var nydnDO = [ { 
            'title':'xxxTITLExxx', 
            'link':'CANONICAL', 
            'p_type':'interactive', 
            'section':'interactive' 
        }];
    </script>
    
    <!-- ADS-START -->
    <script onload="nydn_ads('mta-delays');" src="http://interactive.nydailynews.com/includes/ads/ads.js"></script>
    <!-- ADS-END -->

    <script src="/js/jquery.min.js"></script>
    <link rel="stylesheet" type="text/css" href="http://assets.nydailynews.com/nydn/c/rh.css">
    <link rel="stylesheet" type="text/css" href="http://assets.nydailynews.com/nydn/c/ra.css">
    <link rel="stylesheet" type="text/css" href="/static/css/style.css">

    <script>var nav_params = {section: 'projects', url: 'http://interactive.nydailynews.com/project/'};</script>
    <script src="//interactive.nydailynews.com/library/vendor-nav/vendor-include.js" defer></script>
    <link rel="stylesheet" type="text/css" href="css/site.css">
    <script>
</script>
</head>
<body id="nydailynews" data-section="nydailynews" data-subsection="NY Daily News">

<!-- SITEHEADER-START -->
<header id="templateheader"></header>
<!-- SITEHEADER-END -->

<!-- CONTENT-START -->
<main>
    <article>
        <section id="lead">
            <h1>Is there a current MTA service alert?</h1>
            <h2 id="yes-no"></h2>
            <p>It has been <time id="timer-text"></time> since the previous MTA subway service alert</p>
            <dl></dl>
        </section>

<div class="ad center">
    <div id='div-gpt-ad-x105'>
      <script>
        googletag.cmd.push(function() { googletag.display('div-gpt-ad-x105'); });
      </script>
    </div>
</div>

        <section class="chart" id="chart">
            <h2>Today in MTA alerts</h2>
            <p><em>Chart updates automatically every minute</em></p>
            <div id="chart-wrapper">
				<figure id="day-chart"></figure>
				<div id="tooltip"></div>
<!--
                <img src="static/img/day-chart.png" alt="">
-->
            </div>
        </section>

        <section class="recent" id="recent">
            <h2>Recent MTA service alerts</h2>
            <div>
                <dl></dl>
            </div>
        </section>
    
        <div class="ad center">
            <div id='div-gpt-ad-1423507761396-1'>
              <script>
                googletag.cmd.push(function() { googletag.display('div-gpt-ad-1423507761396-1'); });
              </script>
            </div>
        </div>

        <section id="news" class="recent">
            <h2>Recent MTA news</h2>
            <ul>
            <?php echo file_get_contents('tag-mta-10.html'); ?>
            </ul>
        </section>
    </article>
</main>

<div class="ad center">
    <div id='div-gpt-ad-1423507761396-3'>
      <script>
        googletag.cmd.push(function() { googletag.display('div-gpt-ad-1423507761396-3'); });
      </script>
    </div>
</div>

<script>
/** https://github.com/csnover/js-iso8601 */(function(n,f){var u=n.parse,c=[1,4,5,6,7,10,11];n.parse=function(t){var i,o,a=0;if(o=/^(\d{4}|[+\-]\d{6})(?:-(\d{2})(?:-(\d{2}))?)?(?:T(\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{3}))?)?(?:(Z)|([+\-])(\d{2})(?::(\d{2}))?)?)?$/.exec(t)){for(var v=0,r;r=c[v];++v)o[r]=+o[r]||0;o[2]=(+o[2]||1)-1,o[3]=+o[3]||1,o[8]!=="Z"&&o[9]!==f&&(a=o[10]*60+o[11],o[9]==="+"&&(a=0-a)),i=n.UTC(o[1],o[2],o[3],o[4],o[5]+a,o[6],o[7])}else i=u?u(t):NaN;return i}})(Date)
</script>
<script src="/js/d3/d3.v4.min.js"></script>
<script src="js/app.js"></script>
<!-- CONTENT-END -->

<!-- FOOTER-START -->
<footer id="templatefooter"></footer>
<!-- FOOTER-END -->
<div id="ra-bp">
      </div> <section id="rao">  <div id="rao-close"></div> <div id="rao-wrap"></div> </section>
</div>
<div id="r-scripts">
    <div id="parsely-root" style="display: none">
        <span id="parsely-cfg" data-parsely-site="nydailynews.com"></span>
    </div>
    <div class="r-ad">
        <div id="div-gpt-ad-x100">
        </div>
    </div>
</div>
</body>
</html>
