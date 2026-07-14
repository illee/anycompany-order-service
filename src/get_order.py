import json

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("anycompany-orders")


def handler(event, context):
    # Returns order details for the given orderId
    order_id = event["pathParameters"]["orderId"]
    response = table.get_item(Key={"orderId": order_id})
    item = response.get("Item")
    if not item:
        return {"statusCode": 404, "body": json.dumps({"message": "Order not found"})}
    return {
        "statusCode": 200,
        "body": json.dumps({
            "orderId": item["orderId"],
            "status": item["status"],
            "amount": item["amount"],
        }),
    }
