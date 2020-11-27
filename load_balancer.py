import boto3
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)

class LoadBalancer():
    def __init__(self, name, subnets, region_name):
        self.name = name
        self.subnets = subnets
        self.lb = None
        self.region_name = region_name
        self.elb = boto3.client('elbv2', region_name=self.region_name, aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                                        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))

    def create_listener(self, elb_arn, target_group_arn):
        return self.elb.create_listener(LoadBalancerArn=elb_arn, Protocol='HTTP', Port=8080, DefaultActions=[{'Type': 'forward', 'TargetGroupArn': target_group_arn,},],)

    def create_target_group(self, name, vpc_id, elb_arn):
        response = self.elb.describe_target_groups()
        response_listeners = self.elb.describe_listeners(LoadBalancerArn=elb_arn)
        if response_listeners['Listeners']:
            for listener in response_listeners['Listeners']:
                self.elb.delete_listener(ListenerArn=listener['ListenerArn'])
        if response['TargetGroups']:
            for t_group in response['TargetGroups']:
                if t_group['TargetGroupName'] == name:
                    self.elb.delete_target_group(TargetGroupArn=t_group['TargetGroupArn'])
        return self.elb.create_target_group(Name=name, Protocol='HTTP', Port=8080, VpcId=vpc_id)

    def register_targets(self, target_group_object, target_group_name, targets_instances_list):
        for t_group in target_group_object['TargetGroups']:
            if t_group['TargetGroupName'] == target_group_name:
                return self.elb.register_targets(TargetGroupArn=t_group['TargetGroupArn'],Targets=targets_instances_list), t_group['TargetGroupArn']

    def create_elb(self, security_group):
        elbs = self.elb.describe_load_balancers()
        if elbs['LoadBalancers']:
            for elb in elbs['LoadBalancers']:
                if elb['LoadBalancerName'] == self.name:
                    self.elb.delete_load_balancer(LoadBalancerArn=elb['LoadBalancerArn'])

        return self.elb.create_load_balancer(Name=self.name, Subnets=self.subnets,  SecurityGroups=security_group, Scheme="internet-facing", Type="application")
