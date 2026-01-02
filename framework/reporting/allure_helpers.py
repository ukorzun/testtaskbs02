from __future__ import annotations

import json
from typing import Any, Dict, Optional

import requests

try:
    import allure
except Exception:  # pragma: no cover
    allure = None


def _safe_json(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)
    except Exception:
        return str(obj)


def attach_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    body: Any = None,
) -> None:
    if allure is None:
        return
    allure.attach(method.upper(), name="request.method", attachment_type=allure.attachment_type.TEXT)
    allure.attach(url, name="request.url", attachment_type=allure.attachment_type.TEXT)
    if headers:
        allure.attach(_safe_json(dict(headers)), name="request.headers", attachment_type=allure.attachment_type.JSON)
    if params:
        allure.attach(_safe_json(dict(params)), name="request.params", attachment_type=allure.attachment_type.JSON)
    if body is not None:
        if isinstance(body, (dict, list)):
            allure.attach(_safe_json(body), name="request.body", attachment_type=allure.attachment_type.JSON)
        else:
            allure.attach(str(body), name="request.body", attachment_type=allure.attachment_type.TEXT)


def attach_response(resp: requests.Response, max_body_chars: int = 10000) -> None:
    if allure is None:
        return
    allure.attach(str(resp.status_code), name="response.status", attachment_type=allure.attachment_type.TEXT)
    try:
        allure.attach(_safe_json(dict(resp.headers)), name="response.headers", attachment_type=allure.attachment_type.JSON)
    except Exception:
        pass

    try:
        body = resp.text or ""
    except Exception:
        body = "<unreadable>"

    if len(body) > max_body_chars:
        body = body[:max_body_chars] + "\n...<truncated>..."

    try:
        j = resp.json()
        allure.attach(_safe_json(j), name="response.body.json", attachment_type=allure.attachment_type.JSON)
    except Exception:
        allure.attach(body, name="response.body", attachment_type=allure.attachment_type.TEXT)
