# Publicar o EduMindAI na internet (grátis, com o domínio da Cloudflare)

Guia para o Claude Code (ou para você) colocar o sistema no ar num endereço como
`https://edumind.favo.net.br`, para o professor acessar.

## Por que não dá para usar Workers/Pages, como na Galeria 3D

O EduMindAI é um servidor **Python** (FastAPI) com banco **SQLite** em arquivo, scikit-learn
e um modelo de IA (sentence-transformers / PyTorch, cerca de 470 MB). Os Workers da
Cloudflare não rodam esse tipo de aplicação, e o Pages só serve sites estáticos. Levar
o sistema para lá exigiria reescrevê-lo.

O caminho grátis que usa o seu domínio é o **Cloudflare Tunnel**. O sistema continua
rodando no seu PC e a Cloudflare cria um "túnel" seguro até ele. Não precisa abrir porta
no roteador e o HTTPS é automático.

**Limite:** o site só fica no ar enquanto o PC estiver ligado, com o sistema e o túnel
rodando. Para a apresentação e a correção do professor, isso basta. Se precisar de um
endereço sempre no ar, veja a Opção C no fim.

---

## Opção A – Link rápido em 2 minutos (sem domínio)

Serve para testar ou mandar um link na hora. Cada vez que rodar, o endereço muda.

```bat
winget install --id Cloudflare.cloudflared
cd C:\projetos\edumindai
iniciar.bat
```

Em **outra** janela do terminal:

```bat
cloudflared tunnel --url http://localhost:8000
```

O endereço `https://xxxx-xxxx.trycloudflare.com` aparece no terminal.

---

## Opção B – Endereço fixo no seu domínio (recomendado)

### Passo 1 – Instalar o cloudflared (uma vez só)

```bat
winget install --id Cloudflare.cloudflared
```

Feche e abra o terminal de novo e confira com `cloudflared --version`.

### Passo 2 – Autorizar o domínio (VOCÊ faz, no navegador)

```bat
cloudflared tunnel login
```

O navegador abre o painel da Cloudflare. Escolha o seu domínio e clique em **Authorize**.
Isso cria o arquivo `C:\Users\User\.cloudflared\cert.pem`.

> Claude Code: este passo exige login do usuário. Peça para ele fazer e só continue
> depois que `cert.pem` existir.

### Passo 3 – Criar o túnel e o endereço

Troque `SEU-DOMINIO.com.br` pelo seu domínio:

```bat
cloudflared tunnel create edumind
cloudflared tunnel route dns edumind edumind.favo.net.br
```

O primeiro comando mostra o **ID do túnel** e cria `C:\Users\User\.cloudflared\<ID>.json`.

### Passo 4 – Arquivo de configuração do túnel

Crie `C:\Users\User\.cloudflared\config.yml` com o conteúdo abaixo, trocando o `<ID>`:

```yaml
tunnel: edumind
credentials-file: C:\Users\User\.cloudflared\<ID>.json
ingress:
  - hostname: edumind.favo.net.br
    service: http://localhost:8000
  - service: http_status:404
```

### Passo 5 – Segurança antes de abrir para a internet

1. Gere um segredo de sessão:
   ```bat
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Crie o arquivo `C:\projetos\edumindai\publicar.bat`. Ele já está no `.gitignore`, porque
   guarda o segredo e não deve ir para o repositório.

   ```bat
   @echo off
   cd /d "%~dp0"
   call .venv\Scripts\activate.bat
   set EDUMIND_SEGREDO_SESSAO=COLE_O_SEGREDO_AQUI
   set EDUMIND_HTTPS=1
   start "EduMindAI" uvicorn app.main:app --host 127.0.0.1 --port 8000 --proxy-headers
   timeout /t 20 >nul
   cloudflared tunnel run edumind
   ```

   - `--host 127.0.0.1`: o sistema só aceita conexões do próprio PC; quem vem de fora
     passa pelo túnel.
   - `EDUMIND_HTTPS=1`: o cookie de login só trafega por HTTPS.
3. Os dados são **fictícios** (script de demonstração). Não cadastre dados reais de
   alunos no sistema publicado.
4. **Opcional:** para só os professores entrarem, use o **Cloudflare Access**, como na
   Galeria. Vá em Zero Trust → Access → Applications → Add → Self-hosted, informe o domínio
   `edumind.favo.net.br` e crie uma policy com os e-mails dos professores. Eles
   recebem um código por e-mail para entrar. É grátis até 50 usuários.

### Passo 6 – Colocar no ar

```bat
cd C:\projetos\edumindai
iniciar.bat
```

Rode o `iniciar.bat` só na primeira vez, para instalar tudo e criar o banco. Feche-o
depois que aparecer "Abra no navegador". Nas próximas vezes, rode apenas:

```bat
publicar.bat
```

Abra `https://edumind.favo.net.br`. Para testar, entre com `professor@escola.demo`
e a senha `edumind123`.

### Passo 7 – Conferir (Claude Code)

```bat
curl https://edumind.favo.net.br/saude
```

A resposta deve mostrar `"versao":"0.2.0"` e `"busca":"híbrida (embeddings + TF-IDF)"`.

### Passo 8 – Colocar o link no relatório (CP4)

Em `docs/relatorio/conteudo_cp4.py`, no Apêndice C ou no Anexo A, acrescente
"Versão de demonstração online: https://edumind.favo.net.br (usuários do Apêndice C)".
Depois gere o relatório de novo:

```bat
.venv\Scripts\python docs\relatorio\gerar_cp4.py docs\relatorio\modelo_EX2_CheckPoint-4.docx C:\Users\User\Downloads\CP4_EduMindAI_Extensao2.docx
```

---

## Opção C – Sempre no ar, sem depender do PC (Hugging Face Spaces, grátis)

Use esta opção se o professor for acessar em horários em que o seu PC está desligado.

- Crie uma conta em huggingface.co, depois um **Space** do tipo **Docker** (CPU básica é
  grátis: 2 vCPU e 16 GB de RAM).
- É preciso um `Dockerfile` (Python 3.12, `pip install -r requirements-ia.txt`,
  `python -m app.seed`, `uvicorn app.main:app --host 0.0.0.0 --port 7860`). O próprio
  Hugging Face monta a imagem, então não precisa ter Docker no PC.
- Configure `EDUMIND_SEGREDO_SESSAO` e `EDUMIND_HTTPS=1` em **Settings → Secrets**.
- O endereço fica `https://SEU-USUARIO-edumind.hf.space`. Na Cloudflare, dá para criar uma
  **Redirect Rule** de `edumind.favo.net.br` para esse endereço.
- Limites: o Space dorme depois de 48 h sem acesso e acorda no próximo acesso (cerca de
  1 minuto). O banco SQLite volta ao estado de demonstração a cada reinício.
