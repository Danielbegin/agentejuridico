# Agente Jurídico - Triagem Automática com BERTimbau

API para classificação de documentos jurídicos em três categorias (*acórdão*, *despacho* e *decisão monocrática*), desenvolvida como projeto de pesquisa no IFRJ.

## 🚀 Tecnologias
- **Modelo Base:** BERTimbau (`neuralmind/bert-base-portuguese-cased`)
- **API:** FastAPI + Uvicorn
- **Container:** Docker
- **Pipeline de Dados:** Compatível com dados estruturados via [JurisData](https://github.com/MayronDAV/JurisData) e extrações do DataJud.

## 🛠️ Como Executar Localmente
```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor da API
uvicorn app:app --reload --port 8080
Acessar documentação interativa: http://127.0.0.1:8080/docs
