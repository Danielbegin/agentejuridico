## 😁 Como usar
### Copie o Repositório
git clone https://github.com/Danielbegin/agentejuridico.git
cd agentejuridico

### Criei e ative um ambiente virtual
python -m venv .venv
* No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
* No Linux/macOS:
source .venv/bin/activate

### No Powershell ainda
pip install -r requirements.txt

### Garanta que seu app.py aponte para o caminho correto do Agente Jurídico
MODEL_PATH = "Bertimbau_Folder"

###Execute o conteiner
docker run -d -p 8080:8080 --name api-juridica agente-juridico

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
