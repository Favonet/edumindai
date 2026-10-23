"""Política de retenção (LGPD art. 15/16): apaga check-ins e alertas resolvidos antigos.

Uso (agendar 1x por mês, ex. cron):  python -m app.retencao
Regra: mantém dados do ano letivo corrente e do anterior; o resto é excluído.
"""
from datetime import date

from sqlalchemy import delete

from .db import SessionLocal
from .models import Alerta, CheckIn


def aplicar_retencao(hoje: date | None = None) -> tuple[int, int]:
    hoje = hoje or date.today()
    corte = date(hoje.year - 1, 1, 1)
    with SessionLocal() as db:
        alertas = db.execute(delete(Alerta).where(Alerta.status == "resolvido",
                                                  Alerta.criado_em < corte)).rowcount
        ids_presos = {a for (a,) in db.query(Alerta.checkin_id).filter(Alerta.checkin_id.isnot(None))}
        q = delete(CheckIn).where(CheckIn.data < corte)
        if ids_presos:
            q = q.where(CheckIn.id.notin_(ids_presos))
        checkins = db.execute(q).rowcount
        db.commit()
    return checkins, alertas


if __name__ == "__main__":
    c, a = aplicar_retencao()
    print(f"Retenção aplicada: {c} check-ins e {a} alertas resolvidos removidos.")
