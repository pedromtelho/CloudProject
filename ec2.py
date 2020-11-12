import boto3
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)

class EC2():
    def __init__(self, image_id, key_name, instance_type, region_name, security_group_name, user_data, session):
        self.image_id = image_id
        self.key_name = key_name
        self.instance_type = instance_type
        self.region_name = region_name
        self.security_group_name = security_group_name
        self.user_data = user_data
        # self.tags = tags
        self.ec2_resource = session.resource('ec2', region_name=self.region_name)
        self.ec2_client = boto3.client('ec2', region_name=self.region_name, aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                                        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))

    def describe_subnets(self):
        subnets = self.ec2_client.describe_subnets()
        ids = [i["SubnetId"] for i in subnets["Subnets"]]
        vpc_ids = [i["VpcId"] for i in subnets["Subnets"]]
        return ids, vpc_ids

    def create_instances(self, max_count):
        waiter_terminated = self.ec2_client.get_waiter('instance_terminated')
        waiter_created = self.ec2_client.get_waiter('instance_status_ok')

        ids = []
        instances = self.ec2_resource.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            if instance.key_name == self.key_name:
                ids.append(instance.id)
        if ids:
            self.ec2_resource.instances.filter(InstanceIds=ids).terminate()
            # waiter_terminated.wait(InstanceIds=ids)

        # self.create_security_group(False)
        instances = self.ec2_resource.create_instances(
            ImageId=self.image_id,
            MinCount=1,
            MaxCount=max_count,
            InstanceType=self.instance_type,
            KeyName=self.key_name,
            SecurityGroups=[self.security_group_name],
            UserData=self.user_data
        )
        waiter_created.wait(InstanceIds=[instance.id for instance in instances ])
        return instances        
    
    def create_security_group(self, flag_delete):
        sec_groups = self.ec2_client.describe_security_groups(Filters=[{'Name': 'group-name','Values': [self.security_group_name]},])
        if sec_groups:
            for sec_group in sec_groups['SecurityGroups']:
                if flag_delete:
                    self.ec2_client.delete_security_group(GroupId=sec_group['GroupId'])
        response = self.ec2_client.create_security_group(GroupName=self.security_group_name, Description='Teste')
        return self.ec2_client.authorize_security_group_ingress(
            GroupId=response['GroupId'],
            IpPermissions=[
                {'IpProtocol': 'tcp',
                'FromPort': 5432,
                'ToPort': 5432,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                'FromPort': 8080,
                'ToPort': 8080,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])
