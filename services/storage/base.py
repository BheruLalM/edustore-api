from abc import ABC, abstractmethod


class Storage(ABC):

    @abstractmethod
    def generate_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
        expires_in: int = 300,
    ) -> str:
        pass

    @abstractmethod
    def generate_download_url(
        self,
        *,
        object_key: str,
        expires_in: int = 300,
    ) -> str:
        pass

    @abstractmethod
    def delete_object(self, *, object_key: str) -> None:
        pass
