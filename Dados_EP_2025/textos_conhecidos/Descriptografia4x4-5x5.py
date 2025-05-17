import string
from itertools import product
from math import gcd
from unidecode import unidecode
import numpy as np
from numpy.linalg import LinAlgError

# --- Configurações ---
MOD = 26
ALPHABET = string.ascii_lowercase
ALPHA_MAP = {c: i for i, c in enumerate(ALPHABET)}
REVERSE_ALPHA_MAP = {i: c for i, c in enumerate(ALPHABET)}

# --- Utilitários ---
def text_to_numbers(text):
    return [ALPHA_MAP[c] for c in text.lower() if c in ALPHA_MAP]

def numbers_to_text(numbers):
    return ''.join(REVERSE_ALPHA_MAP[n % MOD] for n in numbers)

def mod_inverse(a, m):
    for i in range(1, m):
        if (a * i) % m == 1:
            return i
    return None

def matrix_inverse(matrix, mod=MOD):
    det = round(np.linalg.det(matrix)) % mod
    if gcd(det, mod) != 1:
        return None
    det_inv = mod_inverse(det, mod)
    if det_inv is None:
        return None
    try:
        adj = np.round(np.linalg.inv(matrix) * det).astype(int) % mod
        inv = (det_inv * adj) % mod
        return inv.tolist()
    except LinAlgError:
        return None

def montar_blocos(vetor, tamanho):
    return [vetor[i:i+tamanho] for i in range(0, len(vetor), tamanho)]

def multiplicar_matriz(A, B, mod=MOD):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) % mod
             for j in range(len(B[0]))] for i in range(len(A))]

# --- Nova heurística baseada em frequência ---
# Frequências médias das letras no português (fonte: https://pt.wikipedia.org/wiki/Frequ%C3%AAncia_de_letras)
FREQ_PT = {
    'a': 0.1463, 'b': 0.0104, 'c': 0.0388, 'd': 0.0499, 'e': 0.1257,
    'f': 0.0102, 'g': 0.0130, 'h': 0.0078, 'i': 0.0618, 'j': 0.0040,
    'k': 0.0002, 'l': 0.0278, 'm': 0.0474, 'n': 0.0505, 'o': 0.1073,
    'p': 0.0252, 'q': 0.0120, 'r': 0.0653, 's': 0.0781, 't': 0.0434,
    'u': 0.0463, 'v': 0.0167, 'w': 0.0001, 'x': 0.0020, 'y': 0.0001,
    'z': 0.0047
}

def score_texto(texto):
    """Calcula uma pontuação de quão parecido o texto está com português,
    baseada na frequência das letras."""
    if not texto:
        return 0
    total = len(texto)
    contagem = {c: 0 for c in ALPHABET}
    for c in texto:
        if c in contagem:
            contagem[c] += 1
    score = 0
    for letra, freq_esperada in FREQ_PT.items():
        freq_texto = contagem[letra] / total
        score += (freq_texto - freq_esperada)**2
    # Score menor = mais parecido (distância quadrática)
    return -score  # para ordenar decrescente (maior é melhor)

# --- Funções principais ---
def carregar_texto_base(path):
    with open(path, 'r', encoding='latin-1') as f:
        texto = f.read()
    texto = unidecode(texto.lower())
    return ''.join(c for c in texto if c in ALPHA_MAP)

def tentar_chaves(texto_claro, texto_cifrado, tamanho_chave, max_resultados=10):
    texto_cifrado_numeros = text_to_numbers(texto_cifrado)
    bloco_tamanho = tamanho_chave * tamanho_chave
    melhores_resultados = []

    # Agora varremos posições do texto claro e cifrado
    for i in range(0, len(texto_claro) - bloco_tamanho + 1):
        trecho_claro = text_to_numbers(texto_claro[i:i+bloco_tamanho])
        if len(trecho_claro) != bloco_tamanho:
            continue
        P = montar_blocos(trecho_claro, tamanho_chave)
        Pinv = matrix_inverse(P)
        if Pinv is None:
            continue

        for j in range(0, len(texto_cifrado_numeros) - bloco_tamanho + 1):
            trecho_cifrado = texto_cifrado_numeros[j:j+bloco_tamanho]
            if len(trecho_cifrado) != bloco_tamanho:
                continue
            C = montar_blocos(trecho_cifrado, tamanho_chave)

            try:
                K = multiplicar_matriz(C, Pinv)

                # Decifragem de todo o texto cifrado usando K
                blocos_cif = montar_blocos(texto_cifrado_numeros, tamanho_chave)
                texto_decifrado = []
                for bloco in blocos_cif:
                    if len(bloco) < tamanho_chave:
                        bloco += [0] * (tamanho_chave - len(bloco))
                    resultado = multiplicar_matriz(K, [[x] for x in bloco])
                    texto_decifrado.extend([linha[0] for linha in resultado])
                texto_final = numbers_to_text(texto_decifrado)

                # Nova heurística
                s = score_texto(texto_final)
                if s > -0.02:  # Ajuste esse limite conforme necessário
                    melhores_resultados.append((i, j, K, texto_final[:300], s))

            except Exception:
                continue

            if len(melhores_resultados) >= max_resultados:
                break
        if len(melhores_resultados) >= max_resultados:
            break

    # Ordena pelos scores melhores (maiores)
    melhores_resultados.sort(key=lambda x: x[4], reverse=True)
    return melhores_resultados

# --- Execução ---
if __name__ == '__main__':
    cifra = 'gaigmwrcbgzczweanigkdctvdjeczwnnxwxecfqvgqoclxxniyckxfuapigubwvgasrubgxahtobwcckxfuajoeuzevgsarbezapcotakylekauewhygieiu'

    texto_base = carregar_texto_base('avesso_da_pele.txt')
    print(f"✅ Texto base carregado com {len(texto_base)} caracteres")

    with open('resultados_chave.txt', 'w', encoding='utf-8') as f_res:
        for tamanho in [4, 5]:
            print(f"\n🔍 Tentando descobrir chave {tamanho}x{tamanho}...")
            resultados = tentar_chaves(texto_base, cifra, tamanho)

            if resultados:
                for idx, (pos_claro, pos_cif, chave, preview, score) in enumerate(resultados):
                    print(f"\n#{idx + 1} 🔑 Posição texto claro: {pos_claro}, texto cifrado: {pos_cif} | Score: {score:.6f}")
                    for linha in chave:
                        print(linha)
                    print(f"📜 Preview do texto decifrado: {preview[:200]}...\n")

                    # Grava no arquivo resultados
                    f_res.write(f"#{idx + 1} Posição texto claro: {pos_claro}, texto cifrado: {pos_cif} | Score: {score:.6f}\n")
                    for linha in chave:
                        f_res.write(str(linha) + '\n')
                    f_res.write(f"Preview: {preview}\n\n")
            else:
                print("❌ Nenhuma chave plausível encontrada.")
