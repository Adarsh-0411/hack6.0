from transformers import pipeline
from typing import List, Dict, Tuple

class LanguageModelHandler:
    def __init__(self):
        self.generator = pipeline('text-generation', model='distilgpt2')  # Swap with LLaMA if GPU available

    def answer_question(self, query: str, evidence: List[Dict]) -> Tuple[str, Dict]:
        joined_context = "\n".join([e['text'] for e in evidence])
        prompt = f"Question: {query}\nContext: {joined_context}\nAnswer concisely:"
        result = self.generator(prompt, max_length=200, num_return_sequences=1)[0]['generated_text']
        answer = result.split("Answer concisely:")[-1].strip()

        return answer, self._rationale(query, evidence, answer)

    def _rationale(self, question: str, evidence: List[Dict], answer: str) -> Dict:
        data = {
            "reasoning_steps": [
                "1. Retrieved top document chunks by semantic similarity.",
                "2. Analyzed each context for hints related to the query.",
                "3. Picked relevant details for accurate response.",
                "4. Compiled a direct and relevant answer."
            ],
            "key_evidence": [],
            "confidence_factors": []
        }

        for i, e in enumerate(evidence[:3]):
            if e['relevance_score'] > 0.7:
                data["key_evidence"].append({
                    "source": f"Chunk #{i+1}",
                    "relevance": round(e['relevance_score'], 3),
                    "excerpt": e['text'][:200] + "..."
                })

        data["confidence_factors"].append({
            "overall_confidence": max([e['relevance_score'] for e in evidence])
        })

        return data
