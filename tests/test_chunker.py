"""Boundary and content-preservation checks; no model calls are needed."""

import unittest
from unittest.mock import patch

from chunker import split_documents
from ingest import Document, load_documents


class ThreadChunkingTests(unittest.TestCase):
    def test_short_thread_has_no_overlapping_tail(self):
        text = "THREAD: Sample?\n\n--- reply 1 (2 votes) ---\n" + "A" * 710 + "."
        chunks = split_documents([Document("sample.txt", text)])
        self.assertEqual([c.text for c in chunks], [text])

    def test_long_thread_keeps_title_and_every_reply_once(self):
        title = "THREAD: How does this work?"
        replies = [f"--- reply {i} (2 votes) ---\n" + (f"Reply {i}. " * 10).strip()
                   for i in range(1, 5)]
        text = "\n\n".join([title, *replies])
        with patch("config.CHUNK_SIZE", 260):
            chunks = split_documents([Document("long.txt", text)])
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(c.text.startswith(title + "\n\n") for c in chunks))
        self.assertTrue(all(len(c.text) <= 260 for c in chunks))
        bodies = "\n\n".join(c.text[len(title) + 2:] for c in chunks)
        self.assertEqual(bodies, "\n\n".join(replies))
        self.assertEqual([c.label for c in chunks],
                         [f"long.txt#{i}" for i in range(len(chunks))])

    def test_oversized_reply_is_preserved(self):
        title = "THREAD: Long answer?"
        reply = "--- reply 1 (2 votes) ---\n" + "Whole sentence. " * 100
        text = f"{title}\n\n{reply}".strip()
        self.assertEqual(split_documents([Document("long.txt", text)])[0].text, text)

    def test_paragraphs_and_empty_documents(self):
        paragraphs = ["First sentence. " * 20, "Second sentence. " * 20]
        text = "\n\n".join(p.strip() for p in paragraphs)
        with patch("config.CHUNK_SIZE", 400):
            chunks = split_documents([Document("empty.txt", "  "), Document("plain.md", text)])
        self.assertEqual([c.text for c in chunks], [p.strip() for p in paragraphs])

    def test_all_actual_threads_keep_their_full_content(self):
        docs = load_documents("advice_threads")
        chunks = split_documents(docs)
        self.assertEqual(len(chunks), len(docs))
        self.assertEqual({c.source: c.text for c in chunks}, {d.source: d.text for d in docs})
        self.assertTrue(all(c.produced_by == "chunker.py::split_documents" for c in chunks))

    def test_invalid_size_fails_clearly(self):
        with patch("config.CHUNK_SIZE", 0):
            with self.assertRaises(ValueError):
                split_documents([Document("sample.txt", "text")])


if __name__ == "__main__":
    unittest.main()
