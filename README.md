# aws-bedrock-app

```
# activate venv
source venv/bin/activate

# configure sso settings
aws configure sso

# check AWS CLI profiles
aws configure list-profiles

# get CLI pfofile name
cat ~/.aws/config | grep profile

# login to sse session
aws sso login --profile $AWS_PROFILE

# check credentials
aws sts get-caller-identity --profile $AWS_PROFILE
```
