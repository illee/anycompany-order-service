"""데모용 경량 인증. 실제 서비스라면 Cognito/JWT 검증기를 쓴다.

여기서는 하드코딩된 Bearer 토큰으로 호출자 신원(customerId)만 확립한다.
토큰은 '누가 호출했는가'는 알려주지만, '그 주문의 소유자인가'는 검증하지 않는다 —
그 소유권 검증 누락이 IDOR의 핵심이다.
"""

TOKENS = {
    "token-alice": "cust-A",
    "token-bob": "cust-B",
}


def get_caller_id(event):
    """Authorization: Bearer <token> 헤더에서 호출자 customerId를 반환. 없으면 None."""
    headers = event.get("headers") or {}
    auth = headers.get("Authorization") or headers.get("authorization") or ""
    if not auth.startswith("Bearer "):
        return None
    token = auth[len("Bearer "):].strip()
    return TOKENS.get(token)
