from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

@dataclass
class ASRResult:
    text: str
    language: str
    language_probability: float
    confidence: float
    duration_s: float
    infer_ms: float
    is_hallucination: bool = False
    model: str = "base"
    notes: List[str] = field(default_factory=list)
    ok: bool = True

    def as_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if not self.notes:
            d.pop("notes", None)
        return d

@dataclass
class GlossToken:
    gloss: str
    role: str
    display: str
    surface: str
    source_lang: str
    index: int
    meta: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ParseResult:
    tokens: List[GlossToken]
    source_lang: str
    text: str
    degraded: bool = False
    notes: List[str] = field(default_factory=list)

@dataclass
class ResolvedStep:
    i: int
    kind: str  # "sign" or "letter"
    gloss: str
    role: str
    tier: str  # "direct", "concept", "compound", "fingerspell"
    duration_ms: int
    gap_ms: int
    asset: Optional[str] = None
    url: Optional[str] = None
    letter: Optional[str] = None
    word: Optional[str] = None
    position: Optional[int] = None
    of: Optional[int] = None

    def as_dict(self) -> Dict[str, Any]:
        res = {
            "i": self.i,
            "kind": self.kind,
            "gloss": self.gloss,
            "role": self.role,
            "tier": self.tier,
            "duration_ms": self.duration_ms,
            "gap_ms": self.gap_ms,
        }
        if self.kind == "sign":
            res["asset"] = self.asset
            res["url"] = self.url
        elif self.kind == "letter":
            res["letter"] = self.letter
            res["word"] = self.word
            res["position"] = self.position
            res["of"] = self.of
        return res