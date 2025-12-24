#services/azure_llm.py

from core.ai.llm_client.azure_config import client, deployment_name

from datetime import datetime

# Definition of the function to call Azure OpenAI LLM

async def azure_llm(prompt, **kwargs): 

    image_data = kwargs.get("image_data", None)
    system_prompt = kwargs.get("system_prompt", None)
    
    messages=[]
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    if image_data:
        # Multimodal message (text + image)
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]
        })
    else:
        messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create( 
        model=deployment_name,  
        messages=messages,
        temperature=0.2,  # Lower temperature for more deterministic responses
        top_p=1.0,
        max_tokens=4096,
    )
    return response.choices[0].message.content

import json
import re
from domain.keyword import Keyword as DomainKeyword
from typing import List
from domain.document import Document
from infrastructure.logger import debug, write_log


async def ask_llm_for_ranked_documents(keywords: List[DomainKeyword], documents: List[Document], language_code: str) -> List[dict]:

    # 1. Format keywords
    keywords_str = "\n".join(
        [f"- {kw.keyword.lower()} (importance: {kw.score})" for kw in keywords]
    )
    # 2. Format documents
    documents_text = ""
    for doc in documents:
        doc_chunks = "\n\n".join([chunk.content for chunk in doc.chunks] or [])
        documents_text += f"\n--- Document: {doc.ao_id} ---\n{doc_chunks}\n"

    # 3. Prepare system prompt and user prompt
    
    # Get the language
    language_codes = {'fr' : 'french', 'en': 'english'}
    language = language_codes.get(language_code, 'english')

    system_prompt = (
        "You are an expert in analyzing professional documents (RAOs). "
        "Your task is to evaluate which RAO documents are the most relevant "
        "to answer a given call for tender (AO), based on weighted keywords."
        "Give the explanations in the language requested by the user."
    )

    prompt = (
        f"The call for tender contains the following important keywords:\n"
        f"{keywords_str}\n\n"
        "You are given extracts (chunks) from several RAO documents.\n"
        f"Rank the documents by relevance and give an explanation in {language}.\n"
        "For each relevant document, return ONLY the keywords from the list above exactly as written "
        "that are actually related to the document. Do NOT include synonyms or new terms.\n"
        "Order the keywords by relevance (most important first).\n"
        "Exclude documents that are not relevant at all.\n\n"
        "Return a VALID JSON array. Each element MUST be an object with exactly these keys:\n"
        "[{\"document\": \"<ao_id>\", \"explanation\": \"<why it matches>\", \"keywords\": [\"k1\", \"k2\", ... ]}, ...]\n\n"
        "Do not add any other keys or data outside this structure."
        f"Here are the document chunks:\n{documents_text}"
    )

    write_log(
        msg=prompt,
        header=f'Prompt associated to {keywords_str}',
        file_name="ranking_prompts.log",
    )

    # 4. Call LLM
    response = await azure_llm(prompt, system_prompt=system_prompt)

    # 5. Clean up response
    cleaned = response.strip() #Removes leading and trailing spaces

    # Remove markdown fences if present
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    # Try parsing directly
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        debug(f"[ERROR] Failed to parse LLM response: {cleaned}")
        write_log(
            msg=f"Failed to parse LLM response:\n{cleaned}",
            header="LLM Response Error",
            file_name="response_LLMs.log",
        )
        return [] # Fallback to empty list if parsing fails
    
