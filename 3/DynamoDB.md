## AWS CLIを使用してテーブルを作成
```
aws dynamodb create-table \
    --table-name BedrockChatSessionTable \
    --attribute-definitions AttributeName=Sessionid,AttributeType=S \
    --key-schema AttributeName=Sessionid,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --profile ${AWS_PROFILE}
```

## AWS CLIによるDynamoDBの全データ確認
```
aws dynamodb scan \
    --table-name BedrockChatSessionTable \
    --profile ${AWS_PROFILE}
```
