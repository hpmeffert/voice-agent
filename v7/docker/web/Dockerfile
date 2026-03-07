FROM nginx:alpine

COPY v7/docker/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY v7/web/ /usr/share/nginx/html/
COPY v7/docs/ /usr/share/nginx/html/docs/
COPY v7/docker/web/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080
CMD ["/start.sh"]
