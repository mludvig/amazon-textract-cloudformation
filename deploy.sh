#!/bin/bash -eu

# Deploy Textract demo
# Environment variables:
# - $AWS_DEFAULT_REGION (default: us-west-2)

echo "[*] Verifying deployment settings..."

## Figure out some defaults
STACK_NAME=${STACK_NAME:-textract-demo}
echo "[x] Stack name: ${STACK_NAME}"

export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-west-2}
echo "[x] Region: ${AWS_DEFAULT_REGION}"

AWS="aws --output=text --region ${AWS_DEFAULT_REGION}"
ACCOUNT_ID=$(${AWS} sts get-caller-identity --query 'Account')
echo "[x] Account ID: ${ACCOUNT_ID}"

## Create S3 Bucket
DEPLOYMENT_BUCKET=${1:-${STACK_NAME}-${ACCOUNT_ID}-${AWS_DEFAULT_REGION}}

# Do we have to create the bucket?
_BUCKETS=$(for _BUCKET in $(${AWS} s3api list-buckets --query 'Buckets[].Name'); do echo $_BUCKET; done)
if [ -z "$(grep "${DEPLOYMENT_BUCKET}" <<< ${_BUCKETS} || true)" ]; then
  echo -n "[!] Create bucket '${DEPLOYMENT_BUCKET}' ? [Y/n] "
  read ANS
  if [ -z "${ANS}" -o "${ANS:0:1}" = "Y" -o "${ANS:0:1}" = "y" ]; then
    ${AWS} s3api create-bucket --acl private --create-bucket-configuration LocationConstraint=${AWS_DEFAULT_REGION} --bucket ${DEPLOYMENT_BUCKET}
  else
    echo "You can set the bucket name as this script parameter."
    echo "For example: $0 textract-test-bucket"
    exit 1
  fi
fi
echo "[x] Deployment bucket: ${DEPLOYMENT_BUCKET}"

echo
echo "Press [Enter] to continue or Ctrl-C to abort."
read

TEMPLATE_FILE=$(mktemp /tmp/template-XXXXXXXX.yml)
aws cloudformation package \
	--template-file template.yml \
	--output-template-file ${TEMPLATE_FILE} \
	--s3-bucket ${DEPLOYMENT_BUCKET} \
	--s3-prefix "deploy"

aws cloudformation deploy \
	--template-file ${TEMPLATE_FILE} \
	--stack-name ${STACK_NAME} \
	--capabilities CAPABILITY_IAM \
  --parameter-overrides Bucket=${DEPLOYMENT_BUCKET}

rm -f ${TEMPLATE_FILE}

DESCRIBE_STACK=$(${AWS} cloudformation describe-stacks --stack-name ${STACK_NAME})
UPLOAD_DIR=$(awk '/^PARAMETERS\s+UploadPrefix/{print $3}' <<< ${DESCRIBE_STACK})
UPLOAD_URL=$(awk '/^OUTPUTS\s+UploadUrl/{print $3}' <<< ${DESCRIBE_STACK})
OUTPUT_DIR=$(awk '/^PARAMETERS\s+OutputPrefix/{print $3}' <<< ${DESCRIBE_STACK})
OUTPUT_URL=$(awk '/^OUTPUTS\s+OutputUrl/{print $3}' <<< ${DESCRIBE_STACK})

cat << __EOF__

All done. Now follow these steps:

1. Upload your test PDF to: ${UPLOAD_URL}
   Console URL: https://console.aws.amazon.com/s3/buckets/${DEPLOYMENT_BUCKET}/${UPLOAD_DIR}/?region=${AWS_DEFAULT_REGION}

2. Open the Step Function page to follow the progress
   Console URL: https://${AWS_DEFAULT_REGION}.console.aws.amazon.com/states/home?region=${AWS_DEFAULT_REGION}#/statemachines

3. When done download the results from: ${OUTPUT_URL}
   Console URL: https://console.aws.amazon.com/s3/buckets/${DEPLOYMENT_BUCKET}/${OUTPUT_DIR}/?region=${AWS_DEFAULT_REGION}

__EOF__
