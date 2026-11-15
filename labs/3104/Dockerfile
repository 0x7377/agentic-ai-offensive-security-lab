FROM php:8.4.26-apache

RUN a2enmod headers \
    && sed -ri 's!Listen 80!Listen 8080!' /etc/apache2/ports.conf \
    && sed -ri 's!<VirtualHost \*:80>!<VirtualHost *:8080>!' /etc/apache2/sites-available/000-default.conf \
    && printf '%s\n' \
       'ServerTokens Full' \
       'ServerSignature Off' \
       'Header always set X-Backend-SAPI "apache2handler"' \
       'Header always set X-Lab-Safety "command-emulation-only"' \
       > /etc/apache2/conf-available/training-fingerprint.conf \
    && a2enconf training-fingerprint

COPY php2shell/php.ini /usr/local/etc/php/conf.d/zz-training.ini
COPY static/php2shell/ /var/www/html/

RUN chown -R www-data:www-data /var/www/html

EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=3s --retries=15 CMD curl -fsS http://127.0.0.1:8080/healthz.php || exit 1
