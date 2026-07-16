# AnyCompany Order Service — 침투 테스트 데모 (2편)

> ⚠️ 의도적으로 취약점을 포함한 **데모 전용** 애플리케이션입니다. 격리된 자사 소유 환경에만
> 배포하고, AWS Security Agent 침투 테스트 시연이 끝나면 즉시 삭제하세요. 프로덕션 배포 금지.

## 애플리케이션 개요

주문 조회·환불 API를 제공하는 서비스. 호출자는 Bearer 토큰으로 인증합니다(데모용 하드코딩 토큰).

**비즈니스 규칙(중요):**
- 주문 조회는 **해당 주문의 소유 고객만** 조회할 수 있어야 한다.
- 환불은 **주문당 한 번만** 처리되어야 한다(중복 환불 금지).

이 규칙들은 코드에 강제되어 있지 않다 — 그게 아래 취약점의 핵심이다.

## 인증

| 토큰 | 고객 |
|---|---|
| `token-alice` | cust-A |
| `token-bob` | cust-B |

요청 헤더: `Authorization: Bearer token-alice`

## 심어둔 취약점

| 엔드포인트 | 취약점 | 설명 |
|---|---|---|
| `GET /orders/{orderId}` | IDOR | 인증은 하지만 주문 소유권을 검증하지 않아, 인증된 사용자가 타인 주문을 조회 가능 |
| `POST /orders/{orderId}/refund` | 비즈니스 로직 결함 | 중복 환불 방지가 없어 같은 주문을 반복 환불 가능 |

## 배포 (계정 057493959099 / us-east-1)

```bash
sam build
sam deploy \
  --stack-name anycompany-order-pentest \
  --region us-east-1 \
  --capabilities CAPABILITY_IAM \
  --resolve-s3 --no-confirm-changeset

# 배포 후 출력된 ApiBaseUrl 확보. 시드 데이터 주입:
curl -X POST "<ApiBaseUrl>/seed"
```

## 취약점 개념 확인 (선택)

```bash
BASE="<ApiBaseUrl>"
# IDOR: alice로 인증하고 bob 소유 주문(order-1002) 조회 → 200 반환되면 취약
curl "$BASE/orders/order-1002" -H "Authorization: Bearer token-alice"
# 중복 환불: 같은 주문에 반복 → 매번 성공하면 취약
curl -X POST "$BASE/orders/order-1001/refund" -H "Authorization: Bearer token-alice"
# 인증 없음 → 401
curl "$BASE/orders/order-1001"
```

`<ApiBaseUrl>`을 Security Agent 침투 테스트의 타깃 도메인으로 등록합니다.

## 정리

```bash
sam delete --stack-name anycompany-order-pentest --region us-east-1
```
