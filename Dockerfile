FROM ubuntu:trusty

RUN apt-get update && apt-get install -yq ruby ruby-dev build-essential git nginx

RUN gem install --no-ri --no-rdoc bundler
ADD Gemfile /app/Gemfile
ADD Gemfile.lock /app/Gemfile.lock
RUN cd /app; bundle install
ADD . /app
WORKDIR /app

EXPOSE 80

RUN bundle exec middleman build --clean && cp -r build/* /usr/share/nginx/html/
CMD nginx -g 'daemon off;' 
