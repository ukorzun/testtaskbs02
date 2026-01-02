from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from framework.http_client import HttpClient
from framework.models import HttpBinAnythingResponse, HttpBinHeadersResponse, HttpBinUuidResponse


@dataclass(frozen=True)
class HttpBinApi:
    client: HttpClient

    def uuid(self) -> HttpBinUuidResponse:
        r = self.client.get("/uuid", headers={"Accept": "application/json"})
        r.raise_for_status()
        return HttpBinUuidResponse.model_validate(r.json())

    def anything_get(
        self,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        accept: Optional[str] = None,
    ):
        hdrs = dict(headers or {})
        if accept:
            hdrs["Accept"] = accept
        return self.client.get("/anything", params=params, headers=hdrs or None)

    def anything_post_json(
        self,
        payload: Dict[str, Any],
        *,
        headers: Optional[Dict[str, str]] = None,
    ) -> HttpBinAnythingResponse:
        hdrs = {"Content-Type": "application/json"}
        if headers:
            hdrs.update(headers)
        r = self.client.post("/anything", json=payload, headers=hdrs)
        r.raise_for_status()
        return HttpBinAnythingResponse.model_validate(r.json())

    def anything_post_form(self, form: Dict[str, Any]) -> HttpBinAnythingResponse:
        r = self.client.post("/anything", data=form)
        r.raise_for_status()
        return HttpBinAnythingResponse.model_validate(r.json())

    def headers(self) -> HttpBinHeadersResponse:
        r = self.client.get("/headers", headers={"Accept": "application/json"})
        r.raise_for_status()
        return HttpBinHeadersResponse.model_validate(r.json())
