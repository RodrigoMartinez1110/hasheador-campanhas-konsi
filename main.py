import streamlit as st
import pandas as pd
import hashlib
import unidecode
from io import StringIO
import os

st.set_page_config(page_title="Hashificador para Google Ads / Meta", layout="centered")
st.title("Hashificador SHA-256 para Campanhas")
st.write("Faça upload de um arquivo CSV com colunas contendo nomes, telefones ou e-mails para gerar os dados hasheados.")

st.markdown("""
    ### Requisitos do arquivo:
    O arquivo **deve conter pelo menos**:
    - Uma coluna com a palavra **"nome"** no cabeçalho (ex: `Nome`, `nome_cliente`, etc)
    - Uma coluna com a palavra **"fone"** ou **"phone"** no cabeçalho (ex: `FONE1`, `telefone`, `phone1`, etc)
    - Uma coluna com a palavra **"mail"** no cabeçalho (ex: `email`, `EMAIL1`, etc)
""")

st.write("---")

# Funções para normalizar os dados nos padrões META ou GOOGLE
def normalizar_email(email):
    if pd.isna(email):
        return None
    return str(email).strip().lower() # Tirar espaçoes e colocar em minusculo

def normalizar_telefone(telefone):
    if pd.isna(telefone):
        return None
    telefone = ''.join(filter(str.isdigit, str(telefone))) # Serve para revmover caracteres que não são digitos e ficar num padrão (11999992222)
    if not telefone:
        return None
    if telefone.startswith('0'):
        telefone = telefone[1:]  # Caso o telefone esteja iniciando com 0, irá tirar
    if len(telefone) < 11:
        return None
    if not telefone.startswith('55'):
        telefone = '55' + telefone # Adiciona o 55 no inicio
    return '+' + telefone

def normalizar_nome(nome):
    if pd.isna(nome):
        return None, None
    nome = unidecode.unidecode(str(nome)).lower().strip() # Retira espaços desnecessários e coloca em minusculo
    partes = nome.split() # Divide o nome da pessoa e coloca numa lista
    if not partes:
        return None, None
    first_name = partes[0]  # Pega apenas o primeiro nome da pessoa
    last_name = ' '.join(partes[1:]) if len(partes) > 1 else '' # Pega apenas o ultimo nome da pessoa
    return first_name, last_name

def aplicar_hash(valor):
    if not valor:
        return None
    return hashlib.sha256(valor.encode('utf-8')).hexdigest() # Aplica o hash256 nos dados

# Seletor de tipo de campanha
tipo_campanha = st.sidebar.selectbox("Selecione o tipo de campanha", ["Google", "Meta"])

# Upload do CSV
uploaded_file = st.sidebar.file_uploader("📁 Arraste seu arquivo CSV aqui", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=';')
        nome_arquivo_original = os.path.splitext(uploaded_file.name)[0]
        nome_csv_hashado = f"{nome_arquivo_original} - hashado.csv"
        nome_csv_formatado = f"{nome_arquivo_original} - formatado.csv"

        if tipo_campanha == "Google":
            df_formatado = pd.DataFrame()
            df_hashed = pd.DataFrame()

            for col in df.columns:
                col_lower = col.lower()
                if 'nome' in col_lower:
                    first_name_col = f"{col}_FIRST_NAME"
                    last_name_col = f"{col}_LAST_NAME"
                    df[[first_name_col, last_name_col]] = df[col].apply(lambda x: pd.Series(normalizar_nome(x)))
                    df_formatado[first_name_col] = df[first_name_col]
                    df_formatado[last_name_col] = df[last_name_col]
                    df_hashed[first_name_col + '_HASHED'] = df[first_name_col].apply(aplicar_hash)
                    df_hashed[last_name_col + '_HASHED'] = df[last_name_col].apply(aplicar_hash)

                elif 'fone' in col_lower or 'phone' in col_lower:
                    novo_col = f"{col}_FORMATADO"
                    df[novo_col] = df[col].apply(normalizar_telefone)
                    df_formatado[novo_col] = df[novo_col]
                    df_hashed[novo_col + '_HASHED'] = df[novo_col].apply(aplicar_hash)

                elif 'mail' in col_lower:
                    novo_col = f"{col}_FORMATADO"
                    df[novo_col] = df[col].apply(normalizar_email)
                    df_formatado[novo_col] = df[novo_col]
                    df_hashed[novo_col + '_HASHED'] = df[novo_col].apply(aplicar_hash)

            # Remove linhas sem dados úteis
            tem_dados_formatados = df_formatado.notna().any(axis=1)
            df_formatado = df_formatado[tem_dados_formatados]
            df_hashed = df_hashed.loc[df_formatado.index]

            if df_hashed.empty:
                st.sidebar.warning("Nenhuma coluna com nome, telefone ou e-mail válida foi encontrada.")
            else:
                st.sidebar.success("Dados processados com sucesso!")
                st.subheader("Preview dos dados hasheados:")
                st.dataframe(df_hashed.head(10))

                st.download_button(
                    label="Baixar CSV Hasheado",
                    data=df_hashed.to_csv(index=False),
                    file_name=nome_csv_hashado,
                    mime="text/csv"
                )

                st.download_button(
                    label="Baixar CSV Formatado (sem hash)",
                    data=df_formatado.to_csv(index=False),
                    file_name=nome_csv_formatado,
                    mime="text/csv"
                )

        elif tipo_campanha == "Meta":
            tipo_dado_meta = st.sidebar.radio("Qual dado deseja hashear?", ["Telefone", "Email"])
            dados_formatados = []

            for col in df.columns:
                col_lower = col.lower()

                if tipo_dado_meta == "Telefone" and ('fone' in col_lower or 'phone' in col_lower):
                    dados_formatados += df[col].apply(normalizar_telefone).dropna().tolist()

                elif tipo_dado_meta == "Email" and 'mail' in col_lower:
                    dados_formatados += df[col].apply(normalizar_email).dropna().tolist()

            if not dados_formatados:
                st.sidebar.warning("Não foi encontrado nenhum dado válido para hash.")
            else:
                dados_unicos = list(set(dados_formatados))
                dados_hashed = [aplicar_hash(d) for d in dados_unicos]

                df_formatado_meta = pd.DataFrame({
                    f"{tipo_dado_meta.upper()}_FORMATADO": dados_unicos
                })

                df_hashed_meta = pd.DataFrame({
                    f"{tipo_dado_meta.upper()}_HASHED": dados_hashed
                })

                st.sidebar.success("Dados processados com sucesso!")

                st.subheader("Preview dos dados hasheados:")
                st.dataframe(df_hashed_meta.head(10))

                st.download_button(
                    label="📥 Baixar CSV Hasheado",
                    data=df_hashed_meta.to_csv(index=False),
                    file_name=nome_csv_hashado,
                    mime="text/csv"
                )

                st.download_button(
                    label="📥 Baixar CSV Formatado (sem hash)",
                    data=df_formatado_meta.to_csv(index=False),
                    file_name=nome_csv_formatado,
                    mime="text/csv"
                )

    except Exception as e:
        st.sidebar.error(f"Erro ao processar o arquivo: {e}")
