#!/bin/sh
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo -u postgres psql -c "CREATE USER cloud WITH PASSWORD 'cloud';"
sudo -u postgres psql -c "CREATE DATABASE tasks OWNER cloud;"
sed '59 c\
listen_addresses = "*"' /etc/postgresql/12/main/postgresql.conf
echo "host all all 0.0.0.0 trust " >> /etc/postgresql/12/main/pg_hba.conf     
sudo ufw allow 5432/tcp     
sudo systemctl restart postgresql