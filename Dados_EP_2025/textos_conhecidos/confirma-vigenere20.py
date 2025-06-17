def letra_para_num(c):
    return ord(c.upper()) - ord('A')

def num_para_letra(n):
    return chr((n % 26) + ord('A'))

def descobrir_chave_vigenere(texto_claro, texto_cifrado, tamanho_chave=20):
    chave_expandida = []
    
    for i in range(len(texto_claro)):
        num_cifrado = letra_para_num(texto_cifrado[i])
        num_claro = letra_para_num(texto_claro[i])
        num_chave = (num_cifrado - num_claro) % 26
        chave_expandida.append(num_para_letra(num_chave))
    
    # Obtem a chave original de tamanho 20
    chave_candidata = ''.join(chave_expandida[:tamanho_chave])

    # Valida a chave
    for i in range(len(texto_claro)):
        k = letra_para_num(chave_candidata[i % tamanho_chave])
        c = letra_para_num(texto_claro[i])
        esperado = (c + k) % 26
        real = letra_para_num(texto_cifrado[i])
        if esperado != real:
            raise ValueError("Chave de tamanho 20 não é compatível com o texto.")
    
    return chave_candidata

def vigenere_decifrar(cifrado, chave):
    texto_claro = []

    for i in range(len(cifrado)):
        num_c = letra_para_num(cifrado[i])
        num_k = letra_para_num(chave[i % len(chave)])
        num_t = (num_c - num_k + 26) % 26
        texto_claro.append(num_para_letra(num_t))

    return ''.join(texto_claro)

# ==== Exemplo de uso ====
texto_claro = "emsuficienteparaquebrarasregrasconservadorasdaepocaeelamesmaconvidasseseupaiparasairetomarumacervejaMasseupainaobebiaseu"
texto_cifrado = "zrzbwrikyidhjzgpsifymfyhjakilvcfimhttjbajwhzujkrixkhykpbggnxxtuczmgumzchoopxrosxnfpyvcuoumepubtgxskxhfzzvdvccikrvdqxcgfr"

# 1. Descobrir a chave
chave = descobrir_chave_vigenere(texto_claro, texto_cifrado, tamanho_chave=20)
print("🔑 Chave descoberta:", chave)

# 2. Descriptografar a mensagem com a chave
texto_decifrado = vigenere_decifrar(texto_cifrado, chave)
print("📜 Texto decifrado:", texto_decifrado)

# 3. Confirmar se bate com o original
print("✅ Confere com o original:", texto_decifrado == texto_claro)


# Para testar, você pode ajustar os textos para que tenham pelo menos 20 caracteres
chave = descobrir_chave_vigenere(texto_claro, texto_cifrado, 20)
print("Chave descoberta:", chave)