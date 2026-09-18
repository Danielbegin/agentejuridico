import pandas as pd
from datasets import load_dataset

print("Baixando amostra do dataset em modo streaming...")

# Usamos streaming=True para não salvar pastas profundas no cache do Windows
dataset = load_dataset("andrebadini/repojus", streaming=True)

# Coletamos apenas os primeiros 500 registros para o teste de validação
amostra = []
for i, item in enumerate(dataset["train"]):
    amostra.append(item)
    if i >= 499:  # Limite de 500 itens
        break

# Converte para DataFrame e salva no CSV
df = pd.DataFrame(amostra)
print("Colunas encontradas:", df.columns)

df.to_csv("dataset.csv", index=False)
print("Arquivo dataset.csv criado com sucesso via streaming!")