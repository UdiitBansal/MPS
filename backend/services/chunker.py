from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)


class Chunker:

    def __init__(self):

        self.splitter = RecursiveCharacterTextSplitter(

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

    def split(self, text):

        if not text:
            return []

        text = text.strip()

        if len(text) == 0:
            return []

        chunks = self.splitter.split_text(text)

        cleaned_chunks = []

        for chunk in chunks:

            chunk = " ".join(chunk.split())

            if len(chunk) > 50:

                cleaned_chunks.append(chunk)

        return cleaned_chunks

    @staticmethod
    def split(text):

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

        chunks = splitter.split_text(text)

        cleaned_chunks = []

        for chunk in chunks:

            chunk = " ".join(chunk.split())

            if len(chunk) > 50:

                cleaned_chunks.append(chunk)

        return cleaned_chunks