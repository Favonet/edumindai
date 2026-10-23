"""Regras de geração de alertas preditivos para o professor (RF004)."""
from datetime import date, timedelta

from sqlalchemy import select

from .models import Alerta, CheckIn, Estudante

DIAS_JANELA = 7
SEQUENCIA_NEGATIVA = 3
MEDIA_LIMITE = -0.3


def _alerta_aberto(db, estudante_id: int, tipo: str) -> bool:
    return db.scalar(select(Alerta.id).where(
        Alerta.estudante_id == estudante_id, Alerta.tipo == tipo,
        Alerta.status != "resolvido")) is not None


def avaliar_checkin(db, estudante: Estudante, checkin: CheckIn) -> list[Alerta]:
    """Avalia o check-in recém-registrado e cria os alertas cabíveis (sem duplicar)."""
    novos: list[Alerta] = []

    if checkin.sinal_risco:
        novos.append(Alerta(estudante_id=estudante.id, checkin_id=checkin.id,
                            tipo="risco_imediato", nivel="alto",
                            motivo="Comentário do check-in contém expressão de possível risco. "
                                   "Acionar o protocolo de acolhimento da escola."))

    recentes = db.scalars(select(CheckIn).where(
        CheckIn.estudante_id == estudante.id,
        CheckIn.data >= date.today() - timedelta(days=DIAS_JANELA))
        .order_by(CheckIn.data.desc())).all()

    ultimos = recentes[:SEQUENCIA_NEGATIVA]
    if (len(ultimos) == SEQUENCIA_NEGATIVA
            and all(c.sentimento_rotulo == "negativo" for c in ultimos)
            and not _alerta_aberto(db, estudante.id, "tendencia_negativa")):
        novos.append(Alerta(estudante_id=estudante.id, checkin_id=checkin.id,
                            tipo="tendencia_negativa", nivel="atencao",
                            motivo=f"{SEQUENCIA_NEGATIVA} check-ins negativos consecutivos."))
    elif (len(recentes) >= 4
          and sum(c.sentimento_score for c in recentes) / len(recentes) <= MEDIA_LIMITE
          and not _alerta_aberto(db, estudante.id, "tendencia_negativa")):
        media = sum(c.sentimento_score for c in recentes) / len(recentes)
        novos.append(Alerta(estudante_id=estudante.id, checkin_id=checkin.id,
                            tipo="tendencia_negativa", nivel="atencao",
                            motivo=f"Média emocional dos últimos {DIAS_JANELA} dias abaixo do "
                                   f"esperado ({media:+.2f})."))

    for a in novos:
        db.add(a)
    db.commit()
    return novos
