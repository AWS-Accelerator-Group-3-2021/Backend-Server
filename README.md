# Backend Server
### Facilitates the communication between Android/iOS and Rekognition
#### Uses Flask as a medium, S3 for storage and Rekognition for object detection



## Usage
```POST Request to ${originURL}:8080/upload ```
```
{
    "img": base64string
}
```  

## Output
A response from the server is sent to the client.  
Example:
```
{
   'names': ['Wood, Hardwood, Plywood, Rug, Table], 
   'confidence': 90,
   'combustibility': Yes
}

names: List
confidence: Integer
combustibility: String
```

<br>

## Credentials

Two Methods:
1. Store keys in ```.aws``` folder  
Filename to store keys in is ```credentials```   
    ##### (Follows the AWS SDK Documentation for Boto3)  
```
If you are using terminal:

cd
mkdir ./aws
cd ./aws
touch credentials
nano credentials

<< Text editor will pop up in the terminal, follow on screen instructions and save the file >>
```
2. Store keys in ```.env``` file in the directory you are working in 
```
/directory/.env

AWS_ACCESS_KEY_ID=<your access key>
AWS_SECRET_ACCESS_KEY=<your secret key>
```

## Usage with Localstack (ONLY S3)

Change the endpoint_url to your localstack link
```
endpoint_url = "http://localhost.localstack.cloud:4566"
...
session = boto3.Session(region_name='us-east-1')

s3 = session.client('s3', endpoint_url=endpoint_url)

```
 
