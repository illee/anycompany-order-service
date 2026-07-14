# AnyCompany Order Service

AnyCompany 이커머스의 주문 조회 서비스입니다. AWS Lambda와 Amazon DynamoDB로 구성됩니다.

## API

### GET /orders/{orderId}

주문 정보를 조회합니다.

응답 예시:

```json
{
  "orderId": "ORD-2026-001234",
  "orderStatus": "DELIVERED",
  "amount": 45000
}
```

> **주의:** 응답의 `orderStatus` 필드는 결제 서비스(anycompany-payment-service)가
> 환불 처리 전 주문 상태 검증에 사용합니다. 필드명 변경 시 하위 호환을 유지해야 합니다.

## 배포

AWS SAM으로 배포합니다.

```bash
sam build && sam deploy
```

