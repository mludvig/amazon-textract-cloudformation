# Textract *with* Step Function *and* Cloud Formation

This is a complete setup for automatic text extraction from PDF / JPEG / PNG files
using [Amazon Textract](https://aws.amazon.com/textract/).

## Deployment

Check out this repository and run the included `deploy.sh` script.

It will create a new *S3 bucket* and the use *CloudFormation template* to
build the required resources.

```
$ ./deploy.sh
[*] Verifying deployment settings...
[x] Stack name: textract-demo
[x] Region: us-west-2
[x] Account ID: 123456789012
[x] Deployment bucket: textract-demo-123456789012-us-west-2

Press [Enter] to continue or Ctrl-C to abort.
```

When done follow these steps to test that it works:

1. *Upload your test PDF* to the `/upload` folder in the newly created S3 bucket.

2. *Open the Step Function page* to follow the progress

3. When done *download the results* from the `/output` folder in the bucket.

## Author

[Michael Ludvig](https://aws.nz)
