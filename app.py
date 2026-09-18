from fastapi import FastAPI
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ESTA LINHA É OBRIGATÓRIA:
app = FastAPI(title="API Triagem Jurídica IFRJ")

# Ajuste o caminho de acordo com a sua pasta do modelo retreinado
MODEL_PATH = "./bertimbau_triagem_juridica-20260916T183413Z-1-001/bertimbau_triagem_juridica"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

MAPPING = {0: "acordao", 1: "despacho", 2: "decisao_monocratica"}

class Peticao(BaseModel):
    texto: str

@app.post("/predict")
def predict(data: Peticao):
    inputs = tokenizer(data.texto, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        pred_class = torch.argmax(probs, dim=-1).item()
        
    return {
        "classe": MAPPING[pred_class],
        "confianca": round(probs[0][pred_class].item(), 4)
    }