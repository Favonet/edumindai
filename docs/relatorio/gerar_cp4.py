"""Gera o CP4 (Relatório Final) da Extensão Universitária II a partir do modelo dos professores.

Mantém o cabeçalho do modelo (logo, curso, disciplina, professores, atividade) e insere o
conteúdo com a mesma formatação do CP3 (Times New Roman 10, espaçamento 1,5).
Uso: python docs/relatorio/gerar_cp4.py <modelo EX2_CheckPoint-4.docx> <saida.docx>
"""
import re
import struct
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parents[2]
DIAG = RAIZ / "docs" / "diagramas"
TELAS = RAIZ / "telas"
FONTE = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Times New Roman"/>'

corpo: list[str] = []
imagens: list[tuple[str, Path]] = []  # (rId, arquivo)
cont = {"fig": 0, "quadro": 0, "pic": 100}


def runs(texto: str, tam=20, italico=False, extra="") -> str:
    """Converte **negrito** em runs."""
    saida = []
    for i, parte in enumerate(re.split(r"\*\*", texto)):
        if not parte:
            continue
        b = "<w:b/>" if i % 2 else ""
        it = "<w:i/>" if italico else ""
        saida.append(f'<w:r><w:rPr>{FONTE}{b}{it}<w:sz w:val="{tam}"/>{extra}</w:rPr>'
                     f'<w:t xml:space="preserve">{escape(parte)}</w:t></w:r>')
    return "".join(saida)


def P(texto, recuo=True):
    ind = '<w:ind w:firstLine="709"/>' if recuo else ""
    corpo.append(f'<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="360" w:lineRule="auto"/>{ind}'
                 f'<w:jc w:val="both"/></w:pPr>{runs(texto)}</w:p>')


def B(texto):
    corpo.append('<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="360" w:lineRule="auto"/>'
                 '<w:ind w:left="709" w:hanging="283"/><w:jc w:val="both"/></w:pPr>'
                 + runs("• " + texto) + "</w:p>")


def H1(texto):
    corpo.append('<w:p><w:pPr><w:keepNext/><w:spacing w:before="240" w:after="80" w:line="360" '
                 f'w:lineRule="auto"/><w:jc w:val="left"/></w:pPr>{runs("**" + texto + "**")}</w:p>')


def H2(texto):
    corpo.append('<w:p><w:pPr><w:keepNext/><w:spacing w:before="160" w:after="40" w:line="360" '
                 f'w:lineRule="auto"/><w:jc w:val="left"/></w:pPr>{runs("**" + texto + "**", italico=True)}</w:p>')


def VAZIO():
    corpo.append('<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:p>')


def _legenda(rotulo, texto, antes=True):
    esp = 'w:before="120" w:after="40"' if antes else 'w:before="0" w:after="160"'
    keep = "<w:keepNext/>" if antes else ""
    corpo.append(f'<w:p><w:pPr>{keep}<w:spacing {esp} w:line="240" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>'
                 f'{runs("**" + rotulo + ":** " + texto, tam=18)}</w:p>')


def Q(titulo, cabecalho, linhas, larguras):
    cont["quadro"] += 1
    _legenda(f"Quadro {cont['quadro']}", titulo)
    total = sum(larguras)
    bordas = "".join(f'<w:{b} w:val="single" w:sz="4" w:color="808080"/>'
                     for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
    xml = [f'<w:tbl><w:tblPr><w:tblW w:w="{total}" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>{bordas}'
           '</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>'
           + "".join(f'<w:gridCol w:w="{w}"/>' for w in larguras) + "</w:tblGrid>"]

    def celula(txt, w, cab):
        shd = '<w:shd w:val="clear" w:color="auto" w:fill="D9E8E6"/>' if cab else ""
        jc = "center" if cab else "left"
        paragrafos = "".join(
            f'<w:p><w:pPr><w:spacing w:line="240" w:lineRule="auto" w:before="20" w:after="20"/>'
            f'<w:jc w:val="{jc}"/></w:pPr>{runs(("**" + t + "**") if cab else t, tam=18)}</w:p>'
            for t in str(txt).split("\n"))
        return f'<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="{w}"/>{shd}</w:tcPr>{paragrafos}</w:tc>'

    xml.append('<w:tr><w:trPr><w:tblHeader/></w:trPr>' + "".join(celula(c, w, True) for c, w in zip(cabecalho, larguras)) + "</w:tr>")
    for ln in linhas:
        xml.append("<w:tr><w:trPr><w:cantSplit/></w:trPr>" + "".join(celula(c, w, False) for c, w in zip(ln, larguras)) + "</w:tr>")
    xml.append("</w:tbl>")
    corpo.append("".join(xml))
    corpo.append('<w:p><w:pPr><w:spacing w:before="0" w:after="80" w:line="240" w:lineRule="auto"/></w:pPr></w:p>')


def _tamanho_png(caminho: Path):
    with open(caminho, "rb") as f:
        f.read(16)
        return struct.unpack(">II", f.read(8))


def F(caminho: Path, legenda: str, largura_cm=15.0, altura_max_cm=14.0):
    cont["fig"] += 1
    cont["pic"] += 1
    rid = f"rIdCP4img{cont['fig']}"
    imagens.append((rid, caminho))
    w, h = _tamanho_png(caminho)
    cx = int(largura_cm * 360000)
    cy = int(cx * h / w)
    if cy > altura_max_cm * 360000:
        cy = int(altura_max_cm * 360000)
        cx = int(cy * w / h)
    nid = cont["pic"]
    corpo.append(
        '<w:p><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="0" w:line="240" w:lineRule="auto"/>'
        '<w:jc w:val="center"/></w:pPr><w:r><w:drawing><wp:inline '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{nid}" name="Figura {cont["fig"]}"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic>'
        f'<pic:nvPicPr><pic:cNvPr id="0" name="{caminho.name}"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"/></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')
    _legenda(f"Figura {cont['fig']}", legenda, antes=False)


def REF(texto):
    corpo.append('<w:p><w:pPr><w:spacing w:before="0" w:after="120" w:line="240" w:lineRule="auto"/>'
                 f'<w:jc w:val="left"/></w:pPr>{runs(texto)}</w:p>')


def DESTAQUE(texto):
    """Parágrafo com trecho a completar pelo estudante (marcado em amarelo)."""
    partes = texto.split("[[")
    xml = runs(partes[0])
    for p in partes[1:]:
        marcado, resto = p.split("]]")
        xml += runs(marcado, extra='<w:highlight w:val="yellow"/>') + runs(resto)
    corpo.append('<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="360" w:lineRule="auto"/>'
                 f'<w:jc w:val="both"/></w:pPr>{xml}</w:p>')


# ======================================================================= CONTEÚDO
from conteudo_cp4 import escrever  # noqa: E402

escrever(globals())


# ======================================================================= MONTAGEM
def montar(modelo: Path, saida: Path):
    zin = zipfile.ZipFile(modelo)
    doc = zin.read("word/document.xml").decode("utf-8")
    ini = doc.index("<w:body>") + len("<w:body>")
    corpo_modelo = doc[ini:doc.rindex("<w:sectPr")]
    sect = doc[doc.rindex("<w:sectPr"):doc.index("</w:body>")]
    # o logo do cabeçalho é uma imagem flutuante que vai até ~3,2 cm do topo, e a margem do modelo
    # é de 2 cm: o logo cobria o início de cada página (figuras cortadas). Margem superior de 3,7 cm.
    sect = re.sub(r'w:top="\d+"', 'w:top="2098"', sect)
    elementos = re.findall(r"<w:p[ >].*?</w:p>|<w:tbl>.*?</w:tbl>", corpo_modelo, re.S)
    texto = lambda e: "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", e))
    corte = next(i for i, e in enumerate(elementos) if texto(e).startswith("Nome do Estudante"))
    cabecalho = elementos[:corte + 1]
    nome = cabecalho[-1]
    # junta os runs do "Nome do Estudante:____" num só texto com o nome
    primeiro_rpr = re.search(r"<w:r>(<w:rPr>.*?</w:rPr>)", nome, re.S).group(1)
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", nome, re.S).group(0)
    cabecalho[-1] = (f"<w:p>{ppr}<w:r>{primeiro_rpr}<w:t xml:space=\"preserve\">Nome do Estudante: "
                     "Ricardo Augusto Ferreira Almeida</w:t></w:r></w:p>")
    novo = doc[:ini] + "".join(cabecalho) + "".join(corpo) + sect + "</w:body></w:document>"

    rels = zin.read("word/_rels/document.xml.rels").decode("utf-8")
    extra = "".join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                    f'relationships/image" Target="media/cp4_{i}_{arq.name}"/>'
                    for i, (rid, arq) in enumerate(imagens))
    rels = rels.replace("</Relationships>", extra + "</Relationships>")
    tipos = zin.read("[Content_Types].xml").decode("utf-8")
    # o modelo traz um GIF sem declaração de tipo; declara png e gif se faltarem
    for ext in ("png", "gif"):
        if f'Extension="{ext}"' not in tipos:
            tipos = tipos.replace("</Types>", f'<Default Extension="{ext}" ContentType="image/{ext}"/></Types>')

    with zipfile.ZipFile(saida, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "word/document.xml":
                zout.writestr(item, novo)
            elif item.filename == "word/_rels/document.xml.rels":
                zout.writestr(item, rels)
            elif item.filename == "[Content_Types].xml":
                zout.writestr(item, tipos)
            else:
                zout.writestr(item, zin.read(item.filename))
        for i, (_, arq) in enumerate(imagens):
            zout.write(arq, f"word/media/cp4_{i}_{arq.name}")
    print(f"{saida}: {cont['fig']} figuras, {cont['quadro']} quadros")


if __name__ == "__main__":
    montar(Path(sys.argv[1]), Path(sys.argv[2]))
