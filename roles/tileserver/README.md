# Tileserver-GL

Open Source (Vector) Map Tiles Self Hosted

## Usage

~~~yaml
- name: Tileserver / Mapserver Play
  hosts:
    - mapserver.example.com
  vars:
    tileserver_domain: map.example.com
    tileserver_allowed_referers:
      - '{{ tileserver_domain }}'
      - .example.com
  roles:
    - role: teamapps.general.tileserver
      tags:
        - tileserver
~~~

## Map Data

you need to manually install the data

* download map data, source https://osm.dbtc.link/mbtiles/ (check current file)
  * `wget https://osm.dbtc.link/mbtiles/2023-05-29-planet.mbtiles.lz4`
  * `lz4 -d *-planet.mbtiles.lz4 planet.mbtiles`
* download natural earth tiles: https://klokantech.github.io/naturalearthtiles/
  * create png version of natural_earth tiles. (see below)
* download fonts from https://github.com/openmaptiles/fonts/releases/tag/v2.0
  extract in data/fonts/

  ~~~bash
  cd /container/tileserver/data/
  mkdir fonts
  wget https://github.com/openmaptiles/fonts/releases/download/v2.0/v2.0.zip
  unzip v2.0.zip -d fonts/
  ~~~

see more in Section Data

### create natural earth PNG version mbtiles

~~~bash
cd /container/tileserver/data
git clone --depth=1 -b gh-pages https://github.com/lukasmartinelli/naturalearthtiles.git
docker run -it  -v /container/tileserver/data/:/data/:rw jskeates/mbutil --image_format=png /data/naturalearthtiles/tiles/natural_earth_2_shaded_relief.raster /data/natural_earth_2_shaded_relief.raster.png.mbtiles
~~~

## About

* https://openmaptiles.org/docs/
* https://openmaptiles.org/docs/host/tileserver-gl/
* https://tileserver.readthedocs.io/en/latest/

## Frontend

* https://openmaptiles.org/docs/website/maplibre-gl-js/
* Examples with Plugins https://maplibre.org/maplibre-gl-js-docs/example/

## Data

Official paid data

* https://data.maptiler.com/downloads/planet/

Generate tiles from open data

* https://github.com/onthegomap/planetiler/blob/main/PLANET.md
* https://daylightmap.org/

Pregenerated mbtiles for free

* https://www.reddit.com/r/openstreetmap/comments/v9yoed/downloadable_planet_europe_and_netherlands/
* https://osm.dbtc.link/mbtiles/

Download and reference in config.json

relief raster data: https://klokantech.github.io/naturalearthtiles/
download to data folder: https://github.com/lukasmartinelli/naturalearthtiles/releases/download/v1.0/natural_earth_2_shaded_relief.raster.mbtiles

## Styles

* https://openmaptiles.org/styles/

Download data from gh-pages branch (includes style-local.json and necessary data like sprites)

* QWant Style: https://github.com/Qwant/qwant-basic-gl-style/tree/gh-pages
* Some nice free styles with "free" contours and hillshade: https://maps.netsyms.net/

## Fonts

download fonts from https://github.com/openmaptiles/fonts/releases/tag/v2.0
extract in data/fonts/

## Other interesting data

* relief raster data: https://klokantech.github.io/naturalearthtiles/
* Various free geodata http://freegisdata.rtwilson.com/

free style with hillshade and contours (US only)

* https://github.com/nst-guide/osm-liberty-topo
* https://github.com/nst-guide/contours

Free terrain tiles from aws:

* https://registry.opendata.aws/terrain-tiles/
* on demand generated hillshades from aws terrain-tiles https://terradactile.sparkgeo.com/
  * Technical background: https://sparkgeo.com/blog/terradactile-generate-cogs-from-aws-terrain-tiles/
  * Source code: https://github.com/sparkgeo/terradactile-lambda/blob/master/terradactile/terradactile/app.py
  * GDAL Docker image https://github.com/developmentseed/geolambda
* https://www.openslopemap.org/karte/
* Global elevation data: http://www.viewfinderpanoramas.org/Coverage%20map%20viewfinderpanoramas_org3.htm

Terrain Tiles:
* https://bertt.wordpress.com/2022/05/24/custom-maplibre-terrain-tiles/
* https://www.eorc.jaxa.jp/ALOS/en/dataset/aw3d30/aw3d30_e.htm
* https://maplibre.org/news/2022-05-20-terrain3d/#10.46/47.2713/11.4/21.6/41

Generate hillshade

* https://github.com/interline-io/planetutils#elevation_tile_download
* https://github.com/Karry/hillshade-tile-server
* https://github.com/clhenrick/gdal_hillshade_tutorial
* https://www.kreidefossilien.de/en/miscellaneous/custom-hillshading-for-osmand

Generate contours

* https://github.com/RomainQuidet/generate-osm-contours
* https://github.com/joe-akeem/contour-tiles

* hillshade/contours and script for France:
  * https://www.data.gouv.fr/fr/datasets/bd-alti-r-25-m-tuiles-pour-courbes-de-niveau-et-ombrage-dynamiques-1/
  * https://makina-corpus.com/sig-webmapping/optimisation-tuiles-mnt-rgb-ombrage-dynamique-mapbox-gl-maplibre-gl
  * https://makina-corpus.com/sig-webmapping/representation-des-modeles-numeriques-de-terrain-sur-le-web-ombrage-et-3d
  * https://github.com/lokkelvin2/kepler.gl-offline#hillshade-generation

## nice to know

Backstory behind Maplibre and planetiler: https://medium.com/@onthegomap/helping-sustain-open-maps-on-the-web-dc419f3af75d

## Custom Styles

* https://github.com/maputnik/editor
  * Tutorial: https://yasoob.me/posts/custom-map-with-tileserver-gl/
* https://github.com/go-spatial/fresco

Howto

* Download styles.json for the style from frontend. (contains fixed urls to your server).
* Open in Maputnik Editor.
* Change config.
* Export.
* Replace the sources, glyph and sprites config with internal placeholders and mbtiles:// urls. example:

~~~json
"sources": {
    "openmaptiles": {
      "type": "vector",
      "url": "mbtiles://{v3}"
    },
    "natural_earth_2_shaded_relief": {
      "maxzoom": 6,
      "tileSize": 256,
      "type": "raster",
      "url": "mbtiles://{natural_earth_2_shaded_relief}"
    }
  },
  "sprite": "{styleJsonFolder}/sprites/osm-liberty",
  "glyphs": "{fontstack}/{range}.pbf",
~~~

## related projects

* Nominatim: geo search, reverse geocoding to self host.
* Free Routing https://github.com/graphhopper/graphhopper
* Various tools for vector tiles: https://github.com/mapbox/awesome-vector-tiles

### AWS Open Data Terrain Tiles

* https://registry.opendata.aws/terrain-tiles/

Zoom level 11:
aws s3 ls --summarize --human-readable --no-sign-request s3://elevation-tiles-prod/geotiff/11/ --recursive
Total Objects: 4194304
   Total Size: 130.9 GiB
