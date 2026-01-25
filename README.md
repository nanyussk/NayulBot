<h1 align="center">✨ NayulBot ✨</h1>

<p align="center">
  <a href="https://github.com/nanyuss/NayulBot">
    <img src="https://img.shields.io/github/languages/top/nanyuss/NayulBot" alt="Top Language" />
  </a>
  <a href="https://github.com/nanyuss/NayulBot/commits/main">
    <img src="https://img.shields.io/github/last-commit/nanyuss/NayulBot" alt="Last Commit" />
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/github/license/nanyuss/NayulBot" alt="License" />
  </a>
</p>

---

## 📌 Visao Geral

**Nayul** e um bot para Discord com comandos de economia, utilidades e automacoes, construido em Python com **discord.py**.

> ⚠️ O desenvolvimento esta pausado temporariamente, mas o projeto permanece aberto para colaboracoes.

## ✨ Destaques

- Cogs organizados por dominio
- Integracoes externas via wrappers
- Camada de dados dedicada
- Estrutura modular para evolucao

## ✅ Requisitos

- Python 3.11+
- Git

---

## 🚀 Inicio Rapido

1. **Clone o repositorio:**
   ```bash
   git clone https://github.com/nanyuss/NayulBot.git
   cd NayulBot
   ```
2. **Configure o ambiente:**
   - Renomeie `example.env` para `.env`
   - Preencha as variaveis obrigatorias
3. **Escolha um metodo e siga o tutorial:**

<details>
  <summary><strong>Usando uv (recomendado)</strong></summary>

1. **Crie o ambiente virtual:**
   ```bash
   uv venv .venv
   ```
2. **Ative o ambiente:**
   ```bash
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   ```
3. **Sincronize as dependencias:**
   ```bash
   uv sync
   ```
   > O `uv sync` usa as dependencias do `pyproject.toml`/`uv.lock`.
4. **Execute o bot:**
   ```bash
   uv run python main.py
   ```
</details>

<details>
  <summary><strong>Usando Python/pip</strong></summary>

1. **Crie e ative o ambiente virtual (opcional, mas recomendado):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   ```
2. **Instale as dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
   > Este metodo usa o `requirements.txt` diretamente.
3. **Execute o bot:**
   ```bash
   python main.py
   ```
</details>

---

## 🔐 Variaveis de Ambiente

Configure no arquivo `.env`:

- `TOKEN`: token do bot no Discord
- `OWNER_IDS`: IDs dos proprietarios separados por virgula
- `MONGO`: string de conexao do MongoDB
- `FILES_API`: URL base da API de arquivos
- `PREFIX` (opcional): prefixo de comandos, padrao `,,`

---

## 🗂 Estrutura do Projeto

- `main.py`: ponto de entrada
- `src/cogs`: comandos e eventos
- `src/core`: nucleo do bot (setup, help, manager de cogs)
- `src/database`: modelos e cliente do banco
- `src/features`: fluxos e UIs internas (ex.: embeds, jogos)
- `src/utils`: helpers e utilitarios
- `src/wrappers`: integracoes externas

---

## 🧪 Testes

```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```

---

## 🤝 Contribuicao

Contribuicoes sao bem-vindas. Sugestoes:

- Corrigir bugs
- Criar novos comandos e cogs
- Melhorar a documentacao
- Otimizar o codigo

---

## 🔗 Links Uteis

- [discord.py (Documentacao)](https://discordpy.readthedocs.io/en/stable/)
- [Python 3.11 (Documentacao)](https://docs.python.org/3.11/)
- [Discord Developer Portal](https://discord.com/developers/)
