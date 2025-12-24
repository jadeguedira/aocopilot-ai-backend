# infrastructure/analyzer_engine.py

from infrastructure.azure_llm import azure_llm
from domain.keyword import Keyword

async def summarize(text: str, language_code: str) -> str:

    # Get the right language
    language_codes = {'fr' : 'french', 'en': 'english'}
    language = language_codes.get(language_code, 'english')

    system_prompt = (
    "You are a professional summarizer assistant. Your goal is to analyze multiple documents provided by the user "
    "and generate a clear, concise, and well-structured summary that captures the key ideas, facts, and arguments across all the files"
    "The summary must always be a single paragraph of about 5 sentences, written in natural, fluent style, in the language requested by the user. "
    "Do not use bullet points or multiple paragraphs."
)

    prompt = f"""
    Below is the full text extracted from multiple documents.

     Please write a single-paragraph summary in {language} that :
    - Highlights the main themes and topics
    - Includes the most important facts, insights, or arguments
    - Flows naturally as one paragraph (around 5 sentences)
    
    Do not format with bullet points. Do not split into multiple paragraphs.

    --- DOCUMENT START ---
    {text}
    """

    try:
        summary = await azure_llm(prompt, system_prompt=system_prompt)
    except Exception as e:
        print(f"Error calling azure_llm: {e}")
        summary = "ERROR: LLM call failed."

    return summary

async def extract_keywords(text: str) -> list:
    system_prompt = (
        "You are a keyword extraction assistant for a RAG-based document retrieval system. "
        "For all the document provided, extract a list of 10 to 15 keywords. Choose both: "
        "1. Direct keywords (explicitly present). "
        "2. Related keywords (semantically linked). "
        "Each keyword must have a relevance score from 1 to 3."
        "The answer should only contain the keywords with their score, without any additional text, in the following format."
        "keyword1:score1\nkeyword2:score2\n...\nkeywordN:scoreN"
    )

    prompt = f"""
    Please process the following document. Generate a list of 10 to 15 keywords.

    --- DOCUMENT START ---
    {text}"""

    keywords: list[Keyword] = []

    try:
        keywords_str  = await azure_llm(prompt, system_prompt=system_prompt)
        for line in keywords_str.strip().splitlines():
            if ':' in line:
                keyword, score = line.rsplit(':', 1)
                keywords.append(Keyword(keyword.strip(), int(score.strip())))
    except Exception as e:
        print(f"Error calling azure_llm: {e}")
        keywords = []
    
    return keywords