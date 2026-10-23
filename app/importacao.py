"""Importação de materiais didáticos a partir de arquivos (RF010 — release 0.2.0).

Aceita PDF, DOCX e TXT de até 5 MB. Extrai apenas o texto: imagens, tabelas complexas e
formatação ficam de fora e o professor revisa o texto antes de publicar.
"""
from __future__ import annotations

import io
import re

TAMANHO_MAXIMO = 5 * 1024 * 1024
EXTENSOES = (".pdf", ".docx", ".txt")


class ErroImportacao(ValueError):
    """Mensagem pronta para mostrar ao professor."""


def _limpar(texto: str) -> str:
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    texto = re.sub(r"-\n(?=[a-záéíóúâêôãõç])", "", texto)          # hifenização no fim da linha
    texto = re.sub(r"(?<![.!?:\n])\n(?!\n)", " ", texto)            # quebra de linha no meio da frase
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return "\n\n".join(p.strip() for p in texto.split("\n\n") if p.strip())


def _pdf(dados: bytes) -> str:
    from pypdf import PdfReader
    try:
        leitor = PdfReader(io.BytesIO(dados))
        if leitor.is_encrypted:
            raise ErroImportacao("O PDF está protegido por senha.")
        return "\n\n".join((p.extract_text() or "") for p in leitor.pages)
    except ErroImportacao:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ErroImportacao("Não foi possível ler este PDF.") from exc


def _docx(dados: bytes) -> str:
    from docx import Document
    try:
        doc = Document(io.BytesIO(dados))
    except Exception as exc:  # noqa: BLE001
        raise ErroImportacao("Não foi possível ler este arquivo do Word.") from exc
    return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _txt(dados: bytes) -> str:
    for cod in ("utf-8", "latin-1"):
        try:
            return dados.decode(cod)
        except UnicodeDecodeError:
            continue
    raise ErroImportacao("Não foi possível ler o arquivo de texto.")


def extrair_texto(nome_arquivo: str, dados: bytes) -> str:
    nome = (nome_arquivo or "").lower()
    if not nome.endswith(EXTENSOES):
        raise ErroImportacao("Formato não aceito. Envie PDF, DOCX ou TXT.")
    if len(dados) > TAMANHO_MAXIMO:
        raise ErroImportacao("O arquivo passa de 5 MB.")
    if nome.endswith(".pdf"):
        bruto = _pdf(dados)
    elif nome.endswith(".docx"):
        bruto = _docx(dados)
    else:
        bruto = _txt(dados)
    texto = _limpar(bruto)
    if len(texto.split()) < 20:
        raise ErroImportacao("Não encontrei texto suficiente no arquivo (pode ser um PDF de "
                             "imagem escaneada). Cole o texto manualmente.")
    return texto
