from dataclasses import dataclass


@dataclass
class Chunk:
    id: str
    text: str
    title: str
    content_id: int
    content_type: str
    language: str
    page_url: str = ""


def chunk_news(article: dict) -> list[Chunk]:
    chunks = []
    base_id = f"news_{article['id']}"
    for lang in ["zh", "en"]:
        title_key = f"title_{lang}"
        summary_key = f"summary_{lang}"
        content_key = f"content_{lang}"
        if title_key not in article:
            continue
        header = f"{article.get(title_key, '')} {article.get(summary_key, '')}"
        chunks.append(Chunk(
            id=f"{base_id}_header_{lang}",
            text=header,
            title=article.get(title_key, ""),
            content_id=article["id"],
            content_type="news",
            language=lang,
            page_url=f"/news/{article['id']}",
        ))
        body = article.get(content_key, "")
        if body:
            for i in range(0, len(body), 500):
                chunks.append(Chunk(
                    id=f"{base_id}_{lang}_{i//500}",
                    text=body[i:i+550],
                    title=article.get(title_key, ""),
                    content_id=article["id"],
                    content_type="news",
                    language=lang,
                    page_url=f"/news/{article['id']}",
                ))
    return chunks


def chunk_faq(faq: dict) -> list[Chunk]:
    chunks = []
    for lang in ["zh", "en"]:
        q_key = f"question_{lang}"
        a_key = f"answer_{lang}"
        if q_key in faq:
            chunks.append(Chunk(
                id=f"faq_{faq['id']}_{lang}",
                text=f"Q: {faq.get(q_key, '')}\nA: {faq.get(a_key, '')}",
                title=faq.get(q_key, ""),
                content_id=faq["id"],
                content_type="faq",
                language=lang,
            ))
    return chunks


def chunk_page_block(block: dict) -> list[Chunk]:
    content = block.get("content", {})
    text_parts = []
    for val in content.values():
        if isinstance(val, str):
            text_parts.append(val)
    text = " ".join(text_parts)
    if not text.strip():
        return []
    return [Chunk(
        id=f"block_{block['id']}",
        text=text,
        title=f"Block: {block.get('type', '')}",
        content_id=block["id"],
        content_type="page_block",
        language="zh",
    )]
