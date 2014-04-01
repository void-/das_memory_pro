import sys
p = "plaintext"
k = "reallylongkey"
def main():
  sys.stdout.write(cipher(sys.argv[1],sys.argv[2]))

def cipher(txt,k):
  """k is a key, txt is the plaintext.
  This cipher is dependant upon the length of the plaintext.
  There is no such thing as a partial decryption with this 
  function. It helps if the key is of prime length.

  plaintext
                 sxor()
  reallylon|gkey
  gkeyreall|ylongkey
  ylongkeyr|eallylongkey
  eallylong|key
  keyreally|longkey
  longkeyre|allylongkey
  allylongk|ey
  eyreallyl|ongkey
  ongkeyrea|llylongkey
  llylongke|y
  yreallylo|ngkey
  ngkeyreal|lylongkey
  lylongkey|
  
  >>> p = "plaintext"
  >>> k = "reallylongkey"
  >>> cipher(p,k) == (cipher(p[:-1],k) + cipher(p[-1],k))
  False
  """

  k = k * len(txt)#keykeykey
  for i in xrange(1,len(txt)):
    txt = sxor(txt,k[i-1:len(txt)*i])
  return txt

def sxor(plaintext,key):
  """cipher that is not input length dependant. It has a
  distributive property on substrings.

  >>> p = "plaintext"
  >>> k = "reallylongkey"
  >>> sxor(p,k) == (sxor(p[:-1],k) + sxor(p[-1],k))
  False
  >>> sxor(p[:-1],k) == sxor(p,k)[:-1]
  True
  
  """
  i,n = 0,0
  z = len(key)
  result = ''
  while i < len(plaintext):
    if n >=z:
      n = 0
    result+=chr(ord(plaintext[i])^ord(key[n]))
    i,n = i+1,n+1
  return result

def rcipher(txt,key):
  origkey = key
  def reccipher(txt,key):
    #print txt
    #print key
    x = len(txt)
    if x == len(key):
      return sxor(txt,key)
    futurekey = key[x:]
    if len(futurekey) != x:
      futurekey = futurekey+origkey
    return reccipher(sxor(txt,key[:x]),futurekey)
  return reccipher(txt,key)

#if __name__ == '__main__':
#  main()
