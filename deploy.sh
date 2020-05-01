#!/bin/bash -exu

source config.sh

LAMBDAS="lambda/start_job.py lambda/get_results.py"
for LAMBDA in ${LAMBDAS}; do
  echo "## ${LAMBDA}"
  pylint ${LAMBDA} || true
  pylint -E ${LAMBDA}
done

# ----

TEMPLATE_FILE=$(mktemp /tmp/template-XXXXXXXX.yml)

aws cloudformation package \
	--template-file template.yml \
	--output-template-file ${TEMPLATE_FILE} \
	--s3-bucket ${DEPLOYMENT_BUCKET}

aws cloudformation deploy \
	--template-file ${TEMPLATE_FILE} \
	--stack-name ${STACK_NAME} \
  --tags "Owner=Michael Ludvig" \
	--capabilities CAPABILITY_IAM \
  ${CFN_ROLE:+--role-arn ${CFN_ROLE}}

rm -f ${TEMPLATE_FILE}

BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name ${STACK_NAME} | jq -r '.Stacks[0].Outputs[]|select(.OutputKey=="Bucket").OutputValue')
aws s3 cp bnz-test.pdf s3://${BUCKET_NAME}/upload/
aws s3 cp invalid.pdf s3://${BUCKET_NAME}/upload/
