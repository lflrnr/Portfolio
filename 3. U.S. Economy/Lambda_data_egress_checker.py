import json
import boto3
from datetime import datetime, timedelta

def get_aws_egress_data_usage(start_date, end_date):
    client = boto3.client('ce', region_name='us-east-1')  # Create a Cost Explorer client

    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date.strftime('%Y-%m-%d'),
            'End': end_date.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Metrics=[
            'UsageQuantity'
        ],
        
        # Filtering by data egress
        Filter={
            'Dimensions': {
                'Key': 'USAGE_TYPE',
                'Values': [
                    'AmazonEC2: EC2: Data Transfer - Internet (Out)',
                    'AmazonS3:DataTransfer-Out-Bytes',
                    'AmazonRDS:DataTransfer-Out-Bytes',
                    'AmazonEC2: Amazon EBS - DataTransfer-Out-Bytes'
                ]
            }
        }
        
        # # Filtering by all data transfer
        # Filter={
        #     'Dimensions': {
        #         'Key': 'USAGE_TYPE',
        #         'Values': [
        #             'DataTransfer'
        #         ]
        #     }
        # }
    )

    total_usage = 0
    for result_by_time in response['ResultsByTime']:
        total_usage += float(result_by_time["Total"]["UsageQuantity"]["Amount"])

    return total_usage

def stop_ecs_service(cluster, service):
    ecs_client = boto3.client('ecs')
    
    response = ecs_client.update_service(
        cluster=cluster,
        service=service,
        desiredCount=0
    )
    return response

def lambda_handler(event, context):
    
    today = datetime.now().date()
    start_date = today - timedelta(days=1)  # Get usage for the last day
    end_date = today

    egress_data_usage = get_aws_egress_data_usage(start_date, end_date)
    print(f"Debug data: {egress_data_usage} ")

    # return egress_data_usage

    if egress_data_usage > 1: # units are in GB
    
        # Replace 'your_cluster_name' and 'your_service_name' with your actual ECS cluster and service names
        cluster = 'econdaily'
        service = 'econplotly'
    
        # Stop the ECS service
        stop_ecs_service(cluster, service)
        print(f'Stopped ECS service: {service}')
        
        # Send SNS notification of egress exceedence
        sns_client = boto3.client('sns', region_name='us-east-1')
        def send_sns_notification(message):
            response = sns_client.publish(
                TopicArn='arn:aws:sns:us-east-1:307103213532:egress-exceeds',
                Message=message
            )
            return response
        message = 'Plotly dashboard stopped due to exceeding egress memory limit!'
        send_sns_notification(message)
    
    else:
        pass

    return {
        'statusCode': 200,
        'body': 'Plotly dashboard stopped due to exceeding egress memory limit!'
    }
