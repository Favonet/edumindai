"""Amostras rotuladas para o classificador de sentimento (RF004).

AMOSTRA_CP3: as 20 frases usadas no relatório parcial (v0.1.0).
AMOSTRA_NOVA: 40 frases escritas e rotuladas ANTES de qualquer mudança no classificador da
v0.2.0, para medir a nova versão sem ajustá-la às próprias frases de teste.

Critério do rótulo: como o estudante está no conjunto (humor escolhido + comentário).
Contraste ("mas", "só que") pesa mais na parte final da frase. Rótulos do desenvolvedor;
servem para comparar versões, não para medir o desempenho real com estudantes.
"""

AMOSTRA_CP3 = [  # (humor, comentário, rótulo esperado)
    (5, "muito feliz hoje!", "positivo"), (4, "gostei da aula", "positivo"), (4, "", "positivo"),
    (3, "normal", "neutro"), (3, "dormi pouco", "neutro"), (2, "estou cansada e triste", "negativo"),
    (1, "", "negativo"), (3, "não estou bem hoje", "negativo"),
    (4, "não gostei da prova mas tudo bem", "neutro"), (2, "brigaram comigo no ônibus", "negativo"),
    (5, "joguei bola com meus amigos", "positivo"), (3, "fiquei confuso na aula", "negativo"),
    (4, "aprendi frações", "positivo"), (2, "", "negativo"), (3, "foi legal", "neutro"),
    (1, "não aguento mais", "negativo"), (4, "estou com sono", "neutro"), (5, "", "positivo"),
    (3, "meu cachorro ficou doente", "negativo"), (2, "tô de boa", "negativo"),
]

AMOSTRA_NOVA = [
    (4, "a aula foi chata mas o recreio foi muito legal", "positivo"),
    (3, "gostei do lanche mas briguei com meu irmão", "negativo"),
    (2, "tirei nota baixa e fiquei muito chateado", "negativo"),
    (5, "hoje foi incrível, fiz um amigo novo", "positivo"),
    (3, "tô meio cansado", "neutro"),
    (3, "nada demais", "neutro"),
    (4, "curti a aula de ciências", "positivo"),
    (2, "me zoaram de novo no recreio", "negativo"),
    (1, "ninguém quis fazer trabalho comigo", "negativo"),
    (3, "estou com saudade da minha avó", "negativo"),
    (4, "estou tranquilo", "positivo"),
    (2, "tô entediado, a aula foi muito chata", "negativo"),
    (5, "consegui ler o livro inteiro sozinho!", "positivo"),
    (3, "mais ou menos", "neutro"),
    (2, "meu pai e minha mãe brigaram ontem", "negativo"),
    (4, "fiquei nervoso na apresentação mas deu tudo certo", "positivo"),
    (3, "não foi ruim", "neutro"),
    (4, "não tive problemas hoje", "positivo"),
    (2, "estou com dor de cabeça", "negativo"),
    (3, "a professora me ajudou", "positivo"),
    (5, "amei o passeio da escola", "positivo"),
    (1, "estou muito triste e com medo", "negativo"),
    (3, "acordei atrasado", "neutro"),
    (4, "foi um dia bom", "positivo"),
    (2, "estou preocupada com a prova", "negativo"),
    (3, "não entendi nada da matéria", "negativo"),
    (4, "entendi a matéria de frações", "positivo"),
    (3, "um pouco cansada mas feliz", "positivo"),
    (2, "ninguém conversou comigo", "negativo"),
    (5, "tô de boa, tudo tranquilo", "positivo"),
    (3, "hoje teve prova", "neutro"),
    (4, "brinquei com meus colegas", "positivo"),
    (2, "fiquei irritado com a bagunça da sala", "negativo"),
    (3, "não estou triste", "neutro"),
    (1, "foi o pior dia", "negativo"),
    (4, "gostei, mas estou um pouco cansado", "positivo"),
    (3, "fiquei com vergonha de ler em voz alta", "negativo"),
    (5, "estou orgulhoso do meu desenho", "positivo"),
    (2, "o ônibus atrasou e perdi a primeira aula", "negativo"),
    (3, "a comida estava boa", "positivo"),
]

assert len(AMOSTRA_CP3) == 20 and len(AMOSTRA_NOVA) == 40
