import json
import time
from pathlib import Path
from typing import List, Tuple, Dict, Any
from model import GlossToken, ResolvedStep, ParseResult
import config


class LexiconDispatcher:
    def __init__(
        self,
        words_file: Path = config.WORDS_FILE,
        glossary_file: Path = config.GLOSSARY_FILE,
        signfiles_dir: Path = config.SIGNFILES_DIR
    ):
        self.words = set()
        self.concepts = {}
        self.signfiles_dir = signfiles_dir

        if words_file.exists():
            with open(words_file, "r", encoding="utf-8") as f:
                self.words = {line.strip().lower() for line in f if line.strip()}

        if glossary_file.exists():
            with open(glossary_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.concepts = data.get("concepts", {})

    def resolve_assets(self, gloss: str) -> Tuple[str, List[str]]:
        gloss_lower = gloss.lower()

        # 1. Direct match
        if gloss_lower in self.words:
            return "direct", [gloss_lower]

        # 2. Concept match
        if gloss_lower in self.concepts:
            sigml = self.concepts[gloss_lower].get("sigml", [])
            if sigml and all(s.lower() in self.words for s in sigml):
                return "concept", [s.lower() for s in sigml]

        # 3. Compound resolution
        for w in self.words:
            if len(w) > 3 and gloss_lower.startswith(w):
                remainder = gloss_lower[len(w):]
                if remainder in self.words:
                    return "compound", [w, remainder]

        # 4. Fallback to fingerspell
        return "fingerspell", list(gloss_lower)

    def resolve_all(self, tokens: List[GlossToken]) -> List[ResolvedStep]:
        steps = []
        step_idx = 0

        for tok in tokens:
            tier, assets = self.resolve_assets(tok.gloss)

            if tier in ["direct", "concept", "compound"]:
                for asset_name in assets:
                    url = f"/static/signfiles/{asset_name}.mp4"
                    steps.append(ResolvedStep(
                        i=step_idx,
                        kind="sign",
                        gloss=tok.gloss,
                        role=tok.role,
                        tier=tier,
                        duration_ms=config.SIGN_DURATION_MS,
                        gap_ms=config.SIGN_GAP_MS,
                        asset=asset_name,
                        url=url
                    ))
                    step_idx += 1
            else:
                # Fingerspell
                word_len = len(assets)
                for pos, char in enumerate(assets, start=1):
                    if not char.isalnum():
                        continue
                    steps.append(ResolvedStep(
                        i=step_idx,
                        kind="letter",
                        gloss=tok.gloss,
                        role=tok.role,
                        tier="fingerspell",
                        duration_ms=config.FINGERSPELL_LETTER_MS,
                        gap_ms=config.FINGERSPELL_WORD_GAP_MS if pos == word_len else 0,
                        letter=char,
                        word=tok.gloss.lower(),
                        position=pos,
                        of=word_len
                    ))
                    step_idx += 1

        return steps

    def build_payload(self, parsed: ParseResult, asr: Any = None, mode: str = "text") -> Dict[str, Any]:
        start_t = time.time()
        resolved_steps = self.resolve_all(parsed.tokens)
        build_ms = round((time.time() - start_t) * 1000, 2)

        sequence_dicts = [s.as_dict() for s in resolved_steps]
        gloss_list = [t.gloss for t in parsed.tokens]

        sign_urls = list({s["url"] for s in sequence_dicts if s["kind"] == "sign"})
        letters = list({s["letter"] for s in sequence_dicts if s["kind"] == "letter"})

        tiers_count = {"direct": 0, "concept": 0, "compound": 0, "fingerspell": 0}
        for s in resolved_steps:
            tiers_count[s.tier] += 1

        total_steps = max(1, len(resolved_steps))
        fallback_ratio = round(tiers_count["fingerspell"] / float(total_steps), 3)

        source_info = {
            "lang": parsed.source_lang,
            "text": parsed.text,
            "degraded_parser": parsed.degraded,
        }
        if asr:
            source_info.update({
                "confidence": asr.confidence,
                "infer_ms": asr.infer_ms,
                "language_probability": asr.language_probability,
            })

        # Legacy fallback array
        legacy_flat = []
        for s in resolved_steps:
            if s.kind == "sign":
                legacy_flat.append(s.asset)
            else:
                legacy_flat.append(s.letter)

        return {
            "type": "isl.sequence",
            "version": "1.0",
            "id": f"{int(time.time()*1000)}",
            "mode": mode,
            "source": source_info,
            "gloss": gloss_list,
            "sequence": sequence_dicts,
            "assets": {
                "signs": sign_urls,
                "letters": letters,
                "letter_url_template": "/static/signfiles/{asset}.mp4",
                "timeout_ms": config.ASSET_TIMEOUT_MS,
            },
            "timing": {
                "sign_ms": config.SIGN_DURATION_MS,
                "sign_gap_ms": config.SIGN_GAP_MS,
                "letter_ms": config.FINGERSPELL_LETTER_MS,
                "word_gap_ms": config.FINGERSPELL_WORD_GAP_MS,
            },
            "stats": {
                "tokens": len(parsed.tokens),
                "steps": len(resolved_steps),
                "sign_steps": sum(1 for s in resolved_steps if s.kind == "sign"),
                "fingerspelled": sum(1 for s in resolved_steps if s.kind == "letter"),
                "tiers": tiers_count,
                "fallback_ratio": fallback_ratio,
                "build_ms": build_ms,
            },
            "legacy": {"final_response": legacy_flat},
        }