# This Lambda function coordinates running the plotly script and the daily scraping script on the same EC2 instance ...
# in order to remain within the AWS free tier resource limits.

import json
import boto3
import time

ecs_client = boto3.client('ecs')

def stop_ecs_service(cluster, service):
    response = ecs_client.update_service(
        cluster=cluster,
        service=service,
        desiredCount=0
    )
    return response

def start_ecs_service(cluster, service):
    response = ecs_client.update_service(
        cluster=cluster,
        service=service,
        desiredCount=1
    )
    return response

def lambda_handler(event, context):
    # Replace 'your_cluster_name' and 'your_service_name' with your actual ECS cluster and service names
    cluster = 'econdaily'
    service = 'econplotly'
    task_definition = 'arn:aws:ecs:us-east-1:307103213532:task-definition/econdaily'

    # Stop the ECS service
    stop_ecs_service(cluster, service)
    print(f'Stopped ECS service: {service}')
    
    # Give ECS service time to fully stop
    time.sleep(120)
    
    # Try/except clause ensures the Plotly website keeps running on AWS even if daily database update has errors
    try:
        
        # Get the container instances in your cluster
        response = ecs_client.list_container_instances(cluster=cluster)
        container_instances = response['containerInstanceArns']
        
        # Run the ECS task using the first container instance in the list
        response1 = ecs_client.start_task(
            cluster=cluster,
            containerInstances=[container_instances[0]],
            taskDefinition=task_definition,
        )
    
        # The econdaily task takes about 7 minutes to run per prior log metrics
        time.sleep(600)
        
        # Generate task_id from prior response1 since stop task method needs specific task_id
        task_id = response1['tasks'][0]['taskArn'].split('/')[-1]
        print(task_id)
        
        # Stop the ECS task
        response2 = ecs_client.stop_task(
            cluster=cluster,
            task=task_id
        )
        
    except error as err:
        print(err)
        pass

    # Start the ECS service
    start_ecs_service(cluster, service)
    print(f'Started ECS service: {service}')

    return {
        'statusCode': 200,
        'body': 'Plotly paused, daily task ran, Plotly resumed.'
    }
