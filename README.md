# Hashificador SHA-256 para Google Ads / Meta
Uma aplicação no Streamlit para normalização e hash de dados sensíveis como nome, telefone e e-mail, nos padrões exigidos pelas plataformas de anúncios Google Ads e Meta (Facebook Ads).

## Objetivo
Este projeto facilita o upload e tratamento de dados antes de enviá-los para campanhas de marketing, garantindo privacidade via hash SHA-256.

## Funcionalidades

- Upload de arquivos CSV contendo dados de contatos
- Detecção automática de colunas com nome, telefone e e-mail
- Normalização dos dados:
  - Nomes sem acentuação e em letras minúsculas
  - Telefones no formato internacional +55
  - E-mails minúsculos e sem espaços
- Aplicação de hash SHA-256 nos dados sensíveis
- Geração de arquivos formatados (sem hash) e hasheados (prontos para subir nas plataformas)
- Suporte a campanhas do **Google** e **Meta**

## Lógica do código

### Para campanhas Google:
- Divide nomes em `FIRST_NAME` e `LAST_NAME`
- Telefones são convertidos para o padrão `+55XXXXXXXXXXX`
- Cria dois arquivos para download:
  - `- formatado.csv`: dados limpos, sem hash
  - `- hashado.csv`: dados prontos para upload no Google Ads

### Para campanhas Meta:
- Permite selecionar entre telefone ou e-mail
- Extrai dados únicos e aplica o hash
- Cria arquivos formatado e hasheado semelhantes


