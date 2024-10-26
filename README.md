# aws-bedrock-app

```
# configure sso settings
aws configure sso

# check AWS CLI profiles
aws configure list-profiles

# get CLI pfofile name
cat ~/.aws/config | grep profile

# login to sse session
aws sso login --profile "CLI profile name"

# check credentials
aws sts get-caller-identity --profile "CLI profile name"
```
