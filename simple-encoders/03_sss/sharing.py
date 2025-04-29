
import logging_config
logger = logging_config.get_logger(__name__)
logger.debug(f"start::{__name__}")

import os
from hashlib import md5


def generate_dummy(filename='dummy.enc', size:int=100):
    dummy_data = ''.join(['bmslehuoihwt-=!' for i in range(size)])
    with open(filename, "wb") as f:
        f.write(dummy_data.encode())
    with open(filename, "rb") as f:
        return f.read()

class SSS:
    def __init__(self,):
        pass

    def chunking(self, enc=None, n=3, chunk_prefix='TEST', to='sharing-folder/'):
        with open(enc, "rb") as f:
            encrypted = f.read()
        logger.debug(f"len::{len(encrypted)}")
        folder_out = os.path.abspath(os.path.join(os.getcwd(), to))
        if not os.path.exists(folder_out):
            os.makedirs(folder_out)
        chunks = []
        for mark, chunk in self.gen_chunks(encrypted, n=n):
            chunk_name = os.path.join(folder_out, f"{chunk_prefix}@{mark=}.chunk")
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

    def merge_chunks(self, chunks):
        def proc_one_file(chunk):
            with open(chunk, "rb") as f:
                marks = f.readline().decode().strip()
                ln_list = []
                for _ in marks:
                    ln_list.append(int(f.readline().decode().strip()))
                combined_chunks = f.read()
            sgms = {}
            for m, ln in zip(marks, ln_list):
                sgms[m] = combined_chunks[:ln]
                combined_chunks = combined_chunks[ln:]
            return sgms

        def merging(sgms):
            res = bytearray([x for xs in list(zip(*sgms.values())) for x in xs])
            max_len = max(map(lambda x: len(x), sgms.values()))
            min_len = min(map(lambda x: len(x), sgms.values()))
            if max_len != min_len:
                res += bytearray([sgms[i][-1] for i in range(len(sgms)) if len(sgms[str(i)]) == max_len])
            return res

        sgms = {}
        for chunk in chunks:
            sgms.update(proc_one_file(chunk))
        merged_file = merging(sgms)
        return merged_file

    def restoring(self, dec, to='restored-file'):
        chunks = [os.path.abspath(os.path.join(os.getcwd(), dec, i)) for i in os.listdir(dec) if i.endswith('.chunk')]
        merged_file = self.merge_chunks(chunks)
        with open(to, 'wb') as f:
            f.write(merged_file)

def main(args):
    if args.dummy:
        generate_dummy(filename=args.dummy)
    sss = SSS()
    if args.enc:
        return sss.chunking(enc=args.enc, to=args.to)
    if args.dec:
        return sss.restoring(dec=args.dec, to=args.to)
    logger.error(f"See help (--help)")
    return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog='sharing.py')
    parser.add_argument('--dummy', type=str, help='Generate dummy file')
    parser.add_argument('--enc', type=str, help='Encrypted file')
    parser.add_argument('--dec', type=str, help='Decrypted file')
    parser.add_argument('--to', type=str, help='Output file path')
    args = parser.parse_args()
    logger.debug(f"args::{args}")
    ok = main(args)
    logger.debug(f"end::{__name__}")
