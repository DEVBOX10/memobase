from datetime import datetime
from enum import IntEnum
from typing import Optional
from pydantic import BaseModel, UUID4
from .blob import BlobType
from . import blob as blob_models


class CODE(IntEnum):
    # Success
    SUCCESS = 0

    # Client-side errors (4xx)
    BAD_REQUEST = 400  # The request could not be understood by the server due to malformed syntax.
    UNAUTHORIZED = 401  # The request requires user authentication.
    FORBIDDEN = 403  # The server understood the request, but is refusing to fulfill it.
    NOT_FOUND = 404  # The server has not found anything matching the Request-URI.
    METHOD_NOT_ALLOWED = 405  # The method specified in the Request-Line is not allowed for the resource identified by the Request-URI.
    CONFLICT = 409  # The request could not be completed due to a conflict with the current state of the resource.
    UNPROCESSABLE_ENTITY = 422  # The server understands the content type of the request entity, and the syntax is correct, but it was unable to process the contained instructions.

    # Server-side errors (5xx)
    INTERNAL_SERVER_ERROR = 500  # The server encountered an unexpected condition which prevented it from fulfilling the request.
    NOT_IMPLEMENTED = 501  # The server does not support the functionality required to fulfill the request.
    BAD_GATEWAY = 502  # The server, while acting as a gateway or proxy, received an invalid response from the upstream server.
    SERVICE_UNAVAILABLE = 503  # The server is currently unable to handle the request due to a temporary overloading or maintenance of the server.
    GATEWAY_TIMEOUT = 504  # The server, while acting as a gateway or proxy, did not receive a timely response from the upstream server.


class IdData(BaseModel):
    id: UUID4


class UserData(BaseModel):
    data: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BlobData(BaseModel):
    blob_type: BlobType
    blob_data: dict  # messages/doc/images...
    fields: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_blob(self) -> blob_models.Blob:
        if self.blob_type == BlobType.chat:
            return blob_models.ChatBlob(**self.blob_data, fields=self.fields)
        elif self.blob_type == BlobType.doc:
            return blob_models.DocBlob(**self.blob_data, fields=self.fields)
        elif self.blob_type == BlobType.image:
            raise NotImplementedError("ImageBlob not implemented yet.")
        elif self.blob_type == BlobType.transcript:
            raise NotImplementedError("TranscriptBlob not implemented yet.")


class BaseResponse(BaseModel):
    data: Optional[dict] = None
    errno: CODE = CODE.SUCCESS
    errmsg: str = ""


class IdResponse(BaseResponse):
    data: Optional[IdData] = None


class UserDataResponse(BaseResponse):
    data: Optional[UserData] = None


class BlobDataResponse(BaseResponse):
    data: Optional[BlobData] = None
