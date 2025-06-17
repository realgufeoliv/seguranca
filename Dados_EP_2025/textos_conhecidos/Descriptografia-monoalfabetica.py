import string
import random
import math
from collections import Counter

ALPHABET = string.ascii_lowercase

def preprocess_text(text):
    text = text.lower()
    return ''.join(c for c in text if c in ALPHABET)

def get_ngrams(text, n):
    return [text[i:i+n] for i in range(len(text)-n+1)]

def extrair_frequencias_ngrams(texto_base):
    texto = preprocess_text(texto_base)
    bigrams = get_ngrams(texto, 2)
    trigrams = get_ngrams(texto, 3)

    total_bigrams = len(bigrams)
    total_trigrams = len(trigrams)

    freq_bigram = Counter(bigrams)
    freq_trigram = Counter(trigrams)

    for k in freq_bigram:
        freq_bigram[k] /= total_bigrams
    for k in freq_trigram:
        freq_trigram[k] /= total_trigrams

    return freq_bigram, freq_trigram

def score_ngrams(text, freq_bigram, freq_trigram):
    text = preprocess_text(text)
    bigrams = get_ngrams(text, 2)
    trigrams = get_ngrams(text, 3)

    score = 0.0

    bigram_counts = Counter(bigrams)
    for bg, count in bigram_counts.items():
        freq = freq_bigram.get(bg, 1e-6)  # valor pequeno para n-gramas raros
        score += math.log(freq) * count

    trigram_counts = Counter(trigrams)
    for tg, count in trigram_counts.items():
        freq = freq_trigram.get(tg, 1e-6)
        score += math.log(freq) * count

    return score

def decifra(texto_cifrado, chave):
    mapa = {c: chave[i] for i, c in enumerate(ALPHABET)}
    inv_mapa = {v: k for k, v in mapa.items()}

    resultado = []
    for c in texto_cifrado.lower():
        if c in ALPHABET:
            resultado.append(inv_mapa.get(c, c))
        else:
            resultado.append(c)
    return ''.join(resultado)

def gerar_vizinho(chave):
    chave_lista = list(chave)
    i, j = random.sample(range(len(chave_lista)), 2)
    chave_lista[i], chave_lista[j] = chave_lista[j], chave_lista[i]
    return ''.join(chave_lista)

def simulated_annealing(texto_cifrado, freq_bigram, freq_trigram,
                        temp_inicial=10.0, temp_final=0.01, alpha=0.95, iteracoes_por_temp=5000):
    chave_atual = ''.join(random.sample(ALPHABET, len(ALPHABET)))
    texto_decifrado = decifra(texto_cifrado, chave_atual)
    score_atual = score_ngrams(texto_decifrado, freq_bigram, freq_trigram)

    melhor_chave = chave_atual
    melhor_score = score_atual

    temp = temp_inicial

    while temp > temp_final:
        for _ in range(iteracoes_por_temp):
            chave_vizinha = gerar_vizinho(chave_atual)
            texto_vizinho = decifra(texto_cifrado, chave_vizinha)
            score_vizinho = score_ngrams(texto_vizinho, freq_bigram, freq_trigram)

            delta = score_vizinho - score_atual
            
            if delta > 0 or random.random() < math.exp(delta / temp):
                chave_atual = chave_vizinha
                score_atual = score_vizinho

                if score_atual > melhor_score:
                    print(decifra(texto_cifrado, chave_atual))
                    melhor_score = score_atual
                    melhor_chave = chave_atual

        print(f"Temp: {temp:.4f} | Score: {melhor_score:.4f} | Chave: {melhor_chave}")
        temp *= alpha

    return melhor_chave, melhor_score

if __name__ == "__main__":
    # Lê arquivo texto base
    caminho_arquivo = "texto_base.txt"  # coloque aqui o caminho para seu arquivo txt
    with open(  'avesso_da_pele.txt', "r", encoding="latin-1") as f:
        texto_base = f.read()

    texto_cifrado = "iqnjivhaqjhgwbacivpjmwqarrjabaqhuhafawghfoamhfoihvwyavagiyakavjqarajuariwnjhqwfwivalavwauiqmhrrwfaiywlarjaqaighfoadwugam"

    freq_bigram, freq_trigram = extrair_frequencias_ngrams(texto_base)
    chave, score = simulated_annealing(texto_cifrado, freq_bigram, freq_trigram)

    print("\nMelhor chave encontrada:", chave)
    texto_decifrado = decifra(texto_cifrado, 'aelmibkohpsuqfwynvrgjdtxzc')
    print("\nTexto decifrado:\n", texto_decifrado)
