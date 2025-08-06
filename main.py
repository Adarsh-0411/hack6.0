from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from document_processor import FileProcessor
from vector_store import DocumentVectorizer
from llm_processor import LanguageModelHandler

app = FastAPI(title="HackRx Query Engine")

class RequestPayload(BaseModel):
    documents: str
    questions: list[str]

class ResponsePayload(BaseModel):
    answers: list[str]

processor = FileProcessor()
vectorizer = DocumentVectorizer()
llm = LanguageModelHandler()

@app.post("/hackrx/run", response_model=ResponsePayload)
async def handle_request(payload: RequestPayload):
    try:
        chunks = processor.load_and_process(payload.documents)
        vectorizer.index_chunks(chunks)

        responses = []
        for question in payload.questions:
            top_contexts = vectorizer.find_similar(question)
            answer, _ = llm.answer_question(question, top_contexts)
            responses.append(answer)

        return ResponsePayload(answers=responses)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
