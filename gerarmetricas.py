import os
import torch
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

# 1. Carregar dataset
df = pd.read_csv("dataset_corrigido.csv", on_bad_lines='skip').dropna(subset=["ementa", "tipo_decisao"])

label2id = {"acordao": 0, "despacho": 1, "decisao_monocratica": 2}
id2label = {v: k for k, v in label2id.items()}

df["label"] = df["tipo_decisao"].map(label2id)
df = df.dropna(subset=["label"])
df["label"] = df["label"].astype(int)

# 2. Caminho do modelo treinado
pasta_saida = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "bertimbau_triagem_juridica-20260916T183413Z-1-001",
    "bertimbau_triagem_juridica"
)

print(f"Carregando modelo treinado de: {pasta_saida}")
tokenizer = AutoTokenizer.from_pretrained(pasta_saida)
model = AutoModelForSequenceClassification.from_pretrained(pasta_saida)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# 3. Gerar predições diretamente em lote via PyTorch
textos = df["ementa"].tolist()
y_true = df["label"].tolist()
y_preds = []

batch_size = 32  # Aumentado para 32 para rodar quase 2x mais rápido

print("Gerando predições no conjunto de dados...")

with torch.no_grad():
    for i in tqdm(range(0, len(textos), batch_size), desc="Classificando"):
        batch_textos = textos[i:i + batch_size]
        inputs = tokenizer(
            batch_textos, 
            padding=True, 
            truncation=True, 
            max_length=512, 
            return_tensors="pt"
        ).to(device)
        
        outputs = model(**inputs)
        preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
        y_preds.extend(preds)


# 4. Calcular métricas e Relatório de Classificação
target_names = ["acordao", "despacho", "decisao_monocratica"]
classes_ids = [0, 1, 2]

print("\n--- Relatório de Classificação ---")
print(classification_report(
    y_true, 
    y_preds, 
    labels=classes_ids, 
    target_names=target_names, 
    zero_division=0
))

# 5. Gerar e salvar a Matriz de Confusão
cm = confusion_matrix(y_true, y_preds, labels=classes_ids)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
plt.xlabel('Predito')
plt.ylabel('Verdadeiro')
plt.title('Matriz de Confusão - Triagem Jurídica BERTimbau')

output_img = "matriz_confusao_ifrj.png"
plt.savefig(output_img)
print(f"Matriz de confusão salva com sucesso em: {output_img}")
plt.show()

output_img = "matriz_confusao_ifrj.png"
plt.savefig(output_img)
print(f"Matriz de confusão salva com sucesso em: {output_img}")
plt.show()