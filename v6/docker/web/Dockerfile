FROM nginx:alpine

COPY v6/docker/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY v6/web/ /usr/share/nginx/html/
COPY v6/docs/ /usr/share/nginx/html/docs/
COPY v6/docker/web/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080
CMD ["/start.sh"]
