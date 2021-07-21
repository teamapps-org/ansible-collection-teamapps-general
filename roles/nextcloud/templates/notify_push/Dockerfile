FROM rust:alpine

WORKDIR /app
RUN wget https://github.com/nextcloud/notify_push/releases/download/{{ nextcloud_notify_push_version }}/notify_push.tar.gz
RUN tar -xzf notify_push.tar.gz
RUN rm -f notify_push.tar.gz

CMD ["/app/notify_push/bin/x86_64/notify_push", "/var/www/html/config/config.php"]
EXPOSE 7867/tcp
