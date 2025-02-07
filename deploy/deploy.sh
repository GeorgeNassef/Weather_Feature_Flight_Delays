#!/bin/bash

# Exit on error
set -e

# Check for AWS CLI
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is required but not installed. Please install it first."
    exit 1
fi

# Check for required environment variables
if [ -z "$AWS_ACCOUNT_ID" ] || [ -z "$AWS_REGION" ] || [ -z "$EFS_ID" ] || [ -z "$SUBNET_ID" ] || [ -z "$SECURITY_GROUP_ID" ]; then
    echo "Required environment variables not set. Please set:"
    echo "  AWS_ACCOUNT_ID      (e.g., 123456789012)"
    echo "  AWS_REGION         (e.g., us-east-1)"
    echo "  EFS_ID            (e.g., fs-12345678)"
    echo "  SUBNET_ID         (e.g., subnet-abcd1234)"
    echo "  SECURITY_GROUP_ID (e.g., sg-abcd1234)"
    exit 1
fi

# Create ECR repository if it doesn't exist
echo "Creating ECR repository..."
aws ecr describe-repositories --repository-names weather-flight-analyzer || \
    aws ecr create-repository --repository-name weather-flight-analyzer

# Build and push Docker image
echo "Building and pushing Docker image..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker build -t weather-flight-analyzer ..
docker tag weather-flight-analyzer:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/weather-flight-analyzer:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/weather-flight-analyzer:latest

# Create ECS cluster if it doesn't exist
echo "Creating ECS cluster..."
aws ecs describe-clusters --clusters weather-flight-analyzer || \
    aws ecs create-cluster --cluster-name weather-flight-analyzer

# Create CloudWatch log group
echo "Creating CloudWatch log group..."
aws logs create-log-group --log-group-name /ecs/weather-flight-analyzer || true

# Replace variables in task definition
echo "Preparing task definition..."
sed -e "s/\${AWS_ACCOUNT_ID}/$AWS_ACCOUNT_ID/g" \
    -e "s/\${AWS_REGION}/$AWS_REGION/g" \
    -e "s/\${EFS_ID}/$EFS_ID/g" \
    fargate-task-definition.json > task-definition.json

# Register task definition
echo "Registering task definition..."
TASK_DEF_ARN=$(aws ecs register-task-definition \
    --cli-input-json file://task-definition.json \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo "Task definition registered: $TASK_DEF_ARN"

# Create or update ECS service
echo "Creating/updating ECS service..."
if aws ecs describe-services --cluster weather-flight-analyzer --services weather-flight-analyzer | grep "MISSING"; then
    # Create new service
    aws ecs create-service \
        --cluster weather-flight-analyzer \
        --service-name weather-flight-analyzer \
        --task-definition "$TASK_DEF_ARN" \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}"
else
    # Update existing service
    aws ecs update-service \
        --cluster weather-flight-analyzer \
        --service weather-flight-analyzer \
        --task-definition "$TASK_DEF_ARN"
fi

echo "Deployment completed successfully!"
echo "Note: You need to replace the subnet and security group IDs in this script with your actual values"
echo "You can monitor the deployment in the AWS Console:"
echo "https://$AWS_REGION.console.aws.amazon.com/ecs/home?region=$AWS_REGION#/clusters/weather-flight-analyzer"
