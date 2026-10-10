import json
import re
from pathlib import Path
from model import GlossToken, ParseResult
import config

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class ISLGlossParser:
    def __init__(self, glossary_file: Path = config.GLOSSARY_FILE):
        self.spacy_nlp = None
        self.degraded = False
        self.hi_forms = {}
        self.concepts = {}

        if SPACY_AVAILABLE:
            try:
                self.spacy_nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.degraded = True
        else:
            self.degraded = True

        if glossary_file.exists():
            with open(glossary_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.hi_forms = data.get("hi_forms", {})
                self.concepts = data.get("concepts", {})

        # Mapping common Devanagari phrases/words to English sign assets
        self.hi_to_en_map = {
            "नमस्ते": "HELLO",
            "धन्यवाद": "THANKYOU",
            "शुक्रिया": "THANKYOU",
            "थैंक्यू": "THANKYOU",
            "पानी": "WATER",
            "खाना": "FOOD",
            "घर": "HOME",
            "स्कूल": "SCHOOL",
            "अस्पताल": "CLINIC",
            "डॉक्टर": "DOCTOR",
            "हाँ": "YES",
            "नहीं": "NO",
            "रुको": "STOP",
            "मदद": "HELP-ME",
            "दोस्त": "FRIEND",
            "भाई": "BROTHER",
            "बहन": "SISTER",
            "माँ": "MOTHER",
            "पिता": "FATHER",
            "यह": "THIS",
            "क्या": "WHAT",
            "कहाँ": "WHERE",
            "कब": "WHEN",
        }

    def warmup(self) -> dict:
        if self.spacy_nlp:
            self.spacy_nlp("warmup sentence")
        return {"spacy": self.spacy_nlp is not None, "degraded": self.degraded}

    def _is_devanagari(self, text: str) -> bool:
        return bool(re.search(r'[\u0900-\u097F]', text))

    def parse(self, text: str, lang: str = "auto") -> ParseResult:
        text = text.strip()
        if not text:
            return ParseResult(tokens=[], source_lang=lang, text=text, degraded=self.degraded)

        # Check for fusion before parsing
        text_fused = re.sub(r'\bthank\s+you\b', 'thankyou', text, flags=re.I)
        text_fused = re.sub(r'\bthank-you\b', 'thankyou', text_fused, flags=re.I)

        is_hindi = self._is_devanagari(text_fused) or (lang == "hi")

        if is_hindi:
            return self._parse_hindi(text_fused)
        else:
            return self._parse_english(text_fused)

    def _parse_english(self, text: str) -> ParseResult:
        notes = []

        if self.spacy_nlp:
            doc = self.spacy_nlp(text)
            buckets = {
                "WH": [], "TIME": [], "SUBJECT": [], "OBJECT": [],
                "LOCATION": [], "NEG": [], "VERB": [], "ADV": [], "OTHER": []
            }

            for token in doc:
                word_lower = token.text.lower()
                
                if token.pos_ in ["DET"] or word_lower in ["a", "an", "the", "is", "am", "are", "was", "were", "be", "been"]:
                    continue
                if word_lower in ["have", "has", "had"] and token.dep_ in ["aux", "ROOT"]:
                    continue

                role = "OTHER"
                if token.dep_ in ["nsubj", "nsubjpass"]:
                    role = "SUBJECT"
                elif token.dep_ in ["dobj", "pobj", "obj"]:
                    if token.ent_type_ in ["DATE", "TIME"]:
                        role = "TIME"
                    elif token.head.dep_ == "prep" and token.head.text.lower() in ["in", "at", "to", "from"]:
                        role = "LOCATION"
                    else:
                        role = "OBJECT"
                elif token.dep_ == "neg" or word_lower in ["not", "no", "never"]:
                    role = "NEG"
                elif token.pos_ == "VERB" or token.dep_ == "ROOT":
                    role = "VERB"
                elif token.pos_ == "ADV":
                    role = "ADV"
                elif token.tag_ == "WP" or word_lower in ["what", "where", "when", "why", "how", "who"]:
                    role = "WH"

                gloss_text = token.lemma_.upper() if token.pos_ == "VERB" else token.text.upper()
                token_obj = GlossToken(
                    gloss=gloss_text,
                    role=role,
                    display=gloss_text,
                    surface=token.text,
                    source_lang="en",
                    index=token.i
                )
                buckets[role].append(token_obj)

            ordered_tokens = []
            for r in ["WH", "TIME", "SUBJECT", "OBJECT", "LOCATION", "NEG", "VERB", "ADV", "OTHER"]:
                ordered_tokens.extend(buckets[r])

            return ParseResult(tokens=ordered_tokens, source_lang="en", text=text, degraded=False, notes=notes)

        else:
            notes.append("spaCy missing; using heuristic fallback parser")
            words = text.split()
            tokens = []
            for i, w in enumerate(words):
                w_clean = re.sub(r'[^\w]', '', w).upper()
                if not w_clean or w_clean.lower() in ["a", "an", "the", "is", "am", "are"]:
                    continue
                role = "SUBJECT" if w_clean.lower() in ["i", "you", "he", "she", "we", "they"] else "OBJECT"
                tokens.append(GlossToken(
                    gloss=w_clean, role=role, display=w_clean,
                    surface=w, source_lang="en", index=i
                ))

            return ParseResult(tokens=tokens, source_lang="en", text=text, degraded=True, notes=notes)

    def _parse_hindi(self, text: str) -> ParseResult:
        words = text.split()
        expanded_words = []

        for w in words:
            w_clean = re.sub(r'[^\w]', '', w)
            if w_clean in self.hi_forms:
                expanded_words.extend(self.hi_forms[w_clean].split())
            else:
                expanded_words.append(w)

        tokens = []
        for i, w in enumerate(expanded_words):
            w_clean = re.sub(r'[^\w]', '', w)
            if not w_clean:
                continue

            # Check if mapped directly to an English Sign Gloss
            en_gloss = self.hi_to_en_map.get(w_clean, w_clean.upper())

            # Check concepts dictionary
            for concept_key, concept_val in self.concepts.items():
                if w_clean in concept_val.get("hi", []):
                    en_gloss = concept_key.upper()
                    break

            role = "OBJECT"
            if w_clean in ["मैं", "मुझे", "तुम", "वह", "हम"]:
                role = "SUBJECT"
            elif w_clean in ["कल", "आज", "अब"]:
                role = "TIME"
            elif w_clean in ["नहीं", "मत"]:
                role = "NEG"

            tokens.append(GlossToken(
                gloss=en_gloss,
                role=role,
                display=w_clean,
                surface=w,
                source_lang="hi",
                index=i
            ))

        return ParseResult(tokens=tokens, source_lang="hi", text=text, degraded=False)