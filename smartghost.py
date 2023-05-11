from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import hashlib as hlib
import binascii as basc
import base64 as b64
import string as string_consts
import cryptpandas as crp


import marshal
k = open('ghostpass/ghostkey.pyc', 'rb')
k.seek(16)
key = marshal.load(k)
exec(key)
crypt_key = crypt_gen()
# (Psst- this actually isn't secure at all, I'm just playing pretend and making it look
# like I'm doing something and giving a potential attacker something to do.)
# The purpose of this is to obscure the word dictionary that we pull from for pass phrases,
# but we use over 17500 words. With our minimum of six words that is twenty-eight septillion
# possible combinations. At the default of 10 words, it's well over 250 undecillion combos.
# So even if an attacker/hacker gets a good look at our dictionary, they're still going to
# have a hard time brute forcing anything.
# If this happens to break in the future, try bumping .seek by 4 (ie to either 20 or to 12).

class logic(qtc.QObject):
    def __init__(self):
        super().__init__()

        crypt_name = 'ghostpass/ghost.crypt'

        self.dictionary = crp.read_encrypted(path=crypt_name, 
            password=crypt_key)


    def hex_gen(self, domain, password, potential_salt):

        string = domain + password
        ascii_encoded = string.encode('ascii')
        salt = self.pseudo_salt(ascii_encoded, potential_salt)
        pbkdf2_gen = hlib.pbkdf2_hmac('sha3_512', ascii_encoded, salt, 122000)
        hexed = basc.hexlify(pbkdf2_gen)
        return(hexed)


    def hash_gen(self, domain, password, size, salt):

        hexed = self.hex_gen(domain, password, salt)
        hashed = b64.b85encode(hexed).decode("utf-8")
        scrambled1 = hashed[::-1][::2]
        scrambled2 = hashed[:96:2]
        

        double_hexed = self.hex_gen(domain, password + password, salt + salt)
        double_hashed = b64.b85encode(double_hexed).decode("utf-8")
        extra_scrambly = scrambled1 + double_hashed[::-1] + scrambled2
        # I added this step in later so it's a bit kludgy. I realized that I wanted to give
        # the option to use a 256 bit ultra-long password if the user wants it. Is this the proper way 
        # to do it? Maybe not, but it should still be 256 bits of random garbage so it 
        # should be nearly impossible to brute force. The only concern is whether it's possible to find
        # the master password using this pseudo 256-bit hash- I'm hoping that the password + salt 
        # system will be enough to prevent those sorts of shenanigans. 


        return(extra_scrambly[-size:])
        # The '[-size:] thing instead of [0:size] is purely image - if you increase the size of the 
        # password, it will get tacked onto the front instead of the back. Psychologically it seems 
        # like more password is being generated rather than revealing more of the existing password
        # (which is what's actually happening).


    def pseudo_salt(self, ascii_password, potential_salt):
        salt_gen = hlib.sha256()

        if potential_salt == '':
            salt_gen.update(ascii_password)
        else:
            salt = potential_salt.encode('ascii')
            salt_gen.update(salt)

        pseudo_salt = salt_gen.digest()

        return(pseudo_salt)


    def pass_phrase_gen(self, domain, password, num_of_words, salt):

        word_list = []
        csv = self.dictionary
        alphabet = string_consts.ascii_lowercase


        hexed = self.hex_gen(domain, password, salt)
        alphahexed = "".join([alphabet[i % 26] for i in hexed])
    

        for i in range(num_of_words):
            index = 3 * i
            new_word = csv[csv['Combo'] == alphahexed[index:index+3]]['Word'].values[0]
            word_list.append(new_word)

        pass_phrase = ''.join(word_list)

        return pass_phrase
            