FROM nginx:alpine

COPY v9/docker/web-customer/nginx.conf /etc/nginx/conf.d/default.conf
COPY v9/web-customer/ /usr/share/nginx/html/
COPY v9/docker/web-customer/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080
CMD ["/start.sh"]
