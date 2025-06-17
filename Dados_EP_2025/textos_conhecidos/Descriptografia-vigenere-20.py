import string
from collections import Counter
from unidecode import unidecode
from itertools import product
import re
ALPHABET = string.ascii_lowercase
ALPHABET_LEN = len(ALPHABET)

# Frequência das letras no português (%)
FREQ_PT = {
    'a': 14.63, 'e': 12.57, 'o': 10.73, 's': 7.81, 'r': 6.53, 'i': 6.18,
    'n': 5.05, 'd': 4.99, 'm': 4.74, 'u': 4.63, 't': 4.34, 'c': 3.88,
    'l': 2.78, 'p': 2.52, 'v': 1.67, 'g': 1.30, 'h': 1.28, 'q': 1.20,
    'b': 1.04, 'f': 1.02, 'z': 0.47, 'j': 0.40, 'x': 0.21, 'k': 0.02
}

# Letras muito raras em português
LETRAS_PROIBIDAS = {'w', 'y', 'k'}
PESO_VOCAB = 3
PESO_FREQ = 1
PENALIDADE_PROIBIDAS = -200

def carregar_vocabulario_arquivo(path):
    with open(path, 'r', encoding='latin-1') as f:
        texto = unidecode(f.read().lower())
    palavras = [''.join(c for c in p if c in ALPHABET) for p in texto.split()]
    return Counter(p for p in palavras if len(p) >= 4)

def vigenere_decrypt(ciphertext, key):
    return ''.join(
        ALPHABET[(ALPHABET.index(c) - ALPHABET.index(key[i % len(key)])) % ALPHABET_LEN]
        for i, c in enumerate(ciphertext) if c in ALPHABET
    )

def score_por_frequencia_letras(texto):
    """Pontua baseado na frequência esperada de letras."""
    total = 0
    counter = Counter(texto)
    for letra in ALPHABET:
        freq_esperada = FREQ_PT.get(letra, 0)
        freq_real = counter.get(letra, 0)
        total += freq_real * freq_esperada
    return total

def letras_mais_provaveis_por_posicao(ciphertext, vocab_counter, key_len, top_n=8):
    vocab_patterns = [(re.compile(r'\b' + re.escape(palavra) + r'\b'), freq)
                      for palavra, freq in vocab_counter.items() if len(palavra) > 2]
    
    letras_por_posicao = []

    for i in range(key_len):
        trecho = ciphertext[i::key_len]
        pontuacoes = []

        for shift in range(ALPHABET_LEN):
            # Decifra o trecho com o shift atual
            decifrado = ''.join(
                ALPHABET[(ALPHABET.index(c) - shift) % ALPHABET_LEN]
                for c in trecho if c in ALPHABET
            )

            # Score baseado em palavras encontradas
            score_vocab = 0
            for pattern, freq in vocab_patterns:
                if pattern.search(decifrado):
                    score_vocab += len(pattern.pattern) * freq  # mais peso a palavras maiores

            # Score baseado em frequência de letras
            score_freq = score_por_frequencia_letras(decifrado)

            # Score final ponderado (ajuste os pesos conforme testes)
            score_total = 0.6 * score_vocab + 0.4 * score_freq

            pontuacoes.append((score_total, ALPHABET[shift]))

        melhores = [letra for _, letra in sorted(pontuacoes, reverse=True)[:top_n]]
        letras_por_posicao.append(melhores)

    return letras_por_posicao

def gerar_chaves(letras_por_posicao, limite=1000):
    for i, combinacao in enumerate(product(*letras_por_posicao)):
        if i >= limite:
            break
        yield ''.join(combinacao)

def score_por_vocabulario(texto, vocab_counter):
    return sum(freq for palavra, freq in vocab_counter.items() if palavra in texto)

def score_por_frequencia(texto):
    contagem = Counter(c for c in texto if c in ALPHABET)
    total = sum(contagem.values())
    if total == 0:
        return -99999

    score = -sum(
        abs((contagem[c] / total * 100) - FREQ_PT.get(c, 0))
        for c in FREQ_PT
    )

    # Penalização para letras muito raras no português
    for letra in LETRAS_PROIBIDAS:
        score += PENALIDADE_PROIBIDAS * contagem.get(letra, 0)

    return score

def quebrar_vigenere(ciphertext, vocab_counter, key_len=20, top_n=8, limite=1000):
    letras_por_pos = letras_mais_provaveis_por_posicao(ciphertext, vocab_counter, key_len, top_n)
    melhores_resultados = []

    for chave in gerar_chaves(letras_por_pos, limite):
        texto = vigenere_decrypt(ciphertext, chave)
        score_vocab = score_por_vocabulario(texto, vocab_counter)
        score_freq = score_por_frequencia(texto)
        score_total = PESO_VOCAB * score_vocab + PESO_FREQ * score_freq
        melhores_resultados.append((score_total, chave, texto))

    melhores_resultados.sort(reverse=True)
    return melhores_resultados[:5]

# Execução
if __name__ == "__main__":
    ciphertext = 'zrzbwrikyidhjzgpsifymfyhjakilvcfimhttjbajwhzujkrixkhykpbggnxxtuczmgumzchoopxrosxnfpyvcuoumepubtgxskxhfzzvdvccikrvdqxcgfr'
    vocabulario = carregar_vocabulario_arquivo("avesso_da_pele.txt")

    resultados = quebrar_vigenere(ciphertext, vocabulario, key_len=20, top_n=20, limite=300000)

    for i, (score, chave, texto) in enumerate(resultados, 1):
        print(f"\n🔍 Tentativa #{i}")
        print("🔑 Chave:", chave)
        print(f"📜 Texto decifrado ({len(texto)} chars):\n{texto[:300]}...")
        print(f"✅ Score total: {score:.2f}")
