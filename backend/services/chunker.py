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

    @classmethod
    def split(cls, text):

        if not text:

            return []

        text = text.strip()

        if not text:

            return []

        chunks = cls.splitter.split_text(text)

        cleaned_chunks = []

        for chunk in chunks:

            chunk = " ".join(chunk.split())

            if len(chunk) >= 50:

                cleaned_chunks.append(chunk)

        return cleaned_chunks