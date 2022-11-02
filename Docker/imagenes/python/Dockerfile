FROM php:5.6-apache
EXPOSE 80/tcp
EXPOSE 80/udp
EXPOSE 8080/tcp
EXPOSE 8080/udp

WORKDIR /var/www/html
RUN apt -y update
RUN apt-get -y install libicu-dev
RUN apt-get -y install unzip
RUN apt-get install -y zlib1g-dev libicu-dev g++
RUN docker-php-ext-install pdo_mysql
RUN docker-php-ext-configure intl
RUN docker-php-ext-install intl
RUN a2enmod rewrite
RUN php -r "copy('http://getcomposer.org/installer', 'composer-setup.php');"
RUN php composer-setup.php
RUN php -r "unlink('composer-setup.php');"
RUN mv composer.phar /usr/local/bin/composer
RUN composer require fakerphp/faker
RUN composer require spipu/html2pdf