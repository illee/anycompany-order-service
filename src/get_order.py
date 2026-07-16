import json
import os

import boto3

from src.auth import get_caller_id

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["ORDER_TABLE"])


def handler(event, context):
    """주문 조회 API.

    호출자는 Bearer 토큰으로 인증된다(auth.get_caller_id).
    취약점(IDOR): 인증은 하지만, 조회한 주문이 '호출자 소유'인지 검증하지 않는다.
    order["customerId"] 와 호출자 신원을 비교해야 하지만 그 검증이 빠져 있어,
    인증된 사용자라면 누구나 orderId만 바꿔 타인의 주문을 조회할 수 있다.
    """
    caller_id = get_caller_id(event)
    if not caller_id:
        return {
            "statusCode": 401,
            "body": json.dumps({"message": "Unauthorized"}),
        }

    order_id = event["pathParameters"]["orderId"]
    response = table.get_item(Key={"orderId": order_id})
    item = response.get("Item")
    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Order not found"}),
        }

    # 소유권 검증 누락: if item["customerId"] != caller_id: return 403  <- 이 검증이 없다.
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
