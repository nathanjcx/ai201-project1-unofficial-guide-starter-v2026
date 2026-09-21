"""
Stage 2: keep advice threads together so replies retain their context.

Short threads stay whole. Longer threads split between replies and repeat the
thread title. The original character-window chunker is retained below for
comparison; pass chunk_size=800 and overlap=120 to reproduce the starter.
"""

from dataclasses import dataclass
import re

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Keep short discussions whole; split longer ones between complete replies.

    CHUNK_SIZE is a soft limit including the repeated thread title. Reply text
    is not overlapped. A single oversized reply stays intact, even if it goes
    over the target. Documents without reply markers use paragraph boundaries.
    """
    if config.CHUNK_SIZE <= 0:
        raise ValueError("chunk size must be positive")

    chunks: list[Chunk] = []
    for doc in documents:
        text = doc.text.strip()
        if not text:
            continue

        pieces: list[str] = []
        if len(text) <= config.CHUNK_SIZE:
            pieces.append(text)
        else:
            sections = re.split(r"(?m)(?=^--- reply \d+\b)", text)
            if text.startswith("THREAD:") and len(sections) > 1:
                title = sections[0].strip()
                blocks = [section.strip() for section in sections[1:]]
            else:
                title = ""
                blocks = text.split("\n\n")

            current: list[str] = []
            for block in blocks:
                block = block.strip()
                if not block:
                    continue
                candidate = "\n\n".join(filter(None, [title, *current, block]))
                if current and len(candidate) > config.CHUNK_SIZE:
                    pieces.append("\n\n".join(filter(None, [title, *current])))
                    current = []
                current.append(block)
            if current:
                pieces.append("\n\n".join(filter(None, [title, *current])))

        for index, piece in enumerate(pieces):
            chunks.append(Chunk(piece, doc.source, index, "chunker.py::split_documents"))

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
