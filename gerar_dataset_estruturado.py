import pandas as pd
import re
import unicodedata

def normalizar(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.lower()

# 1. Ler o arquivo bruto original (dataset.csv)
with open("dataset.csv", "r", encoding="utf-8", errors="ignore") as f:
    linhas = f.readlines()

dados = []

for linha in linhas:
    linha_limpa = linha.strip()
    if not linha_limpa or len(linha_limpa) < 30:
        continue
    
    linha_norm = normalizar(linha_limpa)
    
    # Classificação por hierarquia de relevância do termo no texto
    # Prioriza marcas explícitas de Despacho e Decisão Monocrática
    if "despacho decisorio" in linha_norm or "despacho" in linha_norm:
        label = "despacho"
    elif "decisao monocratica" in linha_norm or "monocratica" in linha_norm:
        label = "decisao_monocratica"
    elif "acordao" in linha_norm or "recurso voluntario" in linha_norm:
        label = "acordao"
    else:
        continue

    # Remove qualquer rótulo antigo que possa ter ficado no final da linha
    texto_final = re.sub(r', *(acordao|despacho|decisao_monocratica)$', '', linha_limpa, flags=re.IGNORECASE)
    
    dados.append({
        "ementa": texto_final,
        "tipo_decisao": label
    })

# 2. Criar e exportar DataFrame limpo
df_novo = pd.DataFrame(dados)

# Salvar garantindo que aspas e vírgulas das ementas não quebrem a estrutura do CSV
df_novo.to_csv("dataset_corrigido.csv", index=False, encoding="utf-8")

print("--- Distribuição Real das Classes ---")
print(df_novo["tipo_decisao"].value_counts())
print(f"\nDataset reconstruído com sucesso em 'dataset_corrigido.csv' ({len(df_novo)} registros).")