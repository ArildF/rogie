#password.py
#created 30.04.2002

#authStrings is the function you need.
#Hacked up protosurge@yahoo.com
#I'm not responsible in how you use this code

#code ripped from http://www.chrisarndt.de/software/authlib.py.html
#authored by Chris Arndt

import md5
import string
import string, sys, time, whrandom

DES_SALT = list('./0123456789' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 'abcdefghijklmnopqrstuvwxyz')
Y64_SALT = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._")

def _to64(v, n):
    r = ''
    while (n-1 >= 0):
        r = r + DES_SALT[v & 0x3F]
        v = v >> 6
        n = n - 1
    return r

#This is almost line-by-lien from the gaim/yahoo lib
def _toy64(val,inlen):
    ret = ''
    ptr = 0
    while inlen >= 3:
		ret = ret + Y64_SALT[ord(val[ptr+0]) >> 2];
		ret = ret + Y64_SALT[((ord(val[ptr+0]) << 4) & 0x30) | (ord(val[ptr+1]) >> 4)]
		ret = ret + Y64_SALT[((ord(val[ptr+1]) << 2) & 0x3c) | (ord(val[ptr+2]) >> 6)]
		ret = ret + Y64_SALT[ord(val[ptr+2]) & 0x3f]
		inlen = inlen - 3
		ptr = ptr + 3

    if inlen > 0:
        ret = ret + Y64_SALT[ord(val[ptr+0]) >> 2]
        fragment = (ord(val[ptr+0]) << 4) & 0x30
        if inlen > 1:
            fragment |= ord(val[ptr+1]) >> 4
        ret = ret + Y64_SALT[fragment]
        if inlen < 2:
            ret = ret + '-'
        else:
            ret = ret + Y64_SALT[(ord(val[ptr+1]) << 2) & 0x3c]
        ret = ret + '-'

    return ret

def md5hash(passwrd, salt=None, magic='$1$'):
    """Encrypt passwd with MD5 algorithm."""
    
    if not salt:
	salt = repr(int(time.time()))[-8:]
    elif salt[:len(magic)] == magic:
        # remove magic from salt if present
        salt = salt[len(magic):]

    # salt only goes up to first '$'
    salt = string.split(salt, '$')[0]
    # limit length of salt to 8
    salt = salt[:8]

    ctx = md5.new(passwrd)
    ctx.update(magic)
    ctx.update(salt)
    
    ctx1 = md5.new(passwrd)
    ctx1.update(salt)
    ctx1.update(passwrd)
    
    final = ctx1.digest()
    
    for i in range(len(passwrd), 0 , -16):
	if i > 16:
	    ctx.update(final)
	else:
	    ctx.update(final[:i])
    
    i = len(passwrd)
    while i:
	if i & 1:
	    ctx.update('\0')
	else:
	    ctx.update(passwrd[:1])
	i = i >> 1
    final = ctx.digest()
    
    for i in range(1000):
	ctx1 = md5.new()
	if i & 1:
	    ctx1.update(passwrd)
	else:
	    ctx1.update(final)
	if i % 3: ctx1.update(salt)
	if i % 7: ctx1.update(passwrd)
	if i & 1:
	    ctx1.update(final)
	else:
	    ctx1.update(passwrd)
        final = ctx1.digest()
    
    rv = magic + salt + '$'
    final = map(ord, final)
    l = (final[0] << 16) + (final[6] << 8) + final[12]
    rv = rv + _to64(l, 4)
    l = (final[1] << 16) + (final[7] << 8) + final[13]
    rv = rv + _to64(l, 4)
    l = (final[2] << 16) + (final[8] << 8) + final[14]
    rv = rv + _to64(l, 4)
    l = (final[3] << 16) + (final[9] << 8) + final[15]
    rv = rv + _to64(l, 4)
    l = (final[4] << 16) + (final[10] << 8) + final[5]
    rv = rv + _to64(l, 4)
    l = final[11]
    rv = rv + _to64(l, 2)
    
    return rv

def md5only(str):
	ctx1 = md5.new(str)
	return ctx1.digest()

def authStrings(challenge, username,passwd):    
    #This is from
    #http://pub66.ezboard.com/fcoreprogrammingfrm5.showMessageRange?topicID=5.topic&start=21&stop=40
    phase1 = _toy64(md5only(passwd), 16)
    tempstring = md5hash(passwd, "$1$_2S43d5f$")
    phase3 = _toy64(md5only(tempstring), 16)

    singlechar = ord(challenge[15]);
    singlechar = singlechar & 7
    singlechar = singlechar % 5

    if singlechar == 0:
        singlechar = ord(challenge[7])
        singlechar = singlechar & 0x0F
        singlechar = ord(challenge[singlechar])
        p2instring = chr(singlechar) + phase1 + username + challenge
        p4instring = chr(singlechar) + phase3 + username + challenge
    elif singlechar == 1:
        singlechar = ord(challenge[9])
        singlechar = singlechar & 0x0F
        singlechar = ord(challenge[singlechar])
        p2instring = chr(singlechar) + username + challenge + phase1
        p4instring = chr(singlechar) + username + challenge + phase3
    elif singlechar == 2:
        singlechar = ord(challenge[0xF])
        singlechar = singlechar & 0x0F
        singlechar = ord(challenge[singlechar])
        p2instring = chr(singlechar) + challenge + phase1 + username
        p4instring = chr(singlechar) + challenge + phase3 + username
    elif singlechar == 3:
        singlechar = ord(challenge[1])
        singlechar = singlechar & 0x0F
        singlechar = ord (challenge[singlechar])
        p2instring = chr(singlechar) + username + phase1 + challenge
        p4instring = chr(singlechar) + username + phase3 + challenge
    elif singlechar == 4:
        singlechar = ord(challenge[0x3])
        singlechar = singlechar & 0x0F
        singlechar = ord(challenge[singlechar])
        p2instring = chr(singlechar) + phase1 + challenge + username
        p4instring = chr(singlechar) + phase3 + challenge + username

    phase2 = _toy64(md5only(p2instring), 16)
    phase4 = _toy64(md5only(p4instring), 16)

    return phase2,phase4

#code ripped from http://www.chrisarndt.de/software/authlib.py.html
#authored by Chris Arndt

#import md5
#import string
#import string, sys, time, whrandom


#def _to64(v, n):
#    r = ''
#    while (n-1 >= 0):
#        r = r + DES_SALT[v & 0x3F]
#        v = v >> 6
#        n = n - 1
#    return r

#DES_SALT = list('./0123456789' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 'abcdefghijklmnopqrstuvwxyz')

#def passcrypt_md5(passwrd, salt=None, magic='$1$'):
#    """Encrypt passwd with MD5 algorithm."""
#    
#    if not salt:
#	salt = repr(int(time.time()))[-8:]
#    elif salt[:len(magic)] == magic:
#        # remove magic from salt if present
#        salt = salt[len(magic):]

#    # salt only goes up to first '$'
#    salt = string.split(salt, '$')[0]
#    # limit length of salt to 8
#    salt = salt[:8]

#    ctx = md5.new(passwrd)
#    ctx.update(magic)
#    ctx.update(salt)
    
#    ctx1 = md5.new(passwrd)
#    ctx1.update(salt)
#    ctx1.update(passwrd)
    
#    final = ctx1.digest()
    
#    for i in range(len(passwrd), 0 , -16):
#	if i > 16:
#	    ctx.update(final)
#	else:
#	    ctx.update(final[:i])
    
#    i = len(passwrd)
#    while i:
#	if i & 1:
#	    ctx.update('\0')
#	else:
#	    ctx.update(passwrd[:1])
#	i = i >> 1
#    final = ctx.digest()
    
#    for i in range(1000):
#	ctx1 = md5.new()
#	if i & 1:
#	    ctx1.update(passwrd)
#	else:
#	    ctx1.update(final)
#	if i % 3: ctx1.update(salt)
#	if i % 7: ctx1.update(passwrd)
#	if i & 1:
#	    ctx1.update(final)
#	else:
#	    ctx1.update(passwrd)
#        final = ctx1.digest()
    
#    rv = magic + salt + '$'
#    final = map(ord, final)
#    l = (final[0] << 16) + (final[6] << 8) + final[12]
#    rv = rv + _to64(l, 4)
#    l = (final[1] << 16) + (final[7] << 8) + final[13]
#    rv = rv + _to64(l, 4)
#    l = (final[2] << 16) + (final[8] << 8) + final[14]
#    rv = rv + _to64(l, 4)
#    l = (final[3] << 16) + (final[9] << 8) + final[15]
#    rv = rv + _to64(l, 4)
#    l = (final[4] << 16) + (final[10] << 8) + final[5]
#    rv = rv + _to64(l, 4)
#    l = final[11]
#    rv = rv + _to64(l, 2)
    
#    return rv


