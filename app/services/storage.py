from uuid import uuid4
from azure.storage.blob.aio import BlobServiceClient

from app.config import app_config


def generate_unique_blob_name(file_name: str) -> str:
    """
    Generate a unique blob name using UUID and original file extension.

    Args:
        file_name: Original file name

    Returns:
        str: Unique blob name in format 'uuid.extension'
    """
    file_extension = file_name.split(".")[-1] if "." in file_name else ""
    return f"{uuid4()}.{file_extension}"


async def get_blob_service_client():
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={app_config.AZURE_STORAGE_ACCOUNT_NAME};"
        f"AccountKey={app_config.AZURE_STORAGE_ACCOUNT_KEY};"
        f"EndpointSuffix=core.windows.net"
    )
    return BlobServiceClient.from_connection_string(connection_string)


async def upload_statement_file(file: bytes, file_name: str) -> str:
    """
    Upload a file to Azure Blob Storage with a unique identifier.

    Args:
        file: The file content in bytes
        file_name: Original file name
    Returns:
        str: The unique blob name used for storage
    """
    unique_blob_name = generate_unique_blob_name(file_name)

    async with await get_blob_service_client() as client:
        blob_client = client.get_container_client("statements").get_blob_client(
            unique_blob_name
        )
        await blob_client.upload_blob(file)

    return unique_blob_name


if __name__ == "__main__":
    import asyncio

    asyncio.run(upload_statement_file(b"test", "test.txt"))
