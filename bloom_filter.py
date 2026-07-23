import math
from bitarray import bitarray
import mmh3


"""
mmh3 aka murmurhash3: Noncrypographic hashing alg that allows hashing with a provided key rather then setting the key before running the program and more importantly allows multiple hash functions to exist in parallel. 
I couldve just uded hashlib but that would be slow and boring.

I debaited using this and the double hashing trick(make 2 hashes and calc all the subsequent with h1+i*h2 mod m) seems like magic because its statistically proven to have truly independent hashes with only 2 functions.
salted hashlib is trash because I dont want to call my hash bitflip times per find.
"""

"""
(p)robability of hashing to a array holding 1 val: 1-1/m with m being slots
so p((n)umber of assigned bits) = (1-1/m)^n
so including k (number of bits flipped per key), p(n*k)=(1-1/m)^(n*k)

can aproximate m at huge values with
lim x->inf (1-1/x)^x = 1/e
so the probability of not getting a collision is close to (1/e)^(n*k/m) or e^-(nk/m)
prob of getting colision is 1-e^-(nk/m)

derive to optimize
1/y dy/dx k = ln(1-e^(nk/m))+(kn/m)/((1-e^(-nk/m))*e^(kn/m))
0 = y(ln(1-e^(-nk/m))+(kn/m)/((1-e^(-nk/m))*e^(kn/m)))
aprox optimal = e^(-nk/m)=1/2

p = (1/2)^k
ln(p) = k*ln(1/2)
=-kln(2)
k = -ln(p)/ln2

ln(2) = nk/m
k = (m*ln(2))/n

m/n = -ln(p)

m = (kn)/ln(2)
= n/ln(2) * mln...idk im tired of math

main idea is that bloom is optimal when half full 
to find k from this we know (m*ln(2))/n from calculus and k = -ln(p)/ln2 from p=(1/2)^k[plugging in 1/2 in our original stat formula]
so -ln(p)/ln2=(m*ln(2))/n->mln(2)=-ln(p)n/ln2->m=-ln(p)n/(ln2)^2

"""

class bloom_filter:
    def __init__(self, precision:float, expected_size:int):
        if precision <=0 or precision >=1:
            raise ValueError("Invalid precision input")
        self.precision = precision
        self.expected_size = expected_size#n
        self.allocated_slots = self._calc_slots()#m
        self.bit_flips = round((self.allocated_slots/self.expected_size)*math.log(2))#k
        self.buffer = bitarray(self.allocated_slots)
        self.buffer.setall(0)

    def _calc_slots(self):
        return math.ceil(-(self.expected_size*math.log(self.precision))/(math.log(2)**2))#rounds up buffer size int(+1) adds 1 extra bit in some cases. not very harmful but wrong.
    
    def _positions(self, item):
        match item:
            case int():
                data = item.to_bytes(8,"big")#turns str into bytes or leaves it as it
            case str():
                data = item.encode()
            case _:
                raise TypeError("Key type has not yet been accounted for")
        h1, h2 = mmh3.hash64(data, signed=False)#make 2 hash's
        for i in range(self.bit_flips):#returning # of bitflips for this keys unique fingerprint
            yield(h1 + i * h2)%self.allocated_slots#double hashing formula, yielding because in contains if an idx is 0 we dont need to calc the rest of the idx's

    def add(self, item)->None:
        """
        item must be an encodable type
        """
        for i in self._positions(item):
            self.buffer[i]=1

    def contains(self, item)->bool:
        """
        item must be a encodable type
        """
        for i in self._positions(item):
            if self.buffer[i]==0:
                return False
        return True

if __name__ == "__main__":
    n = 10000
    r=.01
    bf = bloom_filter(r, n)
    print("allocated slots: ", bf.allocated_slots)
    print("bits flipped per hashing: ", bf.bit_flips)

    for i in range(n):
        bf.add(i)

    false_pos = [0,0]
    for i in range(n*10):
        if bf.contains(i):
            false_pos[1]=false_pos[1]+1
        else:
            false_pos[0]=false_pos[0]+1

    def false_neg_tst():
        for i in range(n):
            if not bf.contains(i):
                return False
        return True
    assert false_neg_tst()
        
    print("ratio of false pos: ", (false_pos[1]-n)/(n*9))
    print("expected ratio: ", r)