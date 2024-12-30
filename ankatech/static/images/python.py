# # # # import zipfile
# # # # import os

# # # # # Başlangıç ZIP dosyasının yolu
# # # # zip_path = "C:\\Users\\Hayali\\Desktop\\Yeni klasör\\Çıktı\\99.zip"

# # # # output_dir = path = "C:\\Users\\Hayali\\Desktop\\Yeni klasör\\Çıktı"

# # # # # Çıkartma işlemini gerçekleştirecek fonksiyon
# # # # def extract_zip(zip_path, output_dir):
# # # #     with zipfile.ZipFile(zip_path, 'r') as zip_ref:
# # # #         zip_ref.extractall(output_dir)

# # # # # Dosya sayısını kontrol et ve sürekli olarak açmaya devam et
# # # # current_zip = zip_path
# # # # count = 0

# # # # # Çıkartma dizini oluşturulmadıysa oluştur
# # # # if not os.path.exists(output_dir):
# # # #     os.makedirs(output_dir)

# # # # while count < 120:
# # # #     # ZIP dosyasını çıkar
# # # #     extract_zip(current_zip, output_dir)

# # # #     # Yeni ZIP dosyasını bul
# # # #     files = os.listdir(output_dir)
# # # #     next_zip = None
# # # #     for file in files:
# # # #         if file.endswith('.zip'):
# # # #             next_zip = os.path.join(output_dir, file)
# # # #             break

# # # #     # Yeni ZIP dosyası varsa işlemi devam ettir
# # # #     if next_zip:
# # # #         current_zip = next_zip
# # # #         count += 1
# # # #     else:
# # # #         print("Sonraki ZIP dosyası bulunamadı.")
# # # #         break

# # # # print(f"Tüm ZIP dosyaları {count} kez çıkarıldı.")
# # # from itertools import cycle

# # # def vigenere_decrypt(text, key):
# # #     key = cycle(key)
# # #     result = ""
# # #     for char, k in zip(text, key):
# # #         if char.isalpha():
# # #             shift = ord(k.lower()) - ord('a')
# # #             if char.isupper():
# # #                 result += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
# # #             else:
# # #                 result += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
# # #         else:
# # #             result += char
# # #     return result

# # # cipher_text = "Kqz}jNylyvc@(jGZ)jG-(jme"
# # # key = "crypto"  # Anahtar kelimeyi buraya yerleştirin
# # # print(vigenere_decrypt(cipher_text, key))
# # import base64

# # def xor_decrypt(cipher_text, key):
# #     decrypted = ''.join([chr(ord(c) ^ key) for c in cipher_text])
# #     return decrypted

# # # Şifreli metin
# # cipher_text = "Kqz}jNylyvc@(jGZ)jG-(jme"

# # # Anahtar değeri (0-255 arası)
# # for key in range(256):  # Anahtar 0'dan 255'e kadar denenecek
# #     decrypted_text = xor_decrypt(cipher_text, key)
# #     print(f"Key {key}: {decrypted_text}")
# # ###########24 key flag
# import urllib.parse

# encoded_string = "asdmflfkrofl%2B%3D%3F34558%24asdad"
# decoded_string = urllib.parse.unquote(encoded_string)
# print(decoded_string)
def vigenere_decrypt(ciphertext, key):
    decrypted_text = []
    key_length = len(key)
    for i, char in enumerate(ciphertext):
        key_char = key[i % key_length]
        decrypted_char = chr(((ord(char) - ord(key_char)) % 256))
        decrypted_text.append(decrypted_char)
    return ''.join(decrypted_text)

ciphertext = "KqciiQamaa"
key = "sibervatan"
decrypted_message = vigenere_decrypt(ciphertext, key)
print(decrypted_message)
