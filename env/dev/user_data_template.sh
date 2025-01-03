#!/bin/bash

sudo yum update -y
sudo yum install -y docker git unzip jq

sudo service docker start
sudo service docker enable

sudo usermod -a -G docker ec2-user

sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose