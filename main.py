from create_key import KeyPair
from ec2 import EC2
from load_balancer import LoadBalancer
from autoscaling_group import AutoscalingGroup
import boto3
from dotenv import load_dotenv
import os


load_dotenv(verbose=True)

session = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


ec2_nv_key_name = 'ec2-keypair-nv'
ec2_oh_key_name = 'ec2-keypair-oh'
ubuntu20_nvirginia_img = 'ami-0dba2cb6798deb6d8'
ubuntu20_ohio_img = 'ami-07efac79022b86107'
target_group_name = 'cloud-project-target'
script_database = '''#!/bin/sh
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo -u postgres psql -c "CREATE USER cloud WITH PASSWORD 'cloud';"
sudo -u postgres psql -c "CREATE DATABASE tasks OWNER cloud;"
sudo sed -i "59 c\
listen_addresses = '*'" /etc/postgresql/12/main/postgresql.conf
sudo bash -c 'echo "host all all 0.0.0.0/0 trust" >> /etc/postgresql/12/main/pg_hba.conf'
sudo ufw allow 5432/tcp     
sudo systemctl restart postgresql
'''
load_balancer_name = 'my-lb'

key_pair_obj_nv = KeyPair(ec2_nv_key_name, 'us-east-1', session)
key_pair_obj_oh = KeyPair(ec2_oh_key_name, 'us-east-2', session)
try:
    key_pair_obj_nv.create()
except:
    print("key pair already exists in North Virginia")
try:
    key_pair_obj_oh.create()
except:
    print("key pair already exists in Ohio")


## Ohio __init__

ec2_ohio = EC2(ubuntu20_ohio_img,
              ec2_oh_key_name, 't2.micro', 'us-east-2', 'secgroup-teste', script_database, session)
ohio_subnets_ids, oh_vpc_ids = ec2_ohio.describe_subnets()
print("creating database instance...")
ec2_id_ohio = ec2_ohio.create_instances(1)
print("Status - OK")

## reload é necessário para pegar o ip das instancias
ec2_id_ohio[0].reload()
database_ip = ec2_id_ohio[0].public_ip_address

script_machines = f"""#!/bin/bash
sudo apt update
sudo apt install python3-dev libpq-dev python3-pip -y
cd /home/ubuntu
git clone https://github.com/pedromtelho/tasks.git
sudo sed -i "83 c 'HOST' : '{database_ip}'," tasks/portfolio/settings.py
sh ./tasks/install.sh
"""

## North Virginia __init__

ec2_north_virginia = EC2(ubuntu20_nvirginia_img,
              ec2_nv_key_name, 't2.micro', 'us-east-1', 'secgroup-teste', script_machines, session)
nv_subnets_ids, nv_vpc_ids = ec2_north_virginia.describe_subnets()
print("creating server instance...")
ec2_id_north_virginia = ec2_north_virginia.create_instances(1)
print("Status - OK")

security_group_id = [instance.security_groups[0]['GroupId'] for instance in ec2_id_north_virginia]

## Load balancer - North Virginia __init__

lb = LoadBalancer(load_balancer_name, nv_subnets_ids, 'us-east-1')    

print("creating load balancer...")
elb_obj = lb.create_elb(security_group_id)
elb_arn = elb_obj['LoadBalancers'][0]['LoadBalancerArn']
elb_dns = elb_obj['LoadBalancers'][0]['DNSName']

a_file = open("script", "r")
list_of_lines = a_file.readlines()
list_of_lines[6] = f"URL_SERVER = '{elb_dns}'\n"

a_file = open("script", "w")
a_file.writelines(list_of_lines)
a_file.close()

print("Status - OK")
target_group_obj = lb.create_target_group(target_group_name, nv_vpc_ids[0])
target_groups_arns = [target['TargetGroupArn'] for target in target_group_obj['TargetGroups']]

targets_instances_list = [{'Id': instance.id} for instance in ec2_id_north_virginia]

## create listener
print('Create listener for application load balancer...')
lb.create_listener(elb_arn, target_groups_arns[0])

## Autoscalling group

auto_scal_obj = AutoscalingGroup('autoscal-cloud-project', 'us-east-1', ec2_id_north_virginia[0].id, target_groups_arns)
print("creating autoscalling group...")
created = auto_scal_obj.create_autoscaling_group()
print("Aguarde alguns minutos antes de acessar os métodos...")

