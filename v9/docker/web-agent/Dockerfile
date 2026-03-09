FROM nginx:alpine

COPY v9/docker/web-agent/nginx.conf /etc/nginx/conf.d/default.conf
COPY v9/web-agent/ /usr/share/nginx/html/
COPY v9/docker/web-agent/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080
CMD ["/start.sh"]
