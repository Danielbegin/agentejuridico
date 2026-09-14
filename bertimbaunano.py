import os
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from google import genai

# Inicialização da aplicação FastAPI
app = FastAPI(
    title="API Jurídica - Triagem e Agente de Minutas",
    description="Sistema assistivo human-in-the-loop para triagem e análise de prazos."
)

# Configuração de CORS para permitir requisições do Frontend (Vercel/HTML)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do dispositivo (CPU para hospedagens gratuitas)
device = torch.device("cpu")

# --- MÓDULO 1: Carregamento do BERTimbau ---
# Se o seu modelo treinado estiver no Hugging Face Hub, altere o nome do repositório aqui
MODEL_NAME = "Danilelisv1/bertimbau_triagem_juridica"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).to(device)
    print("✅ Modelo BERTimbau e Tokenizer carregados com sucesso.")
except Exception as e:
    print(f"⚠️ Erro ao carregar o modelo local/remoto: {e}")

# --- MÓDULO 2: Configuração do Cliente Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Esquema de validação dos dados de entrada
class AnaliseRequest(BaseModel):
    texto: str

@app.get("/")
def status():
    """Rota de verificação de saúde da API."""
    return {
        "status": "online",
        "modelo_triagem": MODEL_NAME,
        "gemini_ativo": client is not None
    }

@app.post("/api/analisar")
async def analisar_peca(payload: AnaliseRequest):
    """
    Rota principal do pipeline:
    1. Realiza triagem determinística via BERTimbau.
    2. Gera rascunho de minuta e fundamentação via Gemini.
    """
    texto = payload.texto.strip()
    if not texto:
        raise HTTPException(status_code=400, detail="O texto da peça não pode ser vazio.")

    # 1. Triagem via BERTimbau
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, max_length=512, padding=True).to(device)
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

    classe_predita = torch.argmax(probs, dim=1).item()
    confianca = probs[0][classe_predita].item()

    # 2. Análise e Minuta via Gemini
    parecer_agente = "Chave da API Gemini não encontrada no ambiente de execução."
    if client:
        try:
            prompt = (
                f"Você é um assistente jurídico especializado no Código de Processo Civil (CPC).\n"
                f"Analise a seguinte peça processual, verifique tempestividade e sugira uma minuta de rascunho:\n\n"
                f"{texto}"
            )
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )
            parecer_agente = response.text
        except Exception as err:
            parecer_agente = f"Erro na chamada do modelo generativo: {str(err)}"

    # 3. Retorno Estruturado para a Interface (XAI & Resultados)
    return {
        "triagem": {
            "classe_predita": classe_predita,
            "confianca": f"{confianca:.2%}",
            "confianca_valor": confianca
        },
        "parecer_agente": parecer_agente,
        "averbacao_cnj": "Minuta elaborada com auxílio de Inteligência Artificial. Sujeita à revisão humana (Resolução CNJ nº 332/2020)."
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)