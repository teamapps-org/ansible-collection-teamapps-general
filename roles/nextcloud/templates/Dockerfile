FROM nextcloud:{{ nextcloud_version }}-fpm

RUN set -ex && \
    \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
    && \
    rm -rf /var/lib/apt/lists/*
