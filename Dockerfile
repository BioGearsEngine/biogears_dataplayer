FROM httpd:2.4

ENV PORT 80
EXPOSE 80

COPY ./dist/ /usr/local/apache2/htdocs/

CMD ["/bin/bash", "-c", "httpd-foreground"]
