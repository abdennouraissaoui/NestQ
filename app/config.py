import os
import configparser

# Load the .ini configuration file
config = configparser.ConfigParser()
config.read("nestq.ini")


class Config:
    # Document Intelligence API
    DOC_INTEL_API_KEY = config["document-intelligence"]["API_KEY"]
    DOC_INTEL_ENDPOINT = config["document-intelligence"]["ENDPOINT"]

    # Azure OpenAI API
    AZURE_OPENAI_API_KEY = config["azure-openai"]["API_KEY"]
    AZURE_OPENAI_ENDPOINT = config["azure-openai"]["ENDPOINT"]


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = config["database"]["DEV_DB_URI"]


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = config["database"]["PROD_DB_URI"]


"""
Windows:
set NESTQ_ENV=development  # for development
set NESTQ_ENV=production   # for production

Linux/Macos:
export NESTQ_ENV=development  # for development
export NESTQ_ENV=production   # for production
"""

if os.getenv("NESTQ_ENV") == "production":
    app_config = ProductionConfig()
else:
    app_config = DevelopmentConfig()


if __name__ == "__main__":
    print(app_config.SQLALCHEMY_DATABASE_URI)
