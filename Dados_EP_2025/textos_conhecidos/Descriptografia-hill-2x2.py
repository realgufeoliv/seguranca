import string
from itertools import product
from math import gcd
from unidecode import unidecode

alpha = string.ascii_lowercase
alpha_map = {letter: idx for idx, letter in enumerate(alpha)}
reverse_alpha_map = {idx: letter for idx, letter in enumerate(alpha)}

def text_to_numbers(text):
    return [alpha_map[letter] for letter in text if letter in alpha_map]

def numbers_to_text(numbers):
    return ''.join([reverse_alpha_map[num] for num in numbers])

def mod_inverse(a, m):
    for i in range(1, m):
        if (a * i) % m == 1:
            return i
    return None

def matrix_inverse(matrix, mod=26):
    det = (matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]) % mod
    if gcd(det, mod) != 1:
        return None
    det_inv = mod_inverse(det, mod)
    if det_inv is None:
        return None
    adj = [[matrix[1][1], -matrix[0][1]], [-matrix[1][0], matrix[0][0]]]
    inv = [
        [(det_inv * adj[0][0]) % mod, (det_inv * adj[0][1]) % mod],
        [(det_inv * adj[1][0]) % mod, (det_inv * adj[1][1]) % mod]
    ]
    return inv

def matrix_multiply(matrix, vector, mod=26):
    return [
        [(matrix[0][0] * vector[0][0] + matrix[0][1] * vector[1][0]) % mod],
        [(matrix[1][0] * vector[0][0] + matrix[1][1] * vector[1][0]) % mod]
    ]

def decrypt(ciphertext, key_matrix, mod=26):
    key_inverse = matrix_inverse(key_matrix, mod)
    if key_inverse is None:
        return None
    ciphertext_numbers = text_to_numbers(ciphertext)
    if len(ciphertext_numbers) % 2 != 0:
        ciphertext_numbers.append(0)  # padding com 'a'
    plaintext_numbers = []
    for i in range(0, len(ciphertext_numbers), 2):
        block = ciphertext_numbers[i:i+2]
        decrypted_block = matrix_multiply(key_inverse, [[block[0]], [block[1]]], mod)
        plaintext_numbers.extend([decrypted_block[0][0], decrypted_block[1][0]])
    return numbers_to_text(plaintext_numbers)

def carregar_vocabulario_arquivo(path):
    with open(path, 'r', encoding='latin-1') as f:
        texto = f.read().lower()
    texto = unidecode(texto)
    palavras = set(
        ''.join(c for c in palavra if c in alpha)
        for palavra in texto.split()
        if any(c.isalpha() for c in palavra)
    )
    return palavras

def segmentar_texto(texto, vocabulario, max_desconhecidas=2):
    n = len(texto)
    dp = [None] * (n + 1)
    desconhecidas = [float('inf')] * (n + 1)
    dp[0] = []
    desconhecidas[0] = 0

    for i in range(1, n + 1):
        for j in range(max(0, i - 20), i):
            palavra = texto[j:i]
            if dp[j] is not None:
                nova_lista = dp[j] + [palavra if palavra in vocabulario else f'??{palavra}??']
                novo_contador = desconhecidas[j] + (0 if palavra in vocabulario else 1)
                if novo_contador < desconhecidas[i]:
                    dp[i] = nova_lista
                    desconhecidas[i] = novo_contador
    return dp[n]

def brute_force_hill(ciphertext, vocabulario, max_results=10):
    resultados = []

    for key in product(range(26), repeat=4):
        key_matrix = [[key[0], key[1]], [key[2], key[3]]]
        if matrix_inverse(key_matrix) is None:
            continue

        decrypted = decrypt(ciphertext, key_matrix)
        if not decrypted:
            continue
        
        texto = ''.join(c if c in alpha else '' for c in unidecode(decrypted))
        segmentacao = segmentar_texto(texto, vocabulario)
        if segmentacao is None:
            continue

        desconhecidas_count = sum(1 for palavra in segmentacao if palavra.startswith('??') and palavra.endswith('??'))
        num_palavras = len(segmentacao)
        qualidade = num_palavras - desconhecidas_count * 2

        resultados.append({
            'key': key_matrix,
            'decrypted': decrypted,
            'qualidade': qualidade,
            'segmentacao': segmentacao
        })

    if not resultados:
        print("❌ Nenhuma chave encontrada.")
        return

    resultados.sort(key=lambda x: x['qualidade'], reverse=True)

    print(f"\n🔍 Top {min(max_results, len(resultados))} resultados:\n")
    for i, res in enumerate(resultados[:max_results], 1):
        print(f"#{i} - Chave: {res['key']} | Qualidade: {res['qualidade']}")
        print(f"Texto decifrado (início): {res['decrypted'][:300]}...")
        print(f"Segmentação: {res['segmentacao'][:10]}{'...' if len(res['segmentacao']) > 10 else ''}")
        print()

# --- Uso ---

ciphertext = "wvcgmtksqkfpmecnpkgzmudavaegbuqyaukeqwifucwkeaoaeuuuvlspcnpkeatxqxafgsmpennwewgagaeecgmkwjuvscmenawtgsyvwpcyuvmetuyggkkn"

vocabulario = carregar_vocabulario_arquivo('avesso_da_pele.txt')

print("✅ Palavras no vocabulário:", len(vocabulario))
print("🧪 Teste segmentação:", segmentar_texto("elasuficientementeexcitadaestiqueiamaoepegueiacamisinhatenteiabriropacotinhocomamaomasaembalagemnaofacilitoualemdissoeun", vocabulario))

brute_force_hill(ciphertext, vocabulario)
