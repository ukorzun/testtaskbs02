from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict, UUID4


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HttpBinAnythingResponse(StrictBaseModel):
    args: Dict[str, Any] = Field(default_factory=dict)
    data: str = ""
    files: Dict[str, Any] = Field(default_factory=dict)
    form: Dict[str, Any] = Field(default_factory=dict)
    headers: Dict[str, Any] = Field(default_factory=dict)
    json: Optional[Dict[str, Any]] = None
    method: str
    origin: str
    url: str


class HttpBinUuidResponse(StrictBaseModel):
    uuid: UUID4


class HttpBinHeadersResponse(StrictBaseModel):
    headers: Dict[str, Any]
