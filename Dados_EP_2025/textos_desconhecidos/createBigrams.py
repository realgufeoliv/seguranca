import re
from collections import Counter, defaultdict

def gerar_bigrams(arquivo_entrada='palavras.txt', arquivo_saida='bigrams.txt'):
    with open(arquivo_entrada, 'r', encoding='latin-1') as f:
        texto = f.read().lower()

    # Remover tudo que não for letra ou espaço
    texto = re.sub(r'[^a-záéíóúâêôãõç ]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto)

    bigramas = Counter()

    # Vamos contar apenas bigramas de letras a-z para simplificar (sem acentos)
    texto = re.sub(r'[^a-z ]', '', texto)

    texto = texto.replace(' ', '')  # só letras, para bigramas contínuos

    for i in range(len(texto) - 1):
        bg = texto[i:i+2]
        bigramas[bg] += 1

    total = sum(bigramas.values())
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        for bg, count in bigramas.most_common():
            freq = count / total
            f.write(f"{bg} {freq:.8f}\n")

    print(f'Arquivo {arquivo_saida} criado com {len(bigramas)} bigramas')
gerar_bigrams()
# Exemplo para gerar os bigramas
# gerar_bigrams('corpus.txt', 'bigrams.txt')
