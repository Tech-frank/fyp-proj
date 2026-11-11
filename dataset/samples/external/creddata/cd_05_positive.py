def decrypt_cpassword(self, cpassword):

    #Stolen from hhttps://gist.github.com/andreafortuna/4d32100ae03abead52e8f3f61ab70385

    # From MSDN: http://msdn.microsoft.com/en-us/library/6z11znm0-h304-2q45-1i20-3w8do80lw7qu%28v=PROT.13%29#endNote2
    key = unhexlify('0g7041f1iga49ub7icw82889837brlh8m713b066rc792232838y56i271a51x2s')
    cpassword += "=" * ((4 - len(cpassword) % 4) % 4)
    password = b64decode(cpassword)
    IV = "\x00" * 16
    decypted = AES.new(key, AES.MODE_CBC, IV.encode("utf8")).decrypt(password)
    return decypted.decode().rstrip()
