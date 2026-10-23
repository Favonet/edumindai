"""Modelo de dados do EduMindAI (modelo físico, via SQLAlchemy)."""
from datetime import datetime, date

from sqlalchemy import (Boolean, Date, DateTime, Float, ForeignKey, Integer, LargeBinary,
                        String, Text, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

PERFIS_ACESSO = ("aluno", "professor", "gestor")
PERFIS_SENSORIAIS = ("TDAH", "TEA", "DISLEXIA", "PADRAO")


class Usuario(Base):
    __tablename__ = "usuario"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[str] = mapped_column(String(20))  # aluno | professor | gestor
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    pref_fonte_grande: Mapped[bool] = mapped_column(Boolean, default=False)
    pref_alto_contraste: Mapped[bool] = mapped_column(Boolean, default=False)
    pref_espacamento: Mapped[bool] = mapped_column(Boolean, default=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    estudante: Mapped["Estudante"] = relationship(back_populates="usuario", uselist=False,
                                                  foreign_keys="Estudante.usuario_id")


class Turma(Base):
    __tablename__ = "turma"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(60))
    ano_letivo: Mapped[int] = mapped_column(Integer)
    escola: Mapped[str] = mapped_column(String(120))
    professor_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))

    professor: Mapped[Usuario] = relationship()
    estudantes: Mapped[list["Estudante"]] = relationship(back_populates="turma")


class Estudante(Base):
    __tablename__ = "estudante"
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), unique=True)
    turma_id: Mapped[int] = mapped_column(ForeignKey("turma.id"))
    perfil_sensorial: Mapped[str] = mapped_column(String(20), default="PADRAO")
    consentimento_responsavel: Mapped[bool] = mapped_column(Boolean, default=False)
    data_consentimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    # v0.2.0: quem consentiu (nome do responsável) e quem registrou o termo no sistema
    nome_responsavel: Mapped[str | None] = mapped_column(String(120), nullable=True)
    consentimento_registrado_por: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id"), nullable=True)

    usuario: Mapped[Usuario] = relationship(back_populates="estudante",
                                            foreign_keys=[usuario_id])
    turma: Mapped[Turma] = relationship(back_populates="estudantes")
    checkins: Mapped[list["CheckIn"]] = relationship(back_populates="estudante",
                                                      order_by="CheckIn.data.desc()")


class CheckIn(Base):
    __tablename__ = "checkin"
    __table_args__ = (UniqueConstraint("estudante_id", "data", name="uq_checkin_dia"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    estudante_id: Mapped[int] = mapped_column(ForeignKey("estudante.id"), index=True)
    data: Mapped[date] = mapped_column(Date, default=date.today)
    humor: Mapped[int] = mapped_column(Integer)  # 1 (muito mal) a 5 (muito bem)
    comentario_cifrado: Mapped[str | None] = mapped_column(Text, nullable=True)
    sentimento_score: Mapped[float] = mapped_column(Float)
    sentimento_rotulo: Mapped[str] = mapped_column(String(10))  # positivo|neutro|negativo
    sinal_risco: Mapped[bool] = mapped_column(Boolean, default=False)

    estudante: Mapped[Estudante] = relationship(back_populates="checkins")


class Alerta(Base):
    __tablename__ = "alerta"
    id: Mapped[int] = mapped_column(primary_key=True)
    estudante_id: Mapped[int] = mapped_column(ForeignKey("estudante.id"), index=True)
    checkin_id: Mapped[int | None] = mapped_column(ForeignKey("checkin.id"), nullable=True)
    tipo: Mapped[str] = mapped_column(String(30))   # risco_imediato | tendencia_negativa
    nivel: Mapped[str] = mapped_column(String(10))  # alto | atencao
    motivo: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(12), default="aberto")  # aberto|em_acomp|resolvido
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    atualizado_por: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)

    estudante: Mapped[Estudante] = relationship()


class Material(Base):
    __tablename__ = "material"
    id: Mapped[int] = mapped_column(primary_key=True)
    turma_id: Mapped[int] = mapped_column(ForeignKey("turma.id"))
    professor_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    titulo: Mapped[str] = mapped_column(String(160))
    disciplina: Mapped[str] = mapped_column(String(60))
    texto_original: Mapped[str] = mapped_column(Text)
    # v0.2.0: origem do texto (digitado ou nome do arquivo importado: PDF, DOCX, TXT)
    origem: Mapped[str | None] = mapped_column(String(160), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    turma: Mapped[Turma] = relationship()
    trechos: Mapped[list["TrechoMaterial"]] = relationship(
        back_populates="material", cascade="all, delete-orphan", order_by="TrechoMaterial.ordem")


class TrechoMaterial(Base):
    """Fragmento (chunk) do material usado na recuperação semântica."""
    __tablename__ = "trecho_material"
    id: Mapped[int] = mapped_column(primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("material.id"), index=True)
    ordem: Mapped[int] = mapped_column(Integer)
    texto: Mapped[str] = mapped_column(Text)
    # v0.2.0: vetor do trecho (float32) gerado pelo modelo de embeddings e o nome do modelo,
    # para não recalcular a cada reinício e para refazer se o modelo mudar
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    embedding_modelo: Mapped[str | None] = mapped_column(String(120), nullable=True)

    material: Mapped[Material] = relationship(back_populates="trechos")


class Adaptacao(Base):
    """Cache das versões adaptadas de cada material por perfil sensorial."""
    __tablename__ = "adaptacao"
    __table_args__ = (UniqueConstraint("material_id", "perfil_sensorial", name="uq_adaptacao"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("material.id", ondelete="CASCADE"))
    perfil_sensorial: Mapped[str] = mapped_column(String(20))
    conteudo_html: Mapped[str] = mapped_column(Text)
    metodo: Mapped[str] = mapped_column(String(20))  # regras | llm
    gerado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class LogAcesso(Base):
    """Trilha de auditoria (LGPD art. 37): quem acessou dado pessoal sensível e quando."""
    __tablename__ = "log_acesso"
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    acao: Mapped[str] = mapped_column(String(60))
    recurso: Mapped[str] = mapped_column(String(120))
    data_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    usuario: Mapped[Usuario | None] = relationship()
