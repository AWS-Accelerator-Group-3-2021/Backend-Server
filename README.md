# flaskrecocombus
### Facilitates the communication between Android/iOS and Rekognition
#### Uses Flask as a medium, S3 for storage and Rekognition for object detection



## Usage

Add all combustible objects into ```combustiblelist.csv```


## Output
A nested list will be generated  
<br>
``` [ ["combustible_item1", ...], ["incombustible_item1", ...] ]```  
<br>
Index 0 - Combustible list  
Index 1 - Incombustible list

## Test Cases
```OriginURL/display/<picture_name>```  
<br>
e.g. if your link is ```http://127.0.0.1:5000/``` and the pic file name is cat.png, do ```http://127.0.0.1:5000/display/cat.png``` to see the picture that you have uploaded

## Credentials

Store keys in ```.aws``` folder  
Filename to store keys in is ```credentials``` (Follows the AWS SDK Documentation for Boto3)  
```
If you are using terminal:

cd
mkdir ./aws
cd ./aws
touch credentials
nano credentials

<< Text editor will pop up in the terminal, follow on screen instructions and save the file >>
```

## Usage with Localstack

Change the endpoint_url to your localstack link
```
endpoint_url = "http://localhost.localstack.cloud:4566"
...
session = boto3.Session(region_name='us-east-1')

s3 = session.client('s3', endpoint_url=endpoint_url)

```
 
