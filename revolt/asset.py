from __future__ import annotations

import mimetypes
from typing import TYPE_CHECKING

from .enums import AssetType
from .utils import Ulid

if TYPE_CHECKING:
    from io import IOBase

    from .state import State
    from .types import File as FilePayload


__all__ = ("Asset", "PartialAsset")

class Asset(Ulid):
    """Represents a file on revolt

    Attributes
    -----------
    id: :class:`str`
        The id of the asset
    tag: :class:`str`
        The tag of the asset, this corrasponds to where the asset is used
    size: :class:`int`
        Amount of bytes in the file
    filename: :class:`str`
        The name of the file
    height: Optional[:class:`int`]
        The height of the file if it is an image or video
    width: Optional[:class:`int`]
        The width of the file if it is an image or video
    content_type: :class:`str`
        The content type of the file
    type: :class:`AssetType`
        The type of asset it is
    url: :class:`str`
        The assets url
    """
    __slots__ = ("state", "id", "tag", "size", "filename", "content_type", "width", "height", "type", "url")

    def __init__(self, data: FilePayload, state: State):
        self.state: State = state

        self.id: str = data['_id']
        self.tag: str = data['tag']
        self.size: int = data['size']
        self.filename: str = data['filename']

        metadata = data['metadata']
        self.height: int | None
        self.width: int | None

        if metadata["type"] == "Image" or metadata["type"] == "Video":  # cannot use `in` because type narrowing will not happen
            self.height = metadata["height"]
            self.width = metadata["width"]
        else:
            self.height = None
            self.width = None

        self.content_type: str | None = data["content_type"]
        self.type: AssetType = AssetType(metadata["type"])

        base_url = self.state.api_info["features"]["autumn"]["url"]
        self.url: str = f"{base_url}/{self.tag}/{self.id}"

    async def read(self) -> bytes:
        """Reads the files content into bytes"""
        return await self.state.http.request_file(self.url)

    async def save(self, fp: IOBase) -> None:
        """Reads the files content and saves it to a file

        Parameters
        -----------
        fp: IOBase
            The file to write too.
        """
        fp.write(await self.read())

class PartialAsset(Asset):
    """Partial asset for when we get limited data about the asset

    Attributes
    -----------
    id: :class:`str`
        The id of the asset, this will always be ``"0"``
    size: :class:`int`
        Amount of bytes in the file, this will always be ``0``
    filename: :class:`str`
        The name of the file, this be always be ``""``
    height: Optional[:class:`int`]
        The height of the file if it is an image or video, this will always be ``None``
    width: Optional[:class:`int`]
        The width of the file if it is an image or video, this will always be ``None``
    content_type: Optional[:class:`str`]
        The content type of the file, this is guessed from the url's file extension if it has one
    type: :class:`AssetType`
        The type of asset it is, this always be ``AssetType.file``
    """

    def __init__(self, url: str, state: State):
        self.state: State = state
        self.id: str = "0"
        self.size: int = 0
        self.filename: str = ""
        self.height: int | None = None
        self.width: int | None = None
        self.content_type: str | None = mimetypes.guess_extension(url)
        self.type: AssetType = AssetType.file
        self.url: str = url
