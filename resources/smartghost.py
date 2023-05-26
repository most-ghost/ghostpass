import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import hashlib as hlib
import binascii as basc
import base64 as b64
import string as string_consts
import pandas as pd


class cls_obj_logic(qtc.QObject):
    def __init__(self):
        super().__init__()

        temp_csv_path =  os.path.join(os.path.dirname(__file__), "grimoire.csv")
        
        self.table_dictionary = pd.read_csv(temp_csv_path)

    def func_hex_gen(self, var_domain, var_password, var_potential_salt):

        var_combined = var_domain + var_password
        var_encoded = var_combined.encode('ascii')
        var_salt = self.func_pseudo_salt(var_encoded, var_potential_salt)
        var_pbkdf2 = hlib.pbkdf2_hmac('sha3_512', var_encoded, var_salt, 122000)
        var_hexed = basc.hexlify(var_pbkdf2)
        return var_hexed


    def func_hash_gen(self, var_domain, var_password, var_size, var_):

        var_hexed = self.func_hex_gen(var_domain, var_password, var_)
        var_hashed = b64.b85encode(var_hexed).decode("utf-8")
        scrambled1 = var_hashed[::-1][::2]
        scrambled2 = var_hashed[:96:2]
        

        double_hexed = self.func_hex_gen(var_domain, var_password + var_password, var_ + var_)
        double_hashed = b64.b85encode(double_hexed).decode("utf-8")
        extra_scrambly = scrambled1 + double_hashed[::-1] + scrambled2
        # I added this step in later so it's a bit kludgy, but it should be fine. It'll still spit out 
        # 256 bits worth of random.


        return(extra_scrambly[-var_size:])
        # [-var_size:] is just for appearances. It looks a little nicer to have new words pop in at the front,
        # instead of tacked onto the back.


    def func_pseudo_salt(self, var_ascii_password, var_potential_salt):
        obj_salt_gen = hlib.sha256()

        if var_potential_salt == '':
            obj_salt_gen.update(var_ascii_password)
        else:
            var_salt = var_potential_salt.encode('ascii')
            obj_salt_gen.update(var_salt)

        var_pseudo_salt = obj_salt_gen.digest()

        return var_pseudo_salt


    def func_passphrase_gen(self, var_domain, var_password, var_word_count, var_salt):

        list_phrase = []
        csv = self.table_dictionary
        const_alphabet = string_consts.ascii_lowercase

        var_hexed = self.func_hex_gen(var_domain, var_password, var_salt)
        var_alphahexed = "".join([const_alphabet[i % 26] for i in var_hexed])
    
        for i in range(var_word_count):
            index = 3 * i
            new_word = csv[csv['Combo'] == var_alphahexed[index:index + 3]]['Word'].values[0]
            list_phrase.insert(0, new_word)

        var_passphrase = ''.join(list_phrase)

        return var_passphrase
            