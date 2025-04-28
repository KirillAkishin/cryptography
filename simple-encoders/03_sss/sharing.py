 
import logging_config 
logger = logging_config.get_logger(__name__)
logger.debug(f"start::{__name__}")

from os import path
from hashlib import md5


class MD5:
    def __init__(self, data):
        self.data = data
        if data != None:
            self.data = str(data)
            self.hash = md5(self.data.encode()).hexdigest()
        else:
            self.data = ''
            self.hash = ''
    def __str__(self) -> str:
        return f"{self.data}({self.hash})"
    def __repr__(self) -> str:
        return self.hash 
    def __call__(self):
        return self.data
    def __add__(self, val2): 
        if val2.data == None:
            return self
        return MD5(self.data + val2.data) 
    def encode(self):
        return self.hash.encode()

def segmentation(encrypted, n=3):
    segments = []
    for i in range(n):
        segments.append(encrypted[i::n])
    return segments 

def neighborhood_combinations(lst:list):
    n = len(lst)
    a = list(range(0,n*(n-1),n-1))
    b = list(range(1,n*(n-1),n-1))
    t = lst*(n-1)
    for item in [(str(i%n)+str(j%n),(t[i%n],t[j%n])) for (i,j) in zip(a,b)]:
        yield item

def combination(
        left, 
        rght, 
        mark:str=None, 
        sep_mark:str='=mark@',
        sep_left:str='=rght@', 
        sep_rght:str='=left@'):
    len_l = str(len(left)).encode()
    sep_l = MD5(sep_left).encode()
    len_r = str(len(rght)).encode()
    sep_r = MD5(sep_rght).encode()
    sep_m = MD5(sep_mark).encode()
    marker = mark.encode() + sep_m if mark else b''
    head = len_l + sep_l + len_r + sep_r 
    chunk = marker + head + left + rght
    return chunk

def chunking(
        encrypted, 
        n=3,
        sep_mark:str='=mark@',
        sep_left:str='=rght@',
        sep_rght:str='=left@'):
    segments = segmentation(encrypted, n=n)
    for mark, pair in neighborhood_combinations(segments):
        chunk = combination(
            *pair,
            mark=mark, 
            sep_mark=sep_mark,
            sep_left=sep_left, 
            sep_rght=sep_rght)
        yield (mark, chunk)


### TO-DO
def restoring(
        chunk_left,
        chunk_rght,
        sep_mark:str='=mark@',
        sep_left:str='=rght@', 
        sep_rght:str='=left@'):
    b_sep_mark=MD5(sep_mark).encode()
    b_sep_left=MD5(sep_left).encode()
    b_sep_rght=MD5(sep_rght).encode()
    
    # first
    mark, ch1 = chunk_left.split(b_sep_mark)
    left_len, ch2 = ch1.split(b_sep_left)
    rght_len, ch3 = ch2.split(b_sep_rght)

    left_len = int(left_len.decode())
    rght_len = int(rght_len.decode())

    left_mark = int(chr(mark[0])) 
    rght_mark = int(chr(mark[1]))

    logger.debug(f"{left_mark=}\t@{left_len=}")
    logger.debug(f"{rght_mark=}\t@{rght_len=}")

    sgms = {}

    sgms[left_mark] = ch3[:left_len]
    sgms[rght_mark] = ch3[left_len:]
    assert len(sgms[rght_mark]) == rght_len

    # second
    mark, ch1 = chunk_rght.split(b_sep_mark)
    left_len, ch2 = ch1.split(b_sep_left)
    rght_len, ch3 = ch2.split(b_sep_rght)

    left_len = int(left_len.decode())
    rght_len = int(rght_len.decode())

    left_mark = int(chr(mark[0])) 
    rght_mark = int(chr(mark[1]))

    logger.debug(f"{left_mark=}\t@{left_len=}")
    logger.debug(f"{rght_mark=}\t@{rght_len=}")

    sgms[left_mark] = ch3[:left_len]
    sgms[rght_mark] = ch3[left_len:]
    assert len(sgms[rght_mark]) == rght_len

    def integration(sgms, n=3):
        res = bytearray([x for xs in list(zip(sgms[0],sgms[1],sgms[2])) for x in xs])
        max_len = max(len(sgms[0]),len(sgms[1]),len(sgms[2]))
        min_len = min(len(sgms[0]),len(sgms[1]),len(sgms[2]))
        if max_len != min_len:
            res += bytearray([sgms[i][-1] for i in range(n) if len(sgms[i]) == max_len])
        return res 

    res = integration(sgms)
    return res

def get_dummy(filename='dummy.enc'):
    dummy_data = "bluh"*100 + "meow"*100 + "shit"*100
    with open(filename, "wb") as f:
        f.write(dummy_data.encode())
    with open(filename, "rb") as f:
        return f.read()

###### TESTS
def _chunking_test(
        encrypted=None, 
        n=3, 
        chunk_prefix='TEST',
        sep_mark='=mark@',
        sep_left='=rght@',
        sep_rght='=left@'):
    # secret = "storage/03_ontologies.enc" 
    encrypted = encrypted or get_dummy()
    logger.debug(f"len::{len(encrypted)}")
    chunks = []
    for mark, chunk in chunking(encrypted, 
                                n=n,
                                sep_mark=sep_mark,
                                sep_left=sep_left,
                                sep_rght=sep_rght):
        chunk_name = f"{chunk_prefix}@{mark=}.chunk" 
        with open(chunk_name, "wb") as f:
            f.write(chunk)
        chunks.append(chunk_name)
        logger.debug(f'mark::{mark}')
        logger.debug(f'len::{len(chunk)}')
    logger.debug(f'chunks::{chunks}')
    return chunks

def _restoring_test(chunk_names, full=True):
    with open(chunk_names[0], "rb") as f:
        ch0 = f.read()
    with open(chunk_names[1], "rb") as f:
        ch1 = f.read()
    with open(chunk_names[2], "rb") as f:
        ch2 = f.read()
    r01 = restoring(chunk_left=ch0, chunk_rght=ch1)
    r12 = restoring(chunk_left=ch1, chunk_rght=ch2)
    r20 = restoring(chunk_left=ch2, chunk_rght=ch0)
    assert r01 == r12 == r20 
    return r01, r12, r20

def _unit_testing(secret=None, n=3):
    if secret:
        with open(secret, "rb") as f:
            encrypted = f.read()
    else:
        encrypted = get_dummy()
        logger.debug("dummy::YES")
    logger.debug(f"len(encrypted)::{len(encrypted)}")
    chunk_names = _chunking_test(encrypted=encrypted, n=n)
    r01, r12, r20 = _restoring_test(chunk_names)
    assert encrypted == r01
    assert encrypted == r12 
    assert encrypted == r20
    logger.info(f'shredder::OK')