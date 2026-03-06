FROM nginx:alpine

COPY v6/docker/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY v6/web/ /usr/share/nginx/html/

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
