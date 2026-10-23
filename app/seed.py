"""Popula o banco com dados FICTÍCIOS para demonstração e testes.

Uso:  python -m app.seed        (apaga e recria o banco local)
Senha de todos os usuários de demonstração: edumind123
"""
import random
from datetime import date, datetime, timedelta

from . import rag, seguranca
from .alertas import avaliar_checkin
from .db import Base, SessionLocal, engine
from .models import CheckIn, Estudante, Material, TrechoMaterial, Turma, Usuario
from .sentimento import analisar

SENHA = "edumind123"

MATERIAIS = [
    ("O ciclo da água", "Ciências", """A água do planeta está sempre em movimento. Esse movimento contínuo é chamado de ciclo da água, ou ciclo hidrológico. Ele acontece porque o Sol aquece a superfície da Terra e fornece a energia necessária para a água mudar de estado físico.

A primeira etapa é a evaporação. Quando o Sol aquece rios, lagos e oceanos, parte da água passa do estado líquido para o estado gasoso e sobe para a atmosfera na forma de vapor. As plantas também liberam vapor de água pelas folhas, em um processo chamado transpiração.

Na segunda etapa, chamada condensação, o vapor de água sobe, encontra camadas de ar mais frias e volta ao estado líquido em gotículas muito pequenas. Essas gotículas se juntam e formam as nuvens.

A terceira etapa é a precipitação. Quando as gotículas das nuvens ficam pesadas, elas caem na forma de chuva, neve ou granizo. A precipitação devolve a água para a superfície da Terra.

Por fim, ocorre a infiltração e o escoamento. Parte da água da chuva penetra no solo e abastece os lençóis freáticos, que são reservatórios de água subterrânea. Outra parte escorre pela superfície e volta para os rios e oceanos, onde o ciclo recomeça.

O ciclo da água é importante porque distribui a água doce pelo planeta, regula a temperatura e permite a existência de vida. Por isso, cuidar das nascentes, evitar o desmatamento e não poluir os rios são atitudes que ajudam a manter esse ciclo saudável."""),
    ("Frações no dia a dia", "Matemática", """Uma fração representa uma parte de um todo que foi dividido em partes iguais. Ela é escrita com dois números separados por um traço: o número de cima é o numerador e o número de baixo é o denominador.

O denominador indica em quantas partes iguais o inteiro foi dividido. O numerador indica quantas dessas partes estamos considerando. Por exemplo, se uma pizza foi cortada em oito pedaços iguais e você comeu três, você comeu três oitavos da pizza.

Frações equivalentes são frações diferentes que representam a mesma quantidade. Um meio e dois quartos são equivalentes, porque metade de uma barra de chocolate é a mesma quantidade que dois de seus quatro pedaços. Para encontrar uma fração equivalente, multiplicamos ou dividimos o numerador e o denominador pelo mesmo número.

Para somar frações com o mesmo denominador, somamos apenas os numeradores e mantemos o denominador. Assim, um quinto mais dois quintos é igual a três quintos. Quando os denominadores são diferentes, primeiro transformamos as frações em frações equivalentes com o mesmo denominador."""),
]

ESTUDANTES = [  # nome fictício, perfil sensorial, padrão de humor (últimos dias)
    ("Ana Beatriz Souza", "TDAH", [4, 4, 5, 3, 4, 4, 5]),
    ("Bruno Henrique Lima", "TEA", [3, 4, 3, 3, 4, 3, 4]),
    ("Carla Mendes", "DISLEXIA", [4, 3, 2, 2, 1, 2, 2]),
    ("Davi Oliveira", "PADRAO", [5, 4, 4, 5, 4, 5, 4]),
    ("Eduarda Costa", "TDAH", [3, 3, 4, 2, 3, 4, 3]),
    ("Felipe Andrade", "TEA", [4, 4, 3, 4, 2, None, 1]),
    ("Gabriela Ramos", "PADRAO", [5, 5, 4, 4, 5, 4, None]),
    ("Heitor Martins", "DISLEXIA", [3, 4, 4, 3, 4, 4, 3]),
]

COMENTARIOS = {
    1: ["hoje foi muito difícil, me senti sozinho no recreio", "não aguento mais as provas, estou muito cansado"],
    2: ["estou cansada e um pouco triste", "brigaram comigo no ônibus", "fiquei confuso na aula de matemática"],
    3: ["normal", "", "dormi pouco"],
    4: ["foi legal, aprendi coisas novas", "gostei da aula de ciências", ""],
    5: ["muito feliz hoje!", "joguei bola com meus amigos", "consegui terminar a atividade sozinho"],
}


def popular():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    random.seed(42)
    db = SessionLocal()
    h = seguranca.gerar_hash_senha(SENHA)

    gestor = Usuario(nome="Marina Gestora", email="gestora@escola.demo", senha_hash=h, perfil="gestor")
    prof = Usuario(nome="Paulo Professor", email="professor@escola.demo", senha_hash=h, perfil="professor")
    db.add_all([gestor, prof]); db.flush()
    turma = Turma(nome="5º ano A", ano_letivo=2026, escola="Escola Municipal Demonstração", professor_id=prof.id)
    db.add(turma); db.flush()

    hoje = date.today()
    for i, (nome, perfil, humores) in enumerate(ESTUDANTES):
        email = f"{nome.split()[0].lower()}@escola.demo"
        u = Usuario(nome=nome, email=email, senha_hash=h, perfil="aluno")
        db.add(u); db.flush()
        est = Estudante(usuario_id=u.id, turma_id=turma.id, perfil_sensorial=perfil,
                        consentimento_responsavel=True, data_consentimento=hoje - timedelta(days=30))
        db.add(est); db.flush()
        dias = len(humores)
        for d, humor in enumerate(humores):
            if humor is None:
                continue
            dia = hoje - timedelta(days=dias - d)  # termina ontem; "hoje" fica livre p/ demonstração
            texto = random.choice(COMENTARIOS[humor])
            r = analisar(humor, texto)
            ck = CheckIn(estudante_id=est.id, data=dia, humor=humor,
                         comentario_cifrado=seguranca.cifrar(texto), sentimento_score=r.score,
                         sentimento_rotulo=r.rotulo, sinal_risco=r.sinal_risco)
            db.add(ck); db.commit()
            for a in avaliar_checkin(db, est, ck):
                a.criado_em = datetime.combine(dia, datetime.min.time()).replace(hour=8, minute=10 + i)
            db.commit()

    for titulo, disc, texto in MATERIAIS:
        m = Material(titulo=titulo, disciplina=disc, turma_id=turma.id, professor_id=prof.id,
                     texto_original=texto)
        db.add(m); db.flush()
        for j, t in enumerate(rag.dividir_em_trechos(texto)):
            db.add(TrechoMaterial(material_id=m.id, ordem=j, texto=t))
    db.commit()
    rag.reconstruir_indice(db)
    db.close()
    print("Banco de demonstração criado. Usuários (senha: edumind123):")
    print("  professor@escola.demo · gestora@escola.demo · ana@escola.demo (aluna TDAH) · bruno@escola.demo (aluno TEA) · carla@escola.demo (aluna dislexia)")


if __name__ == "__main__":
    popular()
