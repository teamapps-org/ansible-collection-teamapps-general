# Matomo

Open Source Website statistics.

Wrapper for webserver role

## Setup

First time, requires manual installation of matomo software:

* wget https://builds.matomo.org/matomo.zip && unzip matomo.zip
* move matomo folder to /container/matomo/code/matomo
* chown www-data: -R /container/matomo/code/

## SSL

Don't enable `force_ssl=1`, it is set by the reverse proxy. if force_ssl is set, then the archive job cannot connect internally to `http://web:8080`

## Tracking Code

* for yourdomain.com (siteId=1)
* using /js/index.php to prevent some adblock

~~~html
<!-- Matomo -->
<script type="text/javascript">
  var _paq = window._paq = window._paq || [];
  /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
  // _paq.push(["disableCookies"]);
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {
    var u="https://{{ matomo_domain }}/";
    _paq.push(['setTrackerUrl', u+'js/index.php']);
    _paq.push(['setSiteId', '1']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.type='text/javascript'; g.async=true; g.src=u+'js/index.php'; s.parentNode.insertBefore(g,s);
  })();
</script>
<!-- End Matomo Code -->
~~~

## Optimization

How to configure Matomo for speed <https://matomo.org/docs/optimize-how-to/>
