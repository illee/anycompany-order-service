import json
import os

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["ORDER_TABLE"])


def handler(event, context):
    """주문 조회 API.

    취약점(IDOR): 호출자(X-Customer-Id)가 이 주문의 소유자인지 검증하지 않는다.
    orderId만 알면 누구나 타인의 주문을 조회할 수 있다.
    """
    order_id = event["pathParameters"]["orderId"]

    response = table.get_item(Key={"orderId": order_id})
    item = response.get("Item")
    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Order not found"}),
        }

    # 소유권 검증이 없다. item["customerId"] 와 호출자 신원을 비교해야 하지만 생략됨.
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "orderId": item["orderId"],
                "customerId": item.get("customerId"),
                "orderStatus": item.get("status"),
                "amount": str(item.get("amount")),
            }
        ),
    }
