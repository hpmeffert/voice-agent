FROM nginx:alpine

COPY v8/docker/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY v8/web/ /usr/share/nginx/html/
COPY v8/docs/ /usr/share/nginx/html/docs/
COPY v8/docker/web/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080
CMD ["/start.sh"]
