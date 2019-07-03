import boto3
from decimal import Decimal
import json
import urllib

def lambda_handler(event, context):
	try:
		# Get the object from the event
		bucket = event['Records'][0]['s3']['bucket']['name']
		key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
		
		print(bucket)
		print(key)

		rekognition = boto3.client('rekognition', region_name='us-east-1')
		dynamodb = boto3.client('dynamodb', region_name='us-east-1')
		sns = boto3.client('sns')

		response = rekognition.search_faces_by_image(
			CollectionId='infospace-emp',
			Image={"S3Object":
				{"Bucket": bucket,
				"Name": key}}
				)
		if response['FaceMatches']:
			for match in response['FaceMatches']:
				#print (match['Face']['FaceId'],match['Face']['Confidence'])
				print('inside')
				face = dynamodb.get_item(
					TableName='rbsemprepo',
					Key={'RekognitionId': {'S': match['Face']['FaceId']}}
					)
					
				if 'Item' in face:
					msg='Hello ' + face['Item']['FullName']['S'] + ' Welcome to RBS !!!'
					print(msg)
					response = sns.publish(
						TopicArn='arn:aws:sns:us-east-1:167771397877:RekognitionAlert',
						Message=msg
						)
				else:
					print ('no match found in person lookup')
					response = sns.publish(
						TopicArn='arn:aws:sns:us-east-1:167771397877:RekognitionAlert',
						Message='Familiar face..... BUT No Employee record.....Might be an ex-employee.....,'
						)

		else:
			print('Not an RBS Employee')
			response = sns.publish(TopicArn='arn:aws:sns:us-east-1:167771397877:RekognitionAlert',Message='Intruder Alert !!!')
	except Exception as e:
		print(e)
		print("Error processing {} from bucket {}. ".format(key, bucket))