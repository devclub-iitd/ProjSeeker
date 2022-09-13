FROM nginx:1.21.3-alpine
ARG PORT
ENV PORT $PORT
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/
RUN envsubst '$PORT' < /etc/nginx/conf.d/nginx.conf > /etc/nginx/conf.d/nginx1.conf
RUN mv /etc/nginx/conf.d/nginx1.conf /etc/nginx/conf.d/nginx.conf