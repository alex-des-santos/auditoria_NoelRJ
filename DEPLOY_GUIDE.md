# 🚀 Guia de Deploy no Streamlit Cloud

Este guia passo a passo vai te ajudar a fazer o deploy da aplicação no Streamlit Cloud.

## ✅ Pré-requisitos

- [ ] Conta no GitHub
- [ ] Conta no Streamlit Cloud (pode fazer login com GitHub)
- [ ] Git instalado no seu computador

## 📝 Passo a Passo

### 1. Inicializar Repositório Git

Abra o terminal no diretório do projeto e execute:

```bash
cd "D:\Dev\PowerBi\CasosNoel"
git init
git branch -M main
```

### 2. Verificar Arquivos que Serão Commitados

**MUITO IMPORTANTE:** Verifique que o CSV com dados sensíveis NÃO será enviado ao GitHub:

```bash
git status
```

**✅ Você DEVE ver:**
```
Untracked files:
  .gitignore
  app.py
  context.md
  context_summary.md
  LICENSE
  README.md
  requirements.txt
  oscar_noel_audit/
  tests/
  ...
```

**❌ Você NÃO DEVE ver:**
```
Oscar Noel 2025 (respostas) - Respostas ao formulário 1.csv
Casos_Noel.pbix
```

Se o CSV aparecer na lista, PARE e verifique o `.gitignore`!

### 3. Fazer Commit dos Arquivos

```bash
git add .
git commit -m "Initial commit: Oscar Noel RJ 2025 Fraud Detection App"
```

### 4. Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. Preencha:
   - **Nome**: `oscar-noel-fraud-detection` (ou outro nome de sua preferência)
   - **Descrição**: `Streamlit app for detecting voting fraud using pattern analysis, anomaly detection, and temporal analysis`
   - **Público ou Privado**: Sua escolha (recomendo Público para portfolio)
   - **NÃO marque** "Add a README file"
   - **NÃO marque** "Add .gitignore"
   - **Escolha** "MIT License" (opcional, já temos um)
3. Clique em **"Create repository"**

### 5. Conectar ao Repositório Remoto

Substitua `SEU-USUARIO` pelo seu usuário do GitHub:

```bash
git remote add origin https://github.com/SEU-USUARIO/oscar-noel-fraud-detection.git
git push -u origin main
```

Se pedir autenticação:
- Username: seu usuário do GitHub
- Password: use um **Personal Access Token** (não a senha)
  - Gere em: https://github.com/settings/tokens
  - Scope necessário: `repo`

### 6. Deploy no Streamlit Cloud

#### 6.1 Acesse o Streamlit Cloud

1. Vá para: https://share.streamlit.io
2. Clique em **"Sign in"** e faça login com sua conta GitHub
3. Clique em **"New app"**

#### 6.2 Configure o Deploy

Preencha o formulário:

- **Repository**: `SEU-USUARIO/oscar-noel-fraud-detection`
- **Branch**: `main`
- **Main file path**: `app.py`
- **App URL** (opcional): escolha um nome único

Clique em **"Deploy!"**

#### 6.3 Aguarde o Build

- O Streamlit Cloud vai instalar as dependências do `requirements.txt`
- Tempo estimado: 2-5 minutos
- Você pode ver os logs em tempo real

#### 6.4 Teste o App

1. Quando o deploy terminar, você verá "Your app is live!"
2. Clique no link para abrir o app
3. **Importante**: Como o CSV não está no repositório, você verá um aviso
4. Use o botão "Faça upload do CSV de votação" na sidebar
5. Faça upload do arquivo CSV e teste o app

## 🎯 Após o Deploy

### Atualizar o README

Atualize o badge do Streamlit no README.md:

```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://SEU-APP.streamlit.app)
```

Substitua `SEU-APP` pela URL real do seu app.

### Adicionar ao Portfolio

Adicione o link do app no seu:
- LinkedIn (seção de Projetos)
- Portfólio pessoal
- README do GitHub (já está lá!)

## 🔄 Atualizações Futuras

Para atualizar o app após mudanças:

```bash
git add .
git commit -m "Descrição das mudanças"
git push
```

O Streamlit Cloud vai automaticamente redesenhar o app!

## ⚠️ Troubleshooting

### Erro: "Unable to deploy - not connected to GitHub"

**Solução**: Verifique que você fez o `git push` corretamente e que o repositório está público ou que o Streamlit tem acesso.

### Erro: "ModuleNotFoundError"

**Solução**: Verifique que todas as dependências estão no `requirements.txt`.

### App mostra aviso sobre CSV

**Solução**: Isso é esperado! Use o upload de arquivo na sidebar para carregar o CSV localmente.

### Erro: "File not found: context.md"

**Solução**: Verifique que os arquivos `context.md` e `context_summary.md` foram commitados.

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs no Streamlit Cloud
2. Teste localmente primeiro: `streamlit run app.py`
3. Consulte a documentação: https://docs.streamlit.io/deploy/streamlit-community-cloud

---

**Bom deploy! 🚀**
