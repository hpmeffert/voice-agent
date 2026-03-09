FROM nginx:alpine

COPY v9/docker/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY v9/web/ /usr/share/nginx/html/
COPY v9/docs/ /usr/share/nginx/html/docs/
COPY v9/docker/web/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080
CMD ["/start.sh"]
