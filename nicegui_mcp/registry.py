from __future__ import annotations

import re
from importlib import resources

from .models import SearchHit, TopicInfo
from .profile import TOPIC_BY_NAME, TOPICS, normalize_topic_name


def available_topics() -> list[TopicInfo]:
    return list(TOPICS)


def get_topic(topic: str) -> TopicInfo:
    normalized = normalize_topic_name(topic)
    try:
        return TOPIC_BY_NAME[normalized]
    except KeyError as exc:
        raise ValueError(f"Unknown topic: {topic}") from exc


def load_guidance_text(topic: str) -> str:
    normalized = normalize_topic_name(topic)
    try:
        with resources.files("nicegui_mcp.docs").joinpath(f"{normalized}.md").open("r", encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError as exc:
        raise ValueError(f"Unknown topic: {topic}") from exc


def search_guidance_text(query: str, topics: list[str] | None = None) -> list[SearchHit]:
    target_topics = [normalize_topic_name(topic) for topic in topics] if topics else [topic.name for topic in TOPICS]
    hits: list[SearchHit] = []
    terms = [term.casefold() for term in re.findall(r"[A-Za-z0-9_+-]+", query) if term.strip()]

    for topic_name in target_topics:
        topic = get_topic(topic_name)
        text = load_guidance_text(topic.name)
        for heading, body in _split_sections(text):
            haystack = body.casefold()
            heading_text = (heading or "").casefold()
            tag_text = " ".join(topic.tags).casefold()
            score = 0.0
            for term in terms:
                score += heading_text.count(term) * 4.0
                score += haystack.count(term) * 1.0
                score += topic.name.casefold().count(term) * 2.0
                score += tag_text.count(term) * 2.0
            if not terms:
                score = 1.0
            if score <= 0:
                continue
            hits.append(
                SearchHit(
                    topic=topic.name,
                    heading=heading,
                    snippet=_make_snippet(body, terms),
                    score=float(score),
                )
            )
    return sorted(hits, key=lambda hit: (-(hit.score or 0.0), hit.topic, hit.heading or ""))


def _split_sections(text: str) -> list[tuple[str | None, str]]:
    sections: list[tuple[str | None, str]] = []
    current_heading: str | None = None
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            if current_heading is not None or current_lines:
                sections.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = line.lstrip("#").strip() or None
            current_lines = [line]
            continue
        current_lines.append(line)
    if current_heading is not None or current_lines:
        sections.append((current_heading, "\n".join(current_lines).strip()))
    return [(heading, body) for heading, body in sections if body]


def _make_snippet(text: str, terms: list[str], width: int = 220) -> str:
    if not text:
        return ""
    if not terms:
        return text[:width].strip()
    lowered = text.casefold()
    positions = [lowered.find(term) for term in terms if lowered.find(term) >= 0]
    if not positions:
        return text[:width].strip()
    start = max(min(positions) - 50, 0)
    end = min(start + width, len(text))
    snippet = text[start:end].strip()
    if start > 0:
        snippet = f"...{snippet}"
    if end < len(text):
        snippet = f"{snippet}..."
    return snippet
