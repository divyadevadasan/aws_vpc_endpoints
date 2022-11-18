from botocore.exceptions import ClientError
import boto3
import json
import os
import sys
import platform

# read input file
try:
    input_file_name = sys.argv[1]
    with open(input_file_name, 'r') as f:
        data = json.load(f)
except IndexError:
    sys.exit("Input file name missing. Please provide input file name.") 

if os.path.getsize(input_file_name) == 0:
    sys.exit(f"Input file '{input_file_name}' is empty.")

#Validate file parameters
if len(data.get('Region')) == 0 or data.get('Region') == "":
    sys.exit("Region is missing ")

region = data.get('Region')

ec2_client = boto3.client('ec2', region_name = region)

vpcids=[]
for vpc in ec2_client.describe_vpcs()['Vpcs']:
    vpcids.append(vpc['VpcId'])
if len(data.get('VPCId')) != 0 and data.get('VPCId') in vpcids:
    print(f"VPCId {data.get('VPCId')} is valid")
else:
    sys.exit(f"VPCId {data.get('VPCId')} is invalid")
subnetids =[]
for subnetid in ec2_client.describe_subnets()['Subnets']:
    subnetids.append(subnetid['SubnetId'])
for ele in data.get('Subnets'):
    if len(data.get('Subnets')) != 0 and ele in subnetids:
        print(f"SubnetID {ele} is valid")
    else:
        sys.exit(f"SubnetID {ele} is invalid")

securityGroups= []
for securityGroup in ec2_client.describe_security_groups()['SecurityGroups']:
    securityGroups.append(securityGroup['GroupId'])
for ele in data.get('SecurityGroups'):
    if len(data.get('Subnets')) != 0 and ele in securityGroups:
        print(f"SecurityGroupID {ele} is valid")
    else:
        sys.exit(f"SecurityGroup {ele} is invalid")

routetables=[]
for routetable in ec2_client.describe_route_tables()['RouteTables']:
    routetables.append(routetable['RouteTableId'])
for ele in data.get('RouteTables'):
    if len(data.get('RouteTables')) != 0 or ele in routetables:
        print(f"RouteTableId {ele} is valid")
    else:
        sys.exit(f"RouteTableId {ele} is invalid")

# List of required service endpoints
required_services = [
    'com.amazonaws.'+region+'.logs', 'com.amazonaws.'+region+'.monitoring', 'com.amazonaws.'+region+'.ec2',
    'com.amazonaws.'+region+'.ec2messages','com.amazonaws.'+region+'.ssm', 
    'com.amazonaws.'+region+'.ssmmessages', 'com.amazonaws.'+region+'.s3', 'com.amazonaws.'+region+'.events',
    'com.amazonaws.'+region+'.dynamodb'
    ]

#Describing the service endpoints already present in account    
try:
    describe_endpoints = ec2_client.describe_vpc_endpoints().get('VpcEndpoints', [])
except ClientError as e:
    print(e)

# Finding the difference between required endpoints and service endpoints already present in account
services_available = []
for endpoint in describe_endpoints:
    services_available.append(endpoint['ServiceName'])
services_pending= set(required_services) - set(services_available)
# Creating Gateway endpoints for s3 and dynamoDB
for service in list(services_pending):
    if (service.__contains__("com.amazonaws."+region+".s3")) or (service.__contains__("com.amazonaws."+region+".dynamodb")):
        try:
            gateway_endpoints = ec2_client.create_vpc_endpoint(
                VpcEndpointType='Gateway',
                VpcId= data['VPCId'],
                RouteTableIds= data['RouteTables'],
                ServiceName= service
                )
        except ClientError as e:
            print(e)        
    else:
        # Creating Interface endpoints for remaining services
        try:
            interface_endpoints = ec2_client.create_vpc_endpoint(
                VpcEndpointType='Interface',
                VpcId= data['VPCId'],
                SubnetIds= data['Subnets'],
                SecurityGroupIds= data['SecurityGroups'],
                ServiceName= service
                )
        except ClientError as e:
            print(e)

# Verifying outbound connectivity
if platform.system() == "Linux":
    command = os.system(f'"for endpoint in logs monitoring ec2 ec2messages ssm ssmmessages s3 events; do nc -zv $endpoint."{region}".amazonaws.com 443; done"')
    print("Shell Script ran with exit code %d" %command)

else:
    print("Verify Outbound Connectivity for Windows OS by manually running Test-NetConnection against endpoints from https://docs.aws.amazon.com/managedservices/latest/accelerate-guide/acc-gs-prereqs.html#acc-vpc-endpoints")
