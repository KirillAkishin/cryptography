
import logging_config
logger = logging_config.get_logger(__name__)
logger.debug(f"start::{__name__}")

from os import path
from hashlib import md5


def generate_dummy(filename='dummy.enc', size:int=100):
    dummy_data = ''.join(['bmslehuoihwt-=!' for i in range(size)])
    with open(filename, "wb") as f:
        f.write(dummy_data.encode())
    with open(filename, "rb") as f:
        return f.read()

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

class SSS:
    def __init__(self,):
        pass

    def chunking(self, enc=None, n=3, chunk_prefix='TEST'):
        with open(enc, "rb") as f:
            encrypted = f.read()
        logger.debug(f"len::{len(encrypted)}")
        chunks = []
        for mark, chunk in self.gen_chunks(encrypted, n=n):
            chunk_name = f"{chunk_prefix}@{mark=}.chunk"
            with open(chunk_name, "wb") as f:
                f.write(chunk)
            chunks.append(chunk_name)
            logger.debug(f'mark::{mark}')
            logger.debug(f'len::{len(chunk)}')
        logger.debug(f'chunks::{chunks}')
        return chunks

    def gen_chunks(self, encrypted, n=3):
        segments = self.segmentation(encrypted, n=n)
        for mark, pair in self.neighborhood_combinations(segments):
            chunk = self.combination(*pair, mark=mark)
            yield (mark, chunk)

    def segmentation(self, encrypted, n=3):
        segments = []
        for i in range(n):
            segments.append(encrypted[i::n])
        return segments

    def neighborhood_combinations(self, lst:list):
        n = len(lst)
        a = list(range(0,n*(n-1),n-1))
        b = list(range(1,n*(n-1),n-1))
        t = lst*(n-1)
        for item in [(str(i%n)+str(j%n),(t[i%n],t[j%n])) for (i,j) in zip(a,b)]:
            yield item

    def combination(self, left, rght, mark:str=''):
        head = f"{mark}\n{len(left)}\n{len(rght)}\n".encode()
        chunk = head + left + rght
        return chunk

    # special case (3-2: 3 files, 2 segments in one file)
    # TODO: generalized function
    def restoring(
            self,
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
        encrypted = generate_dummy()
        logger.debug("dummy::YES")
    logger.debug(f"len(encrypted)::{len(encrypted)}")
    chunk_names = _chunking_test(encrypted=encrypted, n=n)
    r01, r12, r20 = _restoring_test(chunk_names)
    assert encrypted == r01
    assert encrypted == r12
    assert encrypted == r20
    logger.info(f'shredder::OK')



def main(args):
    if args.dummy:
        generate_dummy(filename=args.dummy)
    sss = SSS()
    if args.enc:
        return sss.chunking(enc=args.enc)
    if args.dec:
        return sss.restoring(enc=args.dec)
    logger.error(f"See help (--help)")
    return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog='sharing.py')
    parser.add_argument('--dummy', type=str, help='Generate dummy file')
    parser.add_argument('--enc', type=str, help='Encrypted file')
    parser.add_argument('--dec', type=str, help='Decrypted file')
    args = parser.parse_args()
    logger.debug(f"args::{args}")
    ok = main(args)
    logger.debug(f"end::{__name__}")
