FROM nginx:alpine

COPY v8/docker/web-customer/nginx.conf /etc/nginx/conf.d/default.conf
COPY v8/web-customer/ /usr/share/nginx/html/
COPY v8/docker/web-customer/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080
CMD ["/start.sh"]
