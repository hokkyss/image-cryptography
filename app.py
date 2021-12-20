import random
from datetime import datetime
from typing import Tuple
from PIL import Image
import numpy as np
from sympy import randprime, isprime
from utils import ELLIPTIC_CURVE, ECRSA, EllipticCurve


SIGN_MARK = bytes("SSSSSIIIIIGGGGGNNNNN*****", "utf-8")


def generate_default_image():
    arr = np.ndarray((256, 256, 3), dtype=np.uint8)
    for i in range(256):
        for j in range(256):
            arr[i, j] = np.array([i, 255, j], dtype=np.uint8)
    image = Image.fromarray(arr, "RGBA")
    image.save("ALL.png")
    image.save("in/ALL.png")


def generate_key(ECC: EllipticCurve) -> Tuple[int, int]:
    e = randprime(0, len(ECC.points))
    d = pow(e, -1, len(ECC.points))

    return (e, d)


def encrypt_image(name: str, key: Tuple[int, int], channel: str = "RGBA"):
    image = Image.open(f"in/{name}").convert(channel)
    image_array = np.asarray(image, dtype=np.uint8)
    (width, height) = image.size
    image.close()
    dimension = len(channel)

    e, d = key

    encrypted = image_array.copy()
    for i in range(height):
        for j in range(width):
            # do not encrypt A
            for k in range(dimension - 1):
                encryption_result = ECRSA.encrypt((e, d), int(encrypted[i, j, k]))
                encrypted[i, j, k] = np.uint8(encryption_result)

    output_image = Image.fromarray(encrypted, mode=channel)
    output_image.save(f"out/{name}")
    return output_image.close()


def decrypt_image(name: str, key: Tuple[int, int], channel: str = "RGBA"):
    image = Image.open(f"out/verified-{name}")
    image_array = np.asarray(image, dtype=np.uint8)
    (width, height) = image.size
    image.close()

    dimension = len(channel)
    e, d = key

    decrypted = image_array.copy()
    for i in range(height):
        for j in range(width):
            # do not decrypt A
            for k in range(dimension - 1):
                decryption_result = ECRSA.decrypt((e, d), int(decrypted[i, j, k]))
                decrypted[i, j, k] = np.uint8(decryption_result)
    output_image = Image.fromarray(decrypted, mode=channel)
    output_image.save(f"out2/{name}")
    return output_image.close()


def generate_signature_key() -> Tuple[Tuple[int, int, int], int]:
    """
    Generates public key and private key for undeniable digital signature
    """
    # q must be 7 bit length
    q = randprime(2 ** 6, 2 ** 7)
    # later on, all powers and multiplications must be in (mod p)
    # so we need p to be 8 bits long in size
    p = 2 * q + 1
    while not isprime(p):
        q = randprime(2 ** 6, 2 ** 7)
        p = 2 * q + 1
    alpha = random.randint(2, q - 1)
    a = random.randint(1, q - 1)
    return ((p, alpha, (alpha ** a) % p), a)


def pow_bytes(sign_bytes: bytearray, x: int, p: int) -> bytearray:
    size = len(sign_bytes)
    for i in range(size):
        sign_bytes[i] = pow(sign_bytes[i], x, p)
    return sign_bytes


def sign(name: str, public_key: Tuple[int, int, int], private_key: int) -> None:
    (p, _, _) = public_key

    file = open(f"out/{name}", "rb")
    content = file.read()
    file.close()

    if content.find(SIGN_MARK) != -1:
        print("File already signed")
        return False

    sign_bytes = bytearray(content)
    sign_bytes = pow_bytes(sign_bytes, private_key, p)

    signing = open(f"out/signed-{name}", "wb")
    signing.write(content)
    signing.write(SIGN_MARK)
    signing.write(sign_bytes)
    signing.close()
    return True


def verify(name: str, public_key: Tuple[int, int, int], private_key: int) -> None:
    (p, alpha, y) = public_key
    q = (p - 1) // 2
    a_inv = pow(a, -1, q)

    file = open(f"out/signed-{name}", "rb")
    content = file.read()
    file.close()

    sign_beginning = content.find(SIGN_MARK)
    if sign_beginning == -1:
        print("masuk sini?")
        return False

    signature = content[sign_beginning + len(SIGN_MARK) :]
    pure_content = content[:sign_beginning]

    """ VERIFIER GENERATES TWO SECRET RANDOM INTEGERS """
    gamma = random.randint(1, q - 1)
    delta = random.randint(1, q - 1)

    """ VERIFIER COMPUTES z AND SEND IT TO SIGNER """
    y_delta = pow(y, delta, p)
    z = bytearray(signature)
    len_z = len(z)
    for i in range(len_z):
        z[i] = (pow(z[i], gamma, p) * y_delta) % p
    """ SIGNER COMPUTES w AND SEND IT TO VERIFIER """
    w = bytearray(z)
    len_w = len(w)
    for i in range(len_w):
        w[i] = pow(w[i], a_inv, p)
    """ VERIFIER computes w' """
    alpha_delta = pow(alpha, delta, p)
    w_prime = pow_bytes(bytearray(pure_content), gamma, p)
    len_w_prime = len(w_prime)
    for i in range(len_w_prime):
        w_prime[i] = (w_prime[i] * alpha_delta) % p

    """ VALIDATE w == w' """
    print(w == w_prime)
    if w == w_prime:
        out = open(f"out/verified-{name}", "wb")
        out.write(pure_content)
        out.close()
        return True
    return False


if __name__ == "__main__":
    use_generated_key = input("Do you want to use default key? (Y/N) ") == "Y"
    if use_generated_key:
        (e, d) = generate_key(ELLIPTIC_CURVE)
        print(f"Your encryption/public key is {e}")
        print(f"decryption/private key is {d}")
        ((p, alpha, y), a) = generate_signature_key()
        print(
            f"Your signature public key is ({p}, {alpha}, {y}). Please don't change the numbers nor the sequence"
        )
        print(f"Your signature private key is {a}")
    else:
        e = int(input("Your public key: "))
        d = int(input("Your private key: "))
        p, alpha, y = list(
            map(
                int,
                input("Your signature public key in format <x> <y> <z>: ").split(" "),
            )
        )
        print(p, alpha, y)
        a = int(input("Your signature private key: "))

    while True:
        print("Put the file you want to encrypt in 'in/<name>'")
        print("Put the file you want to be signed in out/signed-<name>")
        print("Put the file you wanted to be verified in out/verified-<name>")
        filename = input("Filename of the image you want to apply cryptography into: ")
        is_png = filename.find(".png") != -1
        if not is_png:
            print("Only png extensions are allowed")
            continue

        print("Available commands:")
        print("1. Encrypt an image")
        print("2. Sign an image")
        print("3. Verify the signature on an image")
        print("4. Decrypt an image")
        prompt = int(input("Enter the number of command you want to do: "))

        if prompt == 1:
            print("Encrypting...")
            time_before_encrypting = datetime.now()
            encrypt_image(filename, key=(e, d))
            time_after_encrypting = datetime.now()
            print("Done encrypting")
            print(
                "Encryption duration:", time_after_encrypting - time_before_encrypting
            )
        elif prompt == 2:
            print("Signing...")
            time_before_signing = datetime.now()
            sign(filename, (p, alpha, y), a)
            time_after_signing = datetime.now()
            print("Sign duration:", time_after_signing - time_before_signing)
        elif prompt == 3:
            print("Verifying...")
            time_before_verifying = datetime.now()
            verified = verify(filename, (p, alpha, y), a)
            time_after_verifying = datetime.now()
            print(
                "Verification duration:", time_after_verifying - time_before_verifying
            )
            if verified:
                print("Signature verification successful.")
            else:
                print("Signature verification failed. Aborting...")
        elif prompt == 4:
            print("Decrypting...")
            time_before_decrypting = datetime.now()
            decrypt_image(filename, key=(e, d))
            time_after_decrypting = datetime.now()
            print("Done decrypting")
            print(
                "Decryption duration:", time_after_decrypting - time_before_decrypting
            )
