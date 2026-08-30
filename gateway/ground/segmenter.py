import re

SENTENCE_END_RE = re.compile(r'[.!?]["\')\]]?\s')
ABBREVIATIONS = {"mr.", "mrs.", "dr.", "prof.", "e.g.", "i.e.", "vs.", "etc.", "u.s.", "u.k."}

class StreamingSegmenter:
    """
    State machine: OPEN -> STABLE -> COMMITTED
    - OPEN: buffer is accumulating, no sentence boundary confirmed yet
    - STABLE: a sentence-ending punctuation was seen, but we wait for one
              more token to guard against abbreviations / decimals ("Dr. Smith", "3.14")
    - COMMITTED: sentence is finalized and yielded for scoring; buffer resets
    """
    def __init__(self):
        self.buffer = ""
        self.state = "OPEN"
        self._pending_end_idx = None
        self._search_start_idx = 0

    def feed(self, token: str) -> list[str]:
        """Feed one streamed token/chunk. Returns list of newly COMMITTED sentences (usually 0 or 1)."""
        self.buffer += token
        committed = []

        while True:
            if self.state == "STABLE":
                # we already saw a candidate boundary; this new token confirms or invalidates it
                candidate = self.buffer[:self._pending_end_idx].strip()
                if self._looks_like_real_boundary(candidate):
                    committed.append(candidate)
                    self.buffer = self.buffer[self._pending_end_idx:].lstrip()
                    self.state = "OPEN"
                    self._pending_end_idx = None
                    self._search_start_idx = 0
                else:
                    self.state = "OPEN"  # false alarm (was an abbreviation/decimal), keep accumulating
                    self._search_start_idx = self._pending_end_idx

            match = SENTENCE_END_RE.search(self.buffer, self._search_start_idx)
            if match and self.state == "OPEN":
                self._pending_end_idx = match.end()
                self.state = "STABLE"
                if self._pending_end_idx < len(self.buffer):
                    continue # Try to resolve it immediately if we have more tokens
            break

        return committed

    def flush(self) -> str | None:
        """Call at end-of-stream to emit whatever remains in the buffer."""
        remainder = self.buffer.strip()
        self.buffer = ""
        self.state = "OPEN"
        return remainder if remainder else None

    def _looks_like_real_boundary(self, candidate: str) -> bool:
        last_word = candidate.split()[-1].lower() if candidate.split() else ""
        if last_word in ABBREVIATIONS:
            return False
        # guard against decimals like "3.14" being split at the "."
        if re.search(r'\d\.\s*$', candidate) is False and candidate.rstrip().endswith('.'):
            tail = candidate[-6:]
            if re.search(r'\d\.\d?$', tail):
                return False
        return True
