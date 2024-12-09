import os
from typing import Any, Dict
import configparser
from urllib.parse import unquote


def load_config() -> Dict[str, Any]:
    config = {}
    if os.path.exists("app/nestq.ini"):
        ini_config = configparser.ConfigParser()
        ini_config.optionxform = str  # Preserve case of keys
        with open("app/nestq.ini", "r") as f:
            ini_config.read_string(f.read().replace("%", "%%"))
        for section in ini_config.sections():
            for key, value in ini_config[section].items():
                config[f"{section.upper()}_{key.upper()}"] = unquote(value)
    return config


local_config = load_config()


class Config:
    # Document Intelligence API
    DOC_INTEL_API_KEY = os.getenv(
        "DOCUMENT_INTELLIGENCE_API_KEY"
    ) or local_config.get("DOCUMENT-INTELLIGENCE_API_KEY")
    DOC_INTEL_ENDPOINT = os.getenv(
        "DOCUMENT_INTELLIGENCE_ENDPOINT"
    ) or local_config.get("DOCUMENT-INTELLIGENCE_ENDPOINT")

    # Azure OpenAI API
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY") or local_config.get(
        "AZURE-OPENAI_API_KEY"
    )
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT") or local_config.get(
        "AZURE-OPENAI_ENDPOINT"
    )

    AZURE_COMMUNICATION_API_KEY = os.getenv(
        "AZURE_COMMUNICATION_API_KEY"
    ) or local_config.get("AZURE-COMMUNICATION_API_KEY")

    AZURE_COMMUNICATION_ENDPOINT = os.getenv(
        "AZURE_COMMUNICATION_ENDPOINT"
    ) or local_config.get("AZURE-COMMUNICATION_ENDPOINT")
    EMAIL_SENDER_ADDRESS = os.getenv("EMAIL_SENDER_ADDRESS") or local_config.get(
        "AZURE-COMMUNICATION_EMAIL_SENDER_ADDRESS"
    )

    RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.7"))

    SALT = os.getenv("AUTH_SALT") or local_config.get("AUTH_SALT")
    AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY") or local_config.get(
        "AUTH_SECRET_KEY"
    )
    AUTH_ALGORITHM = os.getenv("AUTH_ALGORITHM") or local_config.get(
        "AUTH_ALGORITHM", "HS256"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
        or local_config.get("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", "10")
    )

    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or local_config.get(
        "DATABASE_DEV_DB_URI"
    )

    FRONTEND_URL = os.getenv("FRONTEND_URL") or local_config.get("FRONTEND_URL")


app_config = Config()


if __name__ == "__main__":
    print(app_config.SQLALCHEMY_DATABASE_URI)
