"""Gabarito de recuperação (RF002) — v0.2.0.

50 perguntas sobre os 5 materiais de demonstração, 10 por material. Cada item traz um
trecho de texto que precisa estar no 1º resultado. Metade das perguntas usa as palavras do
material (literal) e metade é parafraseada, como um estudante perguntaria (paráfrase).

As perguntas foram divididas antes de qualquer medição:
  CALIBRACAO (20) — usadas só para escolher o peso dos embeddings na busca híbrida;
  AVALIACAO  (30) — usadas só para medir o resultado, sem participar da escolha do peso.
"""

# (pergunta, trecho esperado no resultado, tipo, conjunto)
PERGUNTAS = [
    # O ciclo da água
    ("o que é condensação?", "chamada condensação", "literal", "cal"),
    ("o que acontece na evaporação", "primeira etapa é a evaporação", "literal", "cal"),
    ("o que é precipitação", "terceira etapa é a precipitação", "literal", "aval"),
    ("o que é lençol freático", "lençóis freáticos", "literal", "aval"),
    ("por que o ciclo da água é importante", "importante porque distribui", "literal", "aval"),
    ("por que chove?", "forma de chuva", "parafrase", "cal"),
    ("como as nuvens se formam?", "formam as nuvens", "parafrase", "cal"),
    ("de onde vem a energia que faz a água mudar de estado?", "Sol aquece a superfície", "parafrase", "aval"),
    ("as plantas soltam água no ar?", "transpiração", "parafrase", "aval"),
    ("o que podemos fazer para proteger os rios e a água?", "cuidar das nascentes", "parafrase", "aval"),
    # Frações no dia a dia
    ("o que é o denominador", "denominador indica", "literal", "cal"),
    ("o que é o numerador", "numerador indica quantas", "literal", "cal"),
    ("o que são frações equivalentes", "equivalentes são frações", "literal", "aval"),
    ("como somar frações com o mesmo denominador", "somamos apenas os numeradores", "literal", "aval"),
    ("o que é uma fração", "representa uma parte de um todo", "literal", "aval"),
    ("comi 3 pedaços de uma pizza cortada em 8, quanto eu comi?", "três oitavos", "parafrase", "cal"),
    ("metade é a mesma coisa que dois quartos?", "Um meio e dois quartos", "parafrase", "cal"),
    ("e se os números de baixo forem diferentes na hora de somar?", "denominadores são diferentes", "parafrase", "aval"),
    ("como achar outra fração que vale a mesma quantidade?", "multiplicamos ou dividimos", "parafrase", "aval"),
    ("qual número fica na parte de cima?", "número de cima é o numerador", "parafrase", "aval"),
    # O Sistema Solar
    ("quais são os planetas do sistema solar", "oito planetas", "literal", "cal"),
    ("qual é o maior planeta", "Júpiter é o maior", "literal", "cal"),
    ("qual planeta é conhecido pelos anéis", "Saturno é conhecido", "literal", "aval"),
    ("o que é o movimento de rotação", "movimento de rotação", "literal", "aval"),
    ("o que é o movimento de translação", "movimento de translação", "literal", "aval"),
    ("por que existe o dia e a noite?", "dia e à noite", "parafrase", "cal"),
    ("quanto tempo a Terra demora para dar uma volta completa em volta do Sol?", "365 dias", "parafrase", "cal"),
    ("por que a lua brilha se não tem luz?", "reflete a luz do Sol", "parafrase", "aval"),
    ("qual planeta fica mais perto do Sol?", "mais próximo do Sol", "parafrase", "aval"),
    ("quais planetas têm o chão duro?", "planetas rochosos", "parafrase", "aval"),
    # Fotossíntese
    ("o que é fotossíntese", "processo pelo qual as plantas produzem", "literal", "cal"),
    ("o que é a clorofila", "pigmento verde", "literal", "cal"),
    ("o que a planta produz na fotossíntese", "produz glicose", "literal", "aval"),
    ("do que a planta precisa para fazer fotossíntese", "luz do Sol, a água", "literal", "aval"),
    ("por que as florestas e as algas são importantes", "florestas e as algas", "literal", "aval"),
    ("por que as folhas são verdes?", "pigmento verde", "parafrase", "cal"),
    ("o que acontece com uma planta que fica no escuro?", "lugar escuro", "parafrase", "cal"),
    ("de onde vem o ar que a gente respira?", "oxigênio liberado pelas plantas", "parafrase", "aval"),
    ("como a planta bebe água?", "retirada do solo pelas raízes", "parafrase", "aval"),
    ("que tipo de açúcar a planta fabrica?", "glicose", "parafrase", "aval"),
    # Substantivos e adjetivos
    ("o que é substantivo", "dá nome aos seres", "literal", "cal"),
    ("o que é adjetivo", "dá uma característica", "literal", "cal"),
    ("o que é substantivo próprio", "substantivo próprio nomeia", "literal", "aval"),
    ("o que é substantivo comum", "substantivo comum nomeia", "literal", "aval"),
    ("o adjetivo concorda com o substantivo?", "concorda com o substantivo", "literal", "aval"),
    ("quando eu escrevo com letra grande no começo?", "letra inicial maiúscula", "parafrase", "cal"),
    ("como eu sei se uma palavra é adjetivo?", "perguntar como é o substantivo", "parafrase", "cal"),
    ("me dá exemplos de palavras que dão nome às coisas", "Casa, menino", "parafrase", "aval"),
    ("por que se fala a gata preta e não a gata preto?", "gata preta", "parafrase", "aval"),
    ("qual é a palavra que diz como uma coisa é?", "dá uma característica", "parafrase", "aval"),
]

CALIBRACAO = [p for p in PERGUNTAS if p[3] == "cal"]
AVALIACAO = [p for p in PERGUNTAS if p[3] == "aval"]
assert len(PERGUNTAS) == 50 and len(CALIBRACAO) == 20 and len(AVALIACAO) == 30
