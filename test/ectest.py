import pyelliptic
 
# Symmetric encryption
iv = pyelliptic.Cipher.gen_IV('aes-256-cfb')
ctx = pyelliptic.Cipher("secretkey", iv, 1, ciphername='aes-256-cfb')
 
ciphertext = ctx.update('test1')
ciphertext += ctx.update('test2')
ciphertext += ctx.final()
 
ctx2 = pyelliptic.Cipher("secretkey", iv, 0, ciphername='aes-256-cfb')
print ctx2.ciphering(ciphertext)
 
# Asymmetric encryption
alice = pyelliptic.ECC(curve='secp256k1')
bob = pyelliptic.ECC(curve='secp256k1')

ciphertext = alice.encrypt("Hello bbBob", bob.get_pubkey())
print bob.decrypt(ciphertext)
 
signature = bob.sign("Hello Alice")
# alice's job :
print pyelliptic.ECC(pubkey=bob.get_pubkey()).verify(signature, "Hello Alice")
 
# ERROR !!!
try:
    key = alice.get_ecdh_key(bob.get_pubkey())
except: print("For ECDH key agreement, the keys must be defined on the same curve !")
 
alice = pyelliptic.ECC(curve='secp256k1')
print alice.get_ecdh_key(bob.get_pubkey()).encode('hex')
print bob.get_ecdh_key(alice.get_pubkey()).encode('hex')

print bob.get_pubkey().encode('hex')
