# aws_vpc_endpoints
Script to create VPC endpoints

#### What does the script do: 
The script checks the customer's primary region for existing VPC endpoints, compares it with a list of Accelerate required endpoints and deploys the missing endpoints to the account. 

#### Who will be using this script: 
Customer will be running the script as a part of AWS Managed Services Accelerate account onboarding. 

#### Why are we running this script:
Each AMS Accelerate account requires a list of private connections from the primary VPC to AWS & VPC endpoint services. This is currently deployed manually by the customer as a part of Accelerate Onboarding Pre-requisite. To reduce the onboarding time and 

### Prerequisites:
Linux instance with IAM permissions to execute API calls "ec2:describe-vpc-endpoints" and "ec2:create-vpc-endpoint" via aws cli or cloudshell. 

### Required Input Parameters: 
1. VPC ID from which the service is accessed
2. Subnet IDs from each availability zone. 
3. Route Table IDs to assign to the VPC endpoints.
4. Security Group IDs to assign to the VPC endpoints.

### Implementation:

1. Download vpcendpoints.zip.
2. Extract vpcendpoints.py file.
3. Upload the file to Cloudshell and execute the script. 
4. Alternatively, copy the file to your localhost or a Linux instance with sufficient EC2 permissions  and

### Documentation: 
* https://docs.aws.amazon.com/vpc/latest/privatelink/create-interface-endpoint.html
