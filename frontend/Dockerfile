FROM python:3.10-bullseye
ARG DEBIAN_FRONTEND=noninteractive
RUN curl -sL https://deb.nodesource.com/setup_19.x | bash -
RUN apt-get install -y nodejs

WORKDIR /frontend
COPY . .
RUN npm install 
RUN npm install react-scripts 

ENTRYPOINT ["npm", "start"]
