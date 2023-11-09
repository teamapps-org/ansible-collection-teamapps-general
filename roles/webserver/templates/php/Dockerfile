FROM php:{{ webserver_php_version }}-fpm

ADD https://github.com/mlocati/docker-php-extension-installer/releases/latest/download/install-php-extensions /usr/local/bin/

RUN set -ex && \
    \
    apt-get update && \
    apt-get install -y --no-install-recommends \
{% for package in webserver_php_apt_packages %}
        {{ package }} \
{% endfor %}
    && \
    chmod +x /usr/local/bin/install-php-extensions && sync && \
    install-php-extensions \
{% for ext in webserver_php_extensions %}
        {{ ext }} \
{% endfor %}
        && \
    rm -rf /var/lib/apt/lists/*

# Use the default production configuration
RUN mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

COPY php-override.ini /usr/local/etc/php/conf.d/override.ini
USER www-data
