import numpy as np
import random
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import unidecode

def carregar_vocabulario(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        palavras = set(unidecode.unidecode(l.strip().lower()) for l in f if len(l.strip()) >= 3)
    return {p: min(len(p)**2, 100) for p in palavras if len(p) >= 4}

def gerar_chave_eficiente():
    while True:
        m = np.random.randint(0, 26, size=(3, 3))
        m[0, 0] = m[1, 1] = m[2, 2] = random.choice([1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25])
        det = int(round(np.linalg.det(m))) % 26
        if det % 2 != 0:
            return tuple(m.flatten())

def avaliacao_rapida(texto, vocabulario):
    score = 0
    palavras_encontradas = set()
    for tamanho in range(4, 9):
        for i in range(len(texto) - tamanho + 1):
            palavra = texto[i:i+tamanho]
            if palavra in vocabulario and palavra not in palavras_encontradas:
                score += vocabulario[palavra]
                palavras_encontradas.add(palavra)
    return score

def busca_inteligente(ciphertext, vocabulario, num_chaves=20000, num_processos=None):
    if num_processos is None:
        num_processos = cpu_count() - 1 or 1
    ciphertext = ''.join(c for c in ciphertext.lower() if c.isalpha())

    args = [(gerar_chave_eficiente(), ciphertext, vocabulario) for _ in range(num_chaves)]

    resultados = []
    with Pool(num_processos) as pool:
        for score, chave, texto in tqdm(pool.imap_unordered(testar_chave_otimizado, args),
                                        total=num_chaves, desc="Testando chaves"):
            if score > 0:
                resultados.append((score, chave, texto))
    return sorted(resultados, key=lambda x: x[0], reverse=True)[:10]

def testar_chave_otimizado(args):
    chave, ciphertext, vocabulario = args
    try:
        m = np.array(chave).reshape(3, 3)
        texto = descriptografar_hill_otimizado(ciphertext, m)
        if texto:
            score = avaliacao_rapida(texto, vocabulario)
            return (score, chave, texto)
    except Exception:
        pass
    return (0, None, None)

def matriz_inversa_modular(mat, mod):
    det = int(round(np.linalg.det(mat))) % mod
    if det % 2 == 0:
        return None
    try:
        inv_det = pow(det, -1, mod)
    except ValueError:
        return None

    cof = np.zeros((3, 3), dtype=int)
    for r in range(3):
        for c in range(3):
            minor = np.delete(np.delete(mat, r, axis=0), c, axis=1)
            cof[r, c] = ((-1) ** (r + c)) * int(round(np.linalg.det(minor))) % mod

    return (inv_det * cof.T) % mod

def descriptografar_hill_otimizado(texto, chave_matriz):
    inv_chave = matriz_inversa_modular(chave_matriz, 26)
    if inv_chave is None:
        return None
    letras = np.array([ord(c) - ord('a') for c in texto], dtype=np.int8)
    padding = (-len(letras)) % 3
    if padding:
        letras = np.append(letras, [4] * padding)  # 'e' = 4
    vetores = letras.reshape(-1, 3)
    decifrado = (vetores @ inv_chave.T) % 26
    return ''.join(chr(c + ord('a')) for c in decifrado.flatten())[:len(texto)]

def segmentar_texto_rapido(texto, vocabulario, max_len=8):
    palavras = []
    i = 0
    while i < len(texto):
        for j in range(min(i + max_len, len(texto)), i, -1):
            palavra = texto[i:j]
            if palavra in vocabulario:
                palavras.append(palavra)
                i = j
                break
        else:
            palavras.append(texto[i])
            i += 1
    return palavras

# ------------------- Execução Principal -------------------
if __name__ == "__main__":
    ciphertext = "tkubgnclaamrgrymvkojsrnafvyvkzsgsqgsfgwwhyrqbqkljpzwayylsnxsqzskuclvbhrfqoaekyicwwhyacsuecubktgntgqekyfhsykqksucyqgskwsf"
    caminho_vocabulario = "palavras.txt"

    print("Carregando vocabulário...")
    vocabulario = carregar_vocabulario(caminho_vocabulario)

    print("\nIniciando ataque...")
    resultados = busca_inteligente(ciphertext, vocabulario, num_chaves=50000)

    print("\nTop 3 resultados:")
    for i, (score, chave, texto) in enumerate(resultados[:3], 1):
        print(f"\nResultado #{i} (Score: {score})")
        print("Chave:")
        for linha in np.array(chave).reshape(3, 3):
            print(linha)
        print(f"\nTexto: {texto[:100]}...")
        print(f"Segmentação: {' '.join(segmentar_texto_rapido(texto[:50], vocabulario))}...")
