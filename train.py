import os
import torch
import numpy as np
import pandas as pd
import unicodedata
from torch import nn
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)

# --- 1. Funções de Normalização e Dataset ---
def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.lower().strip().replace(' ', '_')

class DatasetJuridico(Dataset):
    def __init__(self, textos, labels, tokenizer, max_len=128): # max_len reduzido para 128
        self.textos = textos
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.textos)

    def __getitem__(self, idx):
        texto = str(self.textos[idx])
        label = self.labels[idx]

        encoding = self.tokenizer(
            texto,
            truncation=True,
            padding='max_length',
            max_length=self.max_len,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'labels': torch.tensor(label, dtype=torch.long)
        }

# --- 2. Carregar e Preparar Dados ---
df = pd.read_csv("dataset_corrigido.csv", on_bad_lines='skip').dropna(subset=["ementa", "tipo_decisao"])

df["tipo_decisao_norm"] = df["tipo_decisao"].apply(normalizar_texto)

label2id = {"acordao": 0, "despacho": 1, "decisao_monocratica": 2}
id2label = {v: k for k, v in label2id.items()}

df["label"] = df["tipo_decisao_norm"].map(label2id)
df = df.dropna(subset=["label"])
df["label"] = df["label"].astype(int)

train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["ementa"].tolist(),
    df["label"].tolist(),
    test_size=0.2,
    random_state=42,
    stratify=df["label"]
)

# --- 3. Modelo e Tokenizer ---
model_name = "neuralmind/bert-base-portuguese-cased"  # BERTimbau base
tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3, use_safetensors=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# --- 4. Calcular Pesos das Classes (APÓS ter train_labels) ---
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_labels),
    y=train_labels
)
weights_tensor = torch.tensor(class_weights, dtype=torch.float).to(device)

# --- 5. Custom Trainer com Loss Ponderada ---
class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        
        loss_fct = nn.CrossEntropyLoss(weight=weights_tensor)
        loss = loss_fct(logits.view(-1, model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

# --- 6. Instanciar Datasets e Treinar ---
train_dataset = DatasetJuridico(train_texts, train_labels, tokenizer)
val_dataset = DatasetJuridico(val_texts, val_labels, tokenizer)

pasta_saida = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "bertimbau_triagem_juridica-20260916T183413Z-1-001",
    "bertimbau_triagem_juridica"
)

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_steps=50,
    learning_rate=2e-5,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    dataloader_num_workers=0, # Garante menor consumo de RAM
    fp16=True  # Ativa precisão mista na GTX 1650 (economiza metades da VRAM e dobra velocidade)
)

trainer = WeightedTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

print("Iniciando o retreinamento com perda ponderada...")
trainer.train()

# Salvar o novo modelo treinado
model.save_pretrained(pasta_saida)
tokenizer.save_pretrained(pasta_saida)
print(f"Modelo retreinado salvo com sucesso em: {pasta_saida}")