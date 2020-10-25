import boto.ec2.elb
import boto3


class LoadBalancer():
    def __init__(self, connection_region, session):
        self.elb = session.resource('ec2', region_name=connection_region)
