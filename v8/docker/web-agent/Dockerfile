FROM nginx:alpine

COPY v8/docker/web-agent/nginx.conf /etc/nginx/conf.d/default.conf
COPY v8/web-agent/ /usr/share/nginx/html/
COPY v8/docker/web-agent/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080
CMD ["/start.sh"]
