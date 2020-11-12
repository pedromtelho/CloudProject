import boto3

class KeyPair():
    def __init__(self, key_name,region_name, session):
        self.key_name = key_name
        self.region_name = region_name
        self.ec2 = session.resource('ec2', region_name=self.region_name)

    def create(self):
        key_pair = self.ec2.create_key_pair(KeyName=self.key_name)
        with open(self.key_name+".pem", "w") as file_key: 
            # Writing data to a file 
            file_key.write(key_pair.key_material) 
