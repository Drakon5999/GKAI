FROM python:3.10-bullseye
ARG DEBIAN_FRONTEND=noninteractive
RUN curl -sL https://deb.nodesource.com/setup_19.x | bash -
RUN apt-get install -y nodejs

ENV GENERATE_SOURCEMAP=false

WORKDIR /frontend
COPY . .
RUN npm install -g serve
RUN npm install react-scripts
RUN npm run build

ENTRYPOINT ["serve", "-s", "build"]
