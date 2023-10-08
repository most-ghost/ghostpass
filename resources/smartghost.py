import os
from PyQt5 import QtCore as qtc
import hashlib as hlib
import binascii as basc
import base64 as b64
import string as string_consts
import pandas as pd
import argon2 as a2


class cls_obj_logic(qtc.QObject):
    """
    This holds the actual password generation logic. Well really all of that is
    actually handled by hashlib, I just piggyback off that and scramble it up a bit.
    """

    obj_hasher = a2.PasswordHasher(hash_len = 1028)

    
    def __init__(self):
        super().__init__()

        temp_csv_path =  os.path.join(os.path.dirname(__file__), "grimoire.csv")
        
        self.table_dictionary = pd.read_csv(temp_csv_path)
        del temp_csv_path


    def func_hash_gen(self, var_domain, var_password, var_size, var_salt):

        var_pseudo_salt = self.func_pseudo_salt(var_password, var_salt, var_size)
        hashed_pass = self.obj_hasher.hash(var_password + var_domain + str(var_size),
                                      salt=var_pseudo_salt)
        
        var_hexed = basc.hexlify(hashed_pass.encode('utf-8'))
        b85_pass = b64.b85encode(var_hexed).decode('utf-8')
        # This process will basically inject a whole lot of special characters into the password.

        return(b85_pass[:-var_size:-1])
        # We'll pull backwards from the end instead of the beginning because the beginning has information appended to it
        # (it looks like this- '$argon2id$v=19$m=65536,t=3,p=4$MTBk ....')
        # We don't want static information like that in our password. Because we've set our hasher to 1024 bits 
        # we're guarenteed to have lots of data to pull from at the end of the password.


    def func_pseudo_salt(self, var_ascii_password, var_potential_salt, var_size):
        obj_salt_gen = hlib.sha256()


        if var_potential_salt == '':
            var_salt = (var_ascii_password + str(var_size)).encode('utf-8')
            obj_salt_gen.update(var_salt)
            # Highly not recommended since this massively reduces the security of our salt, 
            # but people be lazy and weakened security is better than no security.

        else:
            var_salt = (var_potential_salt + str(var_size)).encode('utf-8')
            obj_salt_gen.update(var_salt)

        var_pseudo_salt = obj_salt_gen.digest()

        return var_pseudo_salt


    def func_passphrase_gen(self, var_domain, var_password, var_word_count, var_salt):

        var_inflate_count = var_word_count * 5

        list_phrase = []
        csv = self.table_dictionary
        const_alphabet = string_consts.ascii_lowercase

        var_hashed = self.func_hash_gen(var_domain, var_password, var_inflate_count, var_salt)
        var_hexed = basc.hexlify(var_hashed.encode('utf-8'))
        var_alphahexed = "".join([const_alphabet[i % 26] for i in var_hexed])
    
        for i in range(var_word_count):
            index = 3 * i
            new_word = csv[csv['Combo'] == var_alphahexed[index:index + 3]]['Word'].values[0]
            list_phrase.insert(0, new_word)
            list_phrase.insert(1, ' ') # Put a space between each word

        list_phrase.pop(-1) # Drop the last space
        var_passphrase = ''.join(list_phrase)

        return var_passphrase
            