import string

def gerar_chaves_de_substituicao(cifrado, claro):
    ALFABETO = string.ascii_lowercase
    mapa_c2p = {}  # cifrado -> claro
    mapa_p2c = {}  # claro -> cifrado

    for c_cif, c_claro in zip(cifrado, claro):
        if c_cif in ALFABETO and c_claro in ALFABETO:
            if c_cif not in mapa_c2p:
                mapa_c2p[c_cif] = c_claro
            elif mapa_c2p[c_cif] != c_claro:
                print(f"[C2P] Aviso: Conflito para '{c_cif}': {mapa_c2p[c_cif]} ≠ {c_claro}")

            if c_claro not in mapa_p2c:
                mapa_p2c[c_claro] = c_cif
            elif mapa_p2c[c_claro] != c_cif:
                print(f"[P2C] Aviso: Conflito para '{c_claro}': {mapa_p2c[c_claro]} ≠ {c_cif}")

    # Preencher chaves de 26 letras
    chave_c2p = ['?'] * 26
    chave_p2c = ['?'] * 26

    usadas_c2p = set(mapa_c2p.values())
    usadas_p2c = set(mapa_p2c.values())

    for letra_cifrada, letra_clara in mapa_c2p.items():
        idx = ALFABETO.index(letra_cifrada)
        chave_c2p[idx] = letra_clara

    for letra_clara, letra_cifrada in mapa_p2c.items():
        idx = ALFABETO.index(letra_clara)
        chave_p2c[idx] = letra_cifrada

    # Preencher lacunas com letras restantes
    faltando_claro = [l for l in ALFABETO if l not in usadas_c2p]
    faltando_cifrado = [l for l in ALFABETO if l not in usadas_p2c]

    idx_falta = 0
    for i in range(26):
        if chave_c2p[i] == '?':
            chave_c2p[i] = faltando_claro[idx_falta]
            idx_falta += 1

    idx_falta = 0
    for i in range(26):
        if chave_p2c[i] == '?':
            chave_p2c[i] = faltando_cifrado[idx_falta]
            idx_falta += 1

    return ''.join(chave_c2p), ''.join(chave_p2c)

def decifrar_com_chave(texto_cifrado, chave_c2p):
    ALFABETO = string.ascii_lowercase
    mapa = {ALFABETO[i]: chave_c2p[i] for i in range(26)}

    resultado = ''
    for c in texto_cifrado:
        resultado += mapa.get(c, c)
    return resultado

# === Entrada ===
cifrado = "iqnjivhaqjhgwbacivpjmwqarrjabaqhuhafawghfoamhfoihvwyavagiyakavjqarajuariwnjhqwfwivalavwauiqmhrrwfaiywlarjaqaighfoadwugam"
claro   = "emqueriamuitofazerjudomassuafamilianaotinhadinheiroparatepagarumasaulaseoquimonoeracaroalemdissonaepocasuamaetinhavoltad"

# === Execução ===
chave_c2p, chave_p2c = gerar_chaves_de_substituicao(cifrado, claro)
decifrado = decifrar_com_chave(cifrado, chave_c2p)

# === Saída ===
print("Chave (cifrado → claro):", chave_c2p)
print("Chave (claro → cifrado):", chave_p2c)
print("Texto decifrado:", decifrado)
