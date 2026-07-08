from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)


class Chunker:

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=CHUNK_SIZE,

        chunk_overlap=CHUNK_OVERLAP,

        separators=[

            "\n\n",

            "\n",

            ". ",

            "? ",

            "! ",

            "; ",

            ", ",

            " "

        ],

        length_function=len,

        is_separator_regex=False

    )

    MIN_CHUNK_LENGTH = 50

    @classmethod
    def split(cls, text):

        if not text:

            return []

        text = " ".join(text.split())

        if not text:

            return []

        raw_chunks = cls.splitter.split_text(text)

        cleaned_chunks = []

        seen = set()

        for chunk in raw_chunks:

            chunk = " ".join(chunk.split()).strip()

            if len(chunk) < cls.MIN_CHUNK_LENGTH:

                continue

            # Skip chunks containing only numbers/symbols
            alpha_count = sum(c.isalpha() for c in chunk)

            if alpha_count < 20:

                continue

            key = chunk.lower()

            if key in seen:

                continue

            seen.add(key)

            cleaned_chunks.append(chunk)

        return cleaned_chunks