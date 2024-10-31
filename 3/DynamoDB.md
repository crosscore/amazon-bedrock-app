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

## テーブルの全項目を取得して削除
```
aws dynamodb scan \
    --table-name BedrockChatSessionTable \
    --attributes-to-get "Sessionid" \
    --query "Items[*].Sessionid.S" \
    --output text | \
while read sessionid; do
    aws dynamodb delete-item \
        --table-name BedrockChatSessionTable \
        --key "{\"Sessionid\": {\"S\": \"$sessionid\"}}"
    echo "Deleted item with Sessionid: $sessionid"
done
```

## テーブルを削除して再作成
### 1. テーブルの削除
```
aws dynamodb delete-table --table-name BedrockChatSessionTable
```

### 2. テーブルが完全に削除されるまで待機
```
aws dynamodb wait table-not-exists --table-name BedrockChatSessionTable
```

### 3. テーブルの再作成
```
aws dynamodb create-table \
    --table-name BedrockChatSessionTable \
    --attribute-definitions AttributeName=Sessionid,AttributeType=S \
    --key-schema AttributeName=Sessionid,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

## jqを組み合わせて整形
```
aws dynamodb scan \
    --table-name BedrockChatSessionTable \
    --profile ${AWS_PROFILE} \
    | jq -r '.Items[] | [.Sessionid.S, .ExpirationTime.N] | @tsv' \
    | column -t
```
