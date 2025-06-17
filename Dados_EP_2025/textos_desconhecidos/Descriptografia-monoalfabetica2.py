from string import ascii_lowercase
import string

def infer_monoalphabetic_key(plaintext, ciphertext):
    mapping = {}
    used_cipher_letters = set()

    for p, c in zip(plaintext, ciphertext):
        if p in mapping:
            if mapping[p] != c:
                raise ValueError(f"Conflict: {p} maps to both {mapping[p]} and {c}")
        else:
            if c in used_cipher_letters:
                raise ValueError(f"Cipher letter {c} already used!")
            mapping[p] = c
            used_cipher_letters.add(c)

    key = [''] * 26
    unused_letters = [c for c in ascii_lowercase if c not in mapping.values()]
    idx_unused = 0

    for i, letter in enumerate(ascii_lowercase):
        if letter in mapping:
            key[i] = mapping[letter]
        else:
            key[i] = unused_letters[idx_unused]
            idx_unused += 1

    return ''.join(key)

def decodificar(texto_cifrado, chave_str):
    # Inverter chave para decodificar
    tabela = str.maketrans(chave_str, string.ascii_lowercase)
    return texto_cifrado.translate(tabela)

# Exemplo:
plaintext = "uvirhamagianoritualdeescolherumdiscocolocarnavitrolaeouvirochiadocaracteristicoantesdamusicacomecarnessemundodeconvenien"
ciphertext = "dstnpwhwrtwzmntudwjiffblmjpfndhitblmlmjmlwnzwstunmjwfmdstnmlptwimlwnwlufntbutlmwzufbiwhdbtlwlmhflwnzfbbfhdzimiflmzsfztfz"

key = infer_monoalphabetic_key(plaintext, ciphertext)
print("Chave inferida:", key)

texto_decifrado = decodificar(ciphertext, key)
print("Texto decifrado:", texto_decifrado)
