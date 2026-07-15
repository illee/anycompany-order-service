# AnyCompany Order Service — 침투 테스트 데모 (2편)

> ⚠️ 의도적으로 취약점을 포함한 **데모 전용** 애플리케이션입니다. 격리된 자사 소유 환경에만
> 배포하고, AWS Security Agent 침투 테스트 시연이 끝나면 즉시 삭제하세요. 프로덕션 배포 금지.

## 심어둔 취약점

| 엔드포인트 | 취약점 | 설명 |
|---|---|---|
| `GET /orders/{orderId}` | IDOR | 호출자 소유권을 검증하지 않아 orderId만 바꾸면 타인 주문 조회 가능 |
| `POST /orders/{orderId}/refund` | 비즈니스 로직 결함 | 중복 환불 방지가 없어 같은 주문을 반복 환불 가능 |

API는 데모 단순화를 위해 `X-Customer-Id` 헤더로 호출자를 식별한다고 가정합니다(실제로는 검증에 쓰이지 않음 — 그게 IDOR의 핵심).

## 배포 (Isengard 계정 / us-east-1)

```bash
# 1) Isengard 자격증명으로 us-east-1 지정 후
sam build
sam deploy --guided \
  --stack-name anycompany-order-pentest \
  --region us-east-1 \
  --capabilities CAPABILITY_IAM
# StackName/Region 확인, 나머지는 기본값 진행

# 2) 배포 후 출력된 ApiBaseUrl 확보. 시드 데이터 주입:
curl -X POST "<ApiBaseUrl>/seed"

# 3) 취약점 개념 확인(선택):
curl "<ApiBaseUrl>/orders/order-1002" -H "X-Customer-Id: cust-A"   # IDOR: A가 B의 주문 조회
curl -X POST "<ApiBaseUrl>/orders/order-1001/refund"               # 반복 호출 시 매번 환불됨
```

`<ApiBaseUrl>`을 Security Agent 침투 테스트의 타깃 도메인으로 등록합니다.

## 정리

```bash
sam delete --stack-name anycompany-order-pentest --region us-east-1
```
