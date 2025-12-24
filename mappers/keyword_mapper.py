from schemas.keyword import Keyword as SchemaKeyword
from domain.keyword import Keyword as DomainKeyword

def to_domain_keywords(schema_keywords: list[SchemaKeyword]) -> list[DomainKeyword]:
    return [DomainKeyword(keyword=kw.keyword, score=kw.score) for kw in schema_keywords]
