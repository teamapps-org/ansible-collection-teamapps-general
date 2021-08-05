# Matomo

Open Source Website statistics.

Wrapper for webserver role

## Variables

See [defaults.yml](defaults/main.yml)

Required configuration:

* `matomo_domain:` (default: `'{{ ansible_fqdn }}'` )
* `matomo_mysql_root_password:`
* `matomo_mysql_password:`

## Setup

First time, requires manual configuration of matomo software:

* Open matomo domain and configure database, admin account etc.

Database Configuration:

Host: `db`
User: `matomo`
Password: (value of `matomo_mysql_password` )
Database: `matomo`
Prefix: `matomo_`

## Matomo Configuration

* System/General: Disable Auto Archiving. a cronjob is configured by the ansible role.

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
