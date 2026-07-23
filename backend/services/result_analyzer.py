import re


class ResultAnalyzer:

    def __init__(self, chunks, metadata):
        self.chunks = chunks
        self.metadata = metadata

    def _get_rows(self):
        rows = []

        pattern = re.compile(
            r"([A-Za-z][A-Za-z\s]+?)\s+((?:\d+\s+){7,10})(\d{2,3})\s+(Pass|Fail|Not Eligible)",
            re.IGNORECASE
        )

        for chunk, meta in zip(self.chunks, self.metadata):

            for match in pattern.finditer(chunk):

                name = match.group(1).strip()

                total = int(match.group(3))

                status = match.group(4)

                rows.append({
                    "name": name,
                    "total": total,
                    "status": status,
                    "source": meta["source"]
                })

        return rows

    def topper(self, document=None):

        rows = self._get_rows()

        if document:
            rows = [
                r for r in rows
                if document.lower() in r["source"].lower()
            ]

        if not rows:
            return None

        return max(rows, key=lambda x: x["total"])

    def max_marks(self, document=None):
        return self.topper(document)

    def pass_count(self, document=None):

        rows = self._get_rows()

        if document:
            rows = [
                r for r in rows
                if document.lower() in r["source"].lower()
            ]

        return sum(
            1
            for r in rows
            if r["status"].lower() == "pass"
        )

    def student_count(self, document=None):

        rows = self._get_rows()

        if document:
            rows = [
                r for r in rows
                if document.lower() in r["source"].lower()
            ]

        return len(rows)