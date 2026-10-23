"""Gráfico de barras v0.1.0 × v0.2.0 a partir de docs/medidas_v0.2.0.json (figura do CP4)."""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

PASTA = Path(__file__).parent
m = json.loads((PASTA.parent / "medidas_v0.2.0.json").read_text(encoding="utf-8"))
av, s = m["recuperacao"]["avaliacao"], m["sentimento"]
GRUPOS = [  # (rótulo, v0.1.0, v0.2.0, total)
    ("Recuperação: 1º resultado (30 perguntas reservadas)", av["tfidf"]["top1"], av["hibrida"]["top1"], 30),
    ("Recuperação: entre os 3 primeiros (30 perguntas)", av["tfidf"]["top3"], av["hibrida"]["top3"], 30),
    ("Recuperação: perguntas parafraseadas, 1º resultado", av["tfidf_parafrase"]["top1"], av["hibrida_parafrase"]["top1"], 15),
    ("Sentimento: amostra nova (40 frases)", s["v1_nova"]["acertos"], s["v2_nova"]["acertos"], 40),
    ("Sentimento: amostra do CP3 (20 frases)", s["v1_cp3"]["acertos"], s["v2_cp3"]["acertos"], 20),
]


def barra(valor, total, cor):
    pct = valor / total * 100
    return (f'<div class="trilho"><div class="barra" style="width:{pct:.1f}%;background:{cor}"></div>'
            f'<span class="v">{valor}/{total} ({pct:.0f}%)</span></div>')


linhas = "".join(f'<div class="grupo"><div class="rot">{r}</div>{barra(a, t, "#9aa5ad")}{barra(b, t, "#1f6f68")}</div>'
                 for r, a, b, t in GRUPOS)
HTML = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;font-family:Arial,sans-serif;background:#fff;color:#111}}
#alvo{{display:inline-block;padding:18px 24px;width:860px}}
.leg{{display:flex;gap:24px;margin-bottom:14px;font-size:15px}} .leg i{{display:inline-block;width:14px;height:14px;margin-right:6px;vertical-align:-2px}}
.grupo{{margin:12px 0}} .rot{{font-size:15px;font-weight:bold;margin-bottom:4px}}
.trilho{{position:relative;height:22px;width:680px;background:#f0f1f2;margin:3px 0;border-radius:3px}}
.barra{{height:100%;border-radius:3px}} .v{{position:absolute;left:692px;top:2px;font-size:14px;white-space:nowrap}}
</style></head><body><div id="alvo">
<div class="leg"><span><i style="background:#9aa5ad"></i>v0.1.0 (TF-IDF / sentimento v1)</span>
<span><i style="background:#1f6f68"></i>v0.2.0 (busca híbrida / sentimento v2)</span></div>{linhas}</div></body></html>"""

with sync_playwright() as p:
    nav = p.chromium.launch(); pg = nav.new_page(device_scale_factor=2)
    pg.set_content(HTML); pg.locator("#alvo").screenshot(path=PASTA / "fig_comparacao_releases.png")
    nav.close()
print("ok")
