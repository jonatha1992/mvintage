from typing import Any, Dict, Optional
import httpx

from app.core.config import settings


class PayAlertError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, code: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class PayAlertNotConfiguredError(PayAlertError):
    pass


class PayAlertClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        origin: Optional[str] = None,
        timeout: float = 15.0,
        http_client: Optional[httpx.Client] = None,
    ):
        self._base_url = base_url
        self._api_key = api_key
        self._origin = origin
        self._timeout = timeout
        self._http_client = http_client

    @property
    def base_url(self) -> str:
        return (self._base_url if self._base_url is not None else settings.PAYALERT_URL).rstrip("/")

    @property
    def api_key(self) -> str:
        return (self._api_key if self._api_key is not None else settings.PAYALERT_API_KEY).strip()

    @property
    def origin(self) -> str:
        return (self._origin if self._origin is not None else settings.PAYALERT_ORIGIN).strip()

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.base_url)

    def _headers(self) -> Dict[str, str]:
        if not self.is_configured:
            raise PayAlertNotConfiguredError("Mercado Pago no habilitado", status_code=503)
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Origin": self.origin,
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = self._headers()
        url = f"{self.base_url}{path}"
        try:
            if self._http_client is not None:
                resp = self._http_client.request(method, url, headers=headers, json=json_body, timeout=self._timeout)
            else:
                with httpx.Client(timeout=self._timeout) as client:
                    resp = client.request(method, url, headers=headers, json=json_body)
        except httpx.HTTPError as exc:
            raise PayAlertError(f"Error de conexión con PayAlert: {exc}", status_code=502) from exc

        payload: Dict[str, Any] = {}
        try:
            data = resp.json()
            if isinstance(data, dict):
                payload = data
        except ValueError:
            payload = {}

        if resp.status_code >= 400:
            code = payload.get("error") if isinstance(payload.get("error"), str) else None
            raise PayAlertError(
                code or f"PayAlert respondió {resp.status_code}",
                status_code=resp.status_code,
                code=code,
            )
        return payload

    def create_charge(
        self,
        order_id: int,
        amount: int,
        payer_ref: str,
        return_url: str,
        payer_email: Optional[str] = None,
        max_installments: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        exclude_cash: bool = True,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "bookingId": f"order-{order_id}",
            "payerRef": payer_ref,
            "amount": amount,
            "returnUrl": return_url,
        }
        if payer_email:
            body["payerEmail"] = payer_email
        if max_installments is not None:
            body["maxInstallments"] = max_installments
        if title:
            body["title"] = title
        if description:
            body["description"] = description[:255]
        body["excludeCash"] = exclude_cash
        try:
            return self._request("POST", "/api/v1/charges", json_body=body)
        except PayAlertError as exc:
            if exc.status_code != 400 or exc.code != "invalid_request":
                raise
            legacy_body = {k: v for k, v in body.items() if k not in ("title", "description", "excludeCash")}
            return self._request("POST", "/api/v1/charges", json_body=legacy_body)

    def get_charge(self, order_id: int) -> Dict[str, Any]:
        return self._request("GET", f"/api/v1/charges/order-{order_id}")

    def get_connection_status(self) -> Dict[str, Any]:
        return self._request("GET", "/api/v1/status")
