import boto3


class KeyPair():
    def __init__(self, file_name):
        self.file_name = file_name

    def create(self):
        ec2 = boto3.resource('ec2')

        # create a file to store the key locally
        outfile = open(self.file_name+'.pem', 'w')
        outfile_ignore = open('.gitignore', 'w')
        outfile_ignore.write(self.file_name+'.pem'+'\n')
        outfile_ignore.write('.env'+'\n')
        outfile_ignore.write('__pycache__/'+'\n')
        # call the boto ec2 function to create a key pair
        key_pair = ec2.create_key_pair(KeyName=self.file_name)

        # capture the key and store it in a file
        KeyPairOut = str(key_pair.key_material)
        outfile.write(KeyPairOut)
