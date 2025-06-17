import numpy as np
import string
import unicodedata
import re
import random
import os
from collections import Counter

ALPHABET = string.ascii_uppercase
MOD = 26

def clean_text(text):
    return ''.join([c for c in text.upper() if c in ALPHABET])

def text_to_vector(text):
    return [ALPHABET.index(c) for c in text]

def vector_to_text(vec):
    return ''.join([ALPHABET[i % 26] for i in vec])

def decrypt_hill(ciphertext, key_matrix):
    ciphertext = clean_text(ciphertext)
    while len(ciphertext) % 4 != 0:
        ciphertext += 'X'

    inv_key = matrix_mod_inv(key_matrix, MOD)
    if inv_key is None:
        return None

    plaintext = ""
    for i in range(0, len(ciphertext), 4):
        block = np.array(text_to_vector(ciphertext[i:i+4]))
        decrypted_block = inv_key.dot(block) % MOD
        plaintext += vector_to_text(decrypted_block)

    return plaintext

def matrix_mod_inv(matrix, mod):
    try:
        det = int(round(np.linalg.det(matrix))) % mod
        det_inv = modinv(det, mod)
        if det_inv is None:
            return None
        adjugate = np.round(det * np.linalg.inv(matrix)).astype(int) % mod
        return (det_inv * adjugate) % mod
    except:
        return None

def modinv(a, m):
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def generate_random_invertible_4x4_matrices(qtd=1000):
    matrices = []
    chaves_str = set()
    tentativas = 0
    while len(matrices) < qtd and tentativas < qtd * 10:
        mat = np.random.randint(0, 26, size=(4, 4))
        det = int(round(np.linalg.det(mat))) % 26
        if det != 0 and modinv(det, 26) is not None:
            chave_str = matriz_para_str(mat)
            if chave_str not in chaves_str:
                matrices.append(mat)
                chaves_str.add(chave_str)
        tentativas += 1
    return matrices


def segmentar_texto(texto, vocab):
    texto = texto.upper()
    i = 0
    palavras = []
    while i < len(texto):
        encontrada = False
        for j in range(min(len(texto), i + 15), i + 2, -1):
            palavra = texto[i:j]
            if palavra in vocab:
                palavras.append(palavra)
                i = j
                encontrada = True
                break
        if not encontrada:
            i += 1
    return palavras

def vogal_bonus(text):
    vogais = set("AEIOU")
    total = len(text)
    if total == 0:
        return 0
    num_vogais = sum(1 for c in text if c in vogais)
    proporcao = num_vogais / total
    return int(proporcao * 100)

def count_vocab_matches(text, vocab_freq, original_ciphertext):
    palavras = segmentar_texto(text, vocab_freq)
    contagem = Counter(palavras)
    score = 0

    for palavra, freq in contagem.items():
        # Só contabiliza se a palavra está no vocab (já está, pois segmentar_texto filtra)
        # Bônus se a palavra está no ciphertext original
        bonus = 10 if palavra in original_ciphertext else 0
        
        # Score valoriza palavras maiores com peso quadrático no tamanho * frequência + bônus
        score += (len(palavra) ** 2) * vocab_freq.get(palavra, 1) + bonus

    # Bônus de vogais na palavra
    score += vogal_bonus(text)

    return score




def salvar_matriz(nome_arquivo, matriz):
    with open(nome_arquivo, "a") as f:
        flat = ','.join(map(str, matriz.flatten()))
        f.write(flat + "\n")

def carregar_matrizes(nome_arquivo):
    if not os.path.exists(nome_arquivo):
        return set()
    with open(nome_arquivo, "r") as f:
        return set(line.strip() for line in f.readlines())

def matriz_para_str(matriz):
    return ','.join(map(str, matriz.flatten()))

def break_hill_with_vocab(ciphertext, vocab_freq, max_matrices=10000):
    ciphertext = clean_text(ciphertext)
    best_score = float('-inf')
    best_plain = ""
    best_key = None

    ruins = carregar_matrizes("matrizes_ruins.txt")
    boas = carregar_matrizes("matrizes_boas.txt")
    print(f"Gerando e testando até {max_matrices} matrizes 4x4 invertíveis...")

    matrices = generate_random_invertible_4x4_matrices(max_matrices)

    melhores_chaves = set()
    melhores_textos = set()

    for i, key in enumerate(matrices):
        key_str = matriz_para_str(key)
        if key_str in ruins or key_str in boas:
            continue

        plain = decrypt_hill(ciphertext, key)
        if plain is None:
            continue

        if plain.count('W') > 1 or plain.count('Y') > 1 or plain.count('K') > 2:
            salvar_matriz("matrizes_ruins.txt", key)
            continue

        score = count_vocab_matches(plain, vocab_freq, ciphertext)

        if score == 0:
            salvar_matriz("matrizes_ruins.txt", key)
        else:
            salvar_matriz("matrizes_boas.txt", key)

        # Só atualiza se o score for melhor e a chave e texto ainda não foram usados
        if score > best_score and key_str not in melhores_chaves and plain not in melhores_textos:
            best_score = score
            best_plain = plain
            best_key = key
            melhores_chaves.add(key_str)
            melhores_textos.add(plain)

        if i % 100 == 0:
            print(best_plain[:100])
            print(f"{i} matrizes testadas... Melhor score até agora: {best_score}")

    return best_key, best_plain


def carregar_vocabulario_com_frequencia(caminho_arquivo):
    with open(caminho_arquivo, 'r', encoding='latin-1') as f:
        texto = f.read()

    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('latin-1')

    palavras = re.findall(r'\b[a-zA-Z]{3,}\b', texto)
    palavras = [p.upper() for p in palavras]

    contagem = Counter(palavras)
    return dict(contagem)  # retorna dicionário palavra->frequência

if __name__ == "__main__":
    ciphertext = "gaigmwrcbgzczweanigkdctvdjeczwnnxwxecfqvgqoclxxniyckxfuapigubwvgasrubgxahtobwcckxfuajoeuzevgsarbezapcotakylekauewhygieiu"

    vocab_freq = carregar_vocabulario_com_frequencia("avesso_da_pele.txt")
    print(f"Vocabulário carregado com {len(vocab_freq)} palavras.")
    print(vocab_freq)
    key, plain = break_hill_with_vocab(ciphertext, vocab_freq, max_matrices=3000000)

    print("\nMelhor matriz chave encontrada:")
    print(key)
    print("\nTexto decriptado:")
    print(plain)

    print("\nPalavras segmentadas encontradas:")
    palavras = segmentar_texto(plain, vocab_freq)
    print(palavras)
