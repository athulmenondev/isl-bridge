import spacy

class ISLParser:
    def __init__(self):
        print("[NLP] Loading spaCy English Model...")
        self.nlp = spacy.load("en_core_web_sm")
        
        # Auxiliary words & articles to strip out for ISL syntax
        self.stop_words = {
            "a", "an", "the", "is", "am", "are", "was", "were", 
            "be", "been", "being", "do", "does", "did", "to"
        }

    def parse(self, text: str) -> list[str]:
        """
        Translates raw text to ISL Gloss Token Array:
        Input:  "The boy is eating a green apple"
        Output: ['BOY', 'GREEN', 'APPLE', 'EAT']
        """
        doc = self.nlp(text)
        
        subjects = []
        objects = []
        verbs = []
        others = []

        for token in doc:
            # 1. Skip stop-words and punctuation
            if token.lower_ in self.stop_words or token.is_punct:
                continue

            # 2. Extract Lemmatized Root word
            lemma_token = token.lemma_.upper()

            # 3. Classify based on Dependency Role
            if "subj" in token.dep_:
                subjects.append(lemma_token)
            elif "obj" in token.dep_:
                objects.append(lemma_token)
            elif token.pos_ in ["VERB", "AUX"]:
                verbs.append(lemma_token)
            elif token.pos_ in ["ADJ", "NOUN", "PROPN", "NUM"]:
                # Place adjectives and modifiers before objects
                objects.append(lemma_token)
            else:
                others.append(lemma_token)

        # 4. Construct ISL SOV Syntax (Subject + Object + Verb + Others)
        isl_gloss = subjects + objects + verbs + others

        # Fallback if dependency parsing misses structure
        if not isl_gloss:
            isl_gloss = [t.lemma_.upper() for t in doc if not t.is_punct and t.lower_ not in self.stop_words]

        return isl_gloss
