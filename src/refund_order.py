import json
import os
import uuid

import boto3

from src.auth import get_caller_id

dynamodb = boto3.resource("dynamodb")
order_table = dynamodb.Table(os.environ["ORDER_TABLE"])
refund_table = dynamodb.Table(os.environ["REFUND_TABLE"])


def handler(event, context):
    """환불 요청 API.

    호출자는 Bearer 토큰으로 인증된다.
    취약점(비즈니스 로직 결함): 이미 환불된 주문인지 확인하지 않는다.
    "환불은 주문당 한 번"이라는 규칙이 코드에 없어, 같은 주문에 반복 요청하면
    호출할 때마다 새 환불이 처리된다(중복 환불). 이 규칙은 코드/문서 컨텍스트가 있어야
    위반 여부를 판단할 수 있다.
    """
    caller_id = get_caller_id(event)
    if not caller_id:
        return {
            "statusCode": 401,
            "body": json.dumps({"message": "Unauthorized"}),
        }

    order_id = event["pathParameters"]["orderId"]
    response = order_table.get_item(Key={"orderId": order_id})
    order = response.get("Item")
    if not order:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Order not found"}),
        }

    # 멱등성 검증 누락: 이미 환불된 주문인지 확인해야 하지만(order["refunded"] 등)
    # 그 검증이 없어 동일 주문에 대한 반복 환불이 매번 성공한다.
    refund_id = str(uuid.uuid4())
    refund_table.put_item(
        Item={
            "refundId": refund_id,
            "orderId": order_id,
            "amount": order.get("amount"),
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Refund processed",
                "refundId": refund_id,
                "orderId": order_id,
                "amount": str(order.get("amount")),
            }
        ),
    }
