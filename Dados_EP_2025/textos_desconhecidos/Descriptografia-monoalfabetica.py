import math
import random
import string

def carregar_vocabulario(caminho='palavras.txt'):
    with open(caminho, 'r', encoding='utf-8') as f:
        return set(line.strip().lower() for line in f if line.strip())

def carregar_bigramas(caminho='bigrams.txt'):
    bigramas = {}
    with open(caminho, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                bigramas[parts[0]] = float(parts[1])
    return bigramas

MIN_PROB = 1e-10

def score_bigram(texto, bigram_freq):
    texto = texto.lower()
    score = 0.0
    total = 0
    for i in range(len(texto) - 1):
        bg = texto[i:i+2]
        if any(c not in string.ascii_lowercase for c in bg):
            continue
        p = bigram_freq.get(bg, MIN_PROB)
        score += math.log(p)
        total += 1
    return score / total if total > 0 else -float('inf')

def segmentar_e_pontuar(texto, vocab, max_len=20):
    texto = texto.lower()
    n = len(texto)
    dp = [0]*(n+1)
    print(f'texto {texto}')
    for i in range(1, n+1):
        melhor = 0
        for j in range(max(0, i - max_len), i):
            if texto[j:i] in vocab and len(texto[j:i]) >= 4:
                pontuacao = dp[j] + (i - j)  # soma comprimento palavra
                if pontuacao > melhor:
                    melhor = pontuacao
        dp[i] = max(dp[i-1], melhor)  # permite "não palavra" contando caractere isolado como zero

    
    return dp[n]

def decodificar(texto_cifrado, chave_str):
    # chave_str é string de 26 letras indicando a permutação do alfabeto
    tabela = str.maketrans(string.ascii_lowercase, chave_str)
    return texto_cifrado.translate(tabela)

def chave_inicial(seed=None):
    letras = list(string.ascii_lowercase)
    if seed is not None:
        random.seed(seed)
    random.shuffle(letras)
    return ''.join(letras)

def trocar_letras(chave_str, i, j):
    # troca caracteres na posição i e j
    lista = list(chave_str)
    lista[i], lista[j] = lista[j], lista[i]
    return ''.join(lista)

def simulated_annealing(texto_cifrado, vocab, bigram_freq, max_iter=500000,
                        temp_init=5.0, temp_final=0.01, alpha=0.995, seed=42):

    random.seed(seed)

    chave_atual = chave_inicial(seed)
    texto_atual = decodificar(texto_cifrado, chave_atual)
    score_big = score_bigram(texto_atual, bigram_freq)
    score_seg = segmentar_e_pontuar(texto_atual, vocab)
    print(f'score_big:{score_big} score_seg:{score_seg}')
    score_atual = 0.7 * score_big + 0.3 * (score_seg / len(texto_atual))  # normalizado
    melhor_chave = chave_atual
    melhor_score = score_atual

    temperatura = temp_init
    letras = string.ascii_lowercase

    for iter in range(max_iter):
        i, j = random.sample(range(26), 2)
        nova_chave = trocar_letras(chave_atual, i, j)
        novo_texto = decodificar(texto_cifrado, nova_chave)
        score_big = score_bigram(novo_texto, bigram_freq)
        score_seg = segmentar_e_pontuar(novo_texto, vocab)
        score_novo = 0.7 * score_big + 0.3 * (score_seg / len(novo_texto))

        delta = score_novo - score_atual

        if delta > 0 or math.exp(delta / temperatura) > random.random():
            chave_atual = nova_chave
            score_atual = score_novo

            if score_novo > melhor_score:
                melhor_score = score_novo
                melhor_chave = nova_chave
                print(f'Iter {iter} | Melhor score: {melhor_score:.5f}')
                print(f'Trecho texto: {novo_texto[:80]}')

        temperatura = max(temp_final, temperatura * alpha)

    return melhor_chave

def main():
    texto_cifrado = 'dstnpwhwrtwzmntudwjiffblmjpfndhitblmlmjmlwnzwstunmjwfmdstnmlptwimlwnwlufntbutlmwzufbiwhdbtlwlmhflwnzfbbfhdzimiflmzsfztfz'

    vocab = carregar_vocabulario('palavras.txt')
    bigram_freq = carregar_bigramas('bigrams.txt')

    print('Iniciando simulated annealing...')
    melhor_chave = simulated_annealing(texto_cifrado, vocab, bigram_freq)

    texto_decifrado = decodificar(texto_cifrado, melhor_chave)
    print('\nTexto decifrado completo:')
    print(texto_decifrado)
    print('\nChave encontrada:')
    print(''.join(melhor_chave))

if __name__ == '__main__':
    main()
