FROM nginx:alpine
COPY docker/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY web/ /usr/share/nginx/html/
COPY docker/web/start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
