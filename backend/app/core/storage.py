import uuid
from pathlib import Path


class StorageService:
    def __init__(self):
        # MinIO backend settings available but unused for now;
        # local file storage is used until Docker/MinIO is available.
        self._local_storage = Path("/tmp/gweb-media")
        self._local_storage.mkdir(parents=True, exist_ok=True)

    def upload(self, data: bytes, filename: str, content_type: str = "") -> str:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
        object_name = f"{uuid.uuid4().hex}.{ext}"
        filepath = self._local_storage / object_name
        filepath.write_bytes(data)
        return object_name

    def get_url(self, object_name: str) -> str:
        if not object_name:
            return ""
        return f"/media/{object_name}"

    def delete(self, object_name: str) -> None:
        if not object_name:
            return
        filepath = self._local_storage / object_name
        if filepath.exists():
            filepath.unlink()


storage = StorageService()
