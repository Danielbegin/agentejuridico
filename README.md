# Agente Jurídico - Triagem Automática com BERTimbau

API para classificação de documentos jurídicos em três categorias (*acórdão*, *despacho* e *decisão monocrática*), desenvolvida como projeto de pesquisa no IFRJ.

## 🛠️ Como Executar Localmente
```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor da API
uvicorn app:app --reload --port 8080
Acessar documentação interativa: http://127.0.0.1:8080/docs

## 📜 Créditos e Modelos de Base

Este projeto utiliza o modelo pré-treinado em português brasileiro **BERTimbau**:

* **Modelo Base:** [neuralmind/bert-base-portuguese-cased](https://huggingface.co/neuralmind/bert-base-portuguese-cased)
* **Licença do Modelo Base:** [MIT License](https://github.com/neuralmind-ai/portuguese-bert/blob/master/LICENSE)
* **Referência de Citação:**
  > SOUZA, Fábio; NOGUEIRA, Rodrigo; LOTUFO, Roberto. **BERTimbau: Pretrained BERT Models for Brazilian Portuguese**. In: Symposium on Information and Human Language Technology (STIL), 2020.

## 🔗 Projetos Relacionados e Ecossistema

- **Coleta e Pipeline de Dados:** A estrutura de extração e raspagem de jurisprudência que alimenta a fase de ingestão do dataset é compatível e integrada conceitualmente com o projeto [JurisData](https://github.com/MayronDAV/JurisData).

## 📄 Licença do Repositório

Este repositório está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
