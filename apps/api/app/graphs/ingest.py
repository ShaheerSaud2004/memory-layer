def chunk_text(text: str, max_chars: int = 4000) -> list[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    parts: list[str] = []
    buf: list[str] = []
    size = 0
    for para in text.split("\n\n"):
        p = para.strip()
        if not p:
            continue
        if size + len(p) + 2 > max_chars:
            if buf:
                parts.append("\n\n".join(buf))
            buf = [p]
            size = len(p)
        else:
            buf.append(p)
            size += len(p) + 2
    if buf:
        parts.append("\n\n".join(buf))
    return parts or [text[:max_chars]]


def run_ingest_pipeline(content: str) -> list[str]:
    return chunk_text(content)
