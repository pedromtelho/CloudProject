import boto3


class EC2():
    def __init__(self, image_id, max_count, key_name, instance_type, region_name, session):
        self.image_id = image_id
        self.max_count = max_count
        self.key_name = key_name
        self.instance_type = instance_type
        self.region_name = region_name
        self.ec2 = session.resource('ec2', region_name=self.region_name)

    def check_running_instances(self):
        id_instances = []
        instances = self.ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            if instance.key_name == self.key_name:
                id_instances.append(instance.id)
        return id_instances

    def create_instances(self):
        ids = self.check_running_instances()
        if ids:
            self.ec2.instances.filter(InstanceIds=ids).terminate()
        instances = self.ec2.create_instances(
            ImageId=self.image_id,
            MinCount=1,
            MaxCount=self.max_count,
            InstanceType=self.instance_type,
            KeyName=self.key_name
        )
        return instances
