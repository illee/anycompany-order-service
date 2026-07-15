import json
import os

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["ORDER_TABLE"])


def handler(event, context):
    """데모용 시드 데이터 생성. 침투 테스트 전에 한 번 호출해 주문을 채운다.

    서로 다른 고객이 소유한 주문 두 건을 넣어, IDOR 재현 시
    'A 고객이 B 고객의 주문을 조회'하는 시나리오가 성립하도록 한다.
    """
    orders = [
        {"orderId": "order-1001", "customerId": "cust-A", "status": "DELIVERED", "amount": 50000},
        {"orderId": "order-1002", "customerId": "cust-B", "status": "DELIVERED", "amount": 99000},
    ]
    for o in orders:
        table.put_item(Item=o)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "seeded", "orders": [o["orderId"] for o in orders]}),
    }
