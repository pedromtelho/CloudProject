from create_key import KeyPair
from ec2 import EC2
import boto3
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)

session = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

ec2_key_name = 'ec2-keypair'

key_pair_obj = KeyPair(ec2_key_name)
try:
    key_pair_obj.create()
except:
    print("key pair already exists")
ec2_obj = EC2('ami-0dba2cb6798deb6d8', 2,
              ec2_key_name, 't2.micro', 'us-east-1', session)
ec2_ids = ec2_obj.create_instances()
print(ec2_ids)
