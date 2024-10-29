import boto3
from tabulate import tabulate
import json
from datetime import datetime
import argparse
from dotenv import load_dotenv
import os
from typing import Tuple, List, Optional

load_dotenv()

def get_env_variables() -> Tuple[str, str]:
    aws_profile = os.getenv('AWS_PROFILE')
    table_name = os.getenv('DYNAMODB_CHAT_TABLE')

    missing_vars = []
    if not aws_profile:
        missing_vars.append('AWS_PROFILE')
    if not table_name:
        missing_vars.append('DYNAMODB_CHAT_TABLE')

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}\n"
                        f"Please set them in your .env file:")

    return aws_profile, table_name

def format_timestamp(timestamp: str) -> str:
    try:
        return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp

def get_dynamo_data(table_name: str, profile_name: Optional[str] = None) -> Tuple[List[str], List[List[str]]]:
    session = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
    dynamodb = session.client('dynamodb')

    try:
        response = dynamodb.scan(TableName=table_name)
    except Exception as e:
        raise Exception(f"Failed to scan DynamoDB table: {str(e)}")

    items = response['Items']

    # テーブルデータの準備
    table_data = []
    headers = ['Session ID', 'Expiration Time', 'Messages']

    for item in items:
        session_id = item['Sessionid']['S']
        expiration_time = format_timestamp(item.get('ExpirationTime', {}).get('N', 'N/A'))

        # メッセージの処理
        messages = []
        if 'Messages' in item:
            try:
                messages_str = item['Messages']['S']
                messages_list = json.loads(messages_str)
                messages = [f"{msg['type']}: {msg['data']['content'][:50]}..."
                            for msg in messages_list]
            except json.JSONDecodeError:
                messages = ['Error: Invalid JSON in messages']
            except KeyError:
                messages = ['Error: Unexpected message format']
            except Exception as e:
                messages = [f'Error parsing messages: {str(e)}']

        table_data.append([
            session_id,
            expiration_time,
            '\n'.join(messages[:2]) + ('\n...' if len(messages) > 2 else '')
        ])

    return headers, table_data

def main():
    try:
        aws_profile, table_name = get_env_variables()

        # コマンドライン引数のパーサー設定
        parser = argparse.ArgumentParser(description='Display DynamoDB table contents in tabular format')
        parser.add_argument('--table', help='Override DynamoDB table name from .env')
        parser.add_argument('--profile', help='Override AWS profile from .env')

        args = parser.parse_args()

        # コマンドライン引数が指定されている場合は環境変数より優先
        table_name = args.table or table_name
        aws_profile = args.profile or aws_profile

        print(f"\nUsing:")
        print(f"- Table: {table_name}")
        print(f"- AWS Profile: {aws_profile}\n")

        headers, data = get_dynamo_data(table_name, aws_profile)

        if not data:
            print("No data found in the table.")
            return

        print(tabulate(data, headers=headers, tablefmt='grid', maxcolwidths=[None, None, 50]))

    except ValueError as ve:
        print(f"Error: {str(ve)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
