import boto.ec2.elb
from boto.ec2.elb import ELBConnection
from boto.ec2.elb import HealthCheck
import boto3
from dotenv import load_dotenv
import os
import time

load_dotenv(verbose=True)

class AutoscalingGroup():
    def __init__(self, name, region_name, instance_id_conf, target_groups_arns):
        self.name = name
        self.region_name = region_name
        self.instance_id_conf = instance_id_conf
        self.target_groups_arns = target_groups_arns
        self.launch_configuration_name = 'launch-config-cloud-project'
        self.auto_scaling = boto3.client('autoscaling', region_name=self.region_name, aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                                        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))

    def create_autoscaling_group(self):
        auto_scal = self.auto_scaling.describe_auto_scaling_groups()
        launch_configurations = self.auto_scaling.describe_launch_configurations()
        if auto_scal['AutoScalingGroups']:
            for auto in auto_scal['AutoScalingGroups']:
                if auto['AutoScalingGroupName'] == self.name:
                    self.auto_scaling.delete_auto_scaling_group(AutoScalingGroupName=auto['AutoScalingGroupName'], ForceDelete=True)
                    print("Deleting auto scaling group. It will take around 150 seconds...")
                    time.sleep(150)
            for lconfig in launch_configurations['LaunchConfigurations']:
                if lconfig['LaunchConfigurationName'] == self.name:
                    print("Deleting launch configuration")
                    self.auto_scaling.delete_launch_configuration(LaunchConfigurationName=lconfig['LaunchConfigurationName'])
        print("Creating auto scaling group...")
        return self.auto_scaling.create_auto_scaling_group(AutoScalingGroupName=self.name, InstanceId=self.instance_id_conf, MinSize=1, MaxSize=15, TargetGroupARNs=self.target_groups_arns)


# auto_scal_obj = AutoscalingGroup('autoscal-cloud-project', 'us-east-1', 'i-041f56291c8750b20', ['arn:aws:elasticloadbalancing:us-east-1:915579118891:targetgroup/cloud-project-target/8d3984cebaca9ed5'])
# created = auto_scal_obj.create_autoscaling_group()
# print(created['ResponseMetadata'])