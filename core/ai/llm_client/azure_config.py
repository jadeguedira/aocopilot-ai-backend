#services/azure_config.py

import os
import asyncio
from lightrag import LightRAG, QueryParam
from openai import AzureOpenAI

# 1. Azure OpenAI Setup

client = AzureOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("OPENAI_API_BASE")
    )

deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")