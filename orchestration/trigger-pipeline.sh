#!/bin/bash
# Manual trigger for GitHub ETL pipeline

STATE_MACHINE_ARN="arn:aws:states:us-east-1:338394181752:stateMachine:github-trending-etl-pipeline"

echo "Starting GitHub ETL pipeline..."

EXECUTION_ARN=$(aws stepfunctions start-execution \
  --state-machine-arn $STATE_MACHINE_ARN \
  --name "manual-$(date +%Y%m%d-%H%M%S)" \
  --query 'executionArn' \
  --output text)

echo "✓ Execution started: $EXECUTION_ARN"
echo ""
echo "Monitor execution:"
echo "  aws stepfunctions describe-execution --execution-arn $EXECUTION_ARN"
echo ""
echo "Or view in console:"
echo "  https://console.aws.amazon.com/states/home?region=us-east-1#/executions/details/$EXECUTION_ARN"
