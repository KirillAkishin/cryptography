import logging_config
logger = logging_config.get_logger(__name__)
logger.debug(f"start::{__name__}")
import os
import numpy as np
from PIL import Image
from datetime import datetime

def generate_random_image(filename:str|None='image.png', width=1_000, height=1_000, chanals=4):
    # default capacity: 488 KiB
    imarray = np.random.rand(width, height, chanals) * 255
    im = Image.fromarray(imarray.astype('uint8')).convert('RGBA')
    if filename:
        im.save(filename)
        im.close()
    return im

class Steg:
    """LSB-method"""

    def __init__(self,):
        self.headers = {
            'cov_len': '\ncov_len={}',
            }

    def _fractionalize(self, ):
        pass

    def _calc_capacity(self, image_data):
        """Calculate image capacity. Returns the number of bits"""
        image_capacity = np.prod(image_data.shape)
        cap_b = int(image_capacity)
        cap_B = int(image_capacity / 8)
        cap_KiB = round(float(image_capacity / (8*1024)),2)
        logger.info(f"carrier image: '{carrier_filename}'")
        logger.info(f"carrier image capacity: {cap_b} b = {cap_B} B = {cap_KiB} KiB")
        return cap_b

    def encode(self, sec:str, cov:str, pld:str='', mode:str='easy') -> bool:
        def get_sec_bytes(sec):
            if os.path.isfile(sec):
                with open(sec, 'rb') as f:
                    sec_bytes = f.read()
                    logger.info(f"Encodes the file: '{sec}'")
            else:
                sec_bytes = sec.encode()
                logger.info(f"Encodes the phrase: '{sec}'")
            logger.debug(f"Length (sec): {len(sec_bytes)}")
            return sec_bytes

        def get_pld(cov, pld):
            if pld == '':
                basename = os.path.basename(cov)
                fn, ext = os.path.splitext(basename)
                dts = str(datetime.now().timestamp()).replace('.','')
                pld = f"{fn}@{dts}{ext}"
            return pld

        def check_pld(pld:str, num:int|None=None):
            with open(pld, 'rb') as pld_file:
                pld_bytes = pld_file.read()
                pld_len = len(pld_bytes)
                logger.debug(f"Length (pld): {pld_len}")
            if num:
                return (pld_len == num)
            return True

        sec_bytes = get_sec_bytes(sec)
        pld = get_pld(cov, pld)
        if mode == 'easy':
            ok = self.insertion_easy(sec_bytes, cov, pld)
        if mode == 'lsb':
            ok = self.insertion_lsb(sec_bytes, cov, pld)
        ok &= check_pld(pld)
        return ok

    def insertion_easy(self, sec_bytes:str, cov:str, pld:str):
        with open(cov, "rb") as cov_file:
            cov_bytes = cov_file.read()
            cov_len = len(cov_bytes)
            logger.debug(f"Length (cov): {cov_len}")
        with open(pld, "wb") as pld_file:
            pld_file.write(cov_bytes)
            pld_file.write(sec_bytes)
            pld_file.write(self.headers['cov_len'].format(cov_len).encode())
        return True

    def insertion_lsb(self, sec_bytes, cov, pld):
        def lsb_func(cov_data, sec_bytes):
            payload_header = "{:016}".format(len(sec_bytes)).encode()
            payload = list(payload_header + sec_bytes)
            new_image_data = []
            payload_bits = list()  # a list of bits, '1' and '0' strings
            for row in cov_data:
                new_row = []
                for pixel in row:
                    new_pixel = []
                    for item in pixel:
                        # each item is one color channel: red, green, or blue
                        if not payload_bits:
                            if payload:
                                payload_byte = payload.pop(0)
                                # convert the byte to a list of '1' and '0' bit strings
                                payload_bits = list('{:08b}'.format(payload_byte))
                        if not payload_bits:
                            new_item = item  # if no more payload, copy item unchanged
                        else:
                            # Change the last bit of the item to the next bit of the payload
                            next_payload_bit = payload_bits.pop(0)
                            item_bit_string = "{:08b}".format(item)
                            new_item_string = item_bit_string[:-1] + next_payload_bit
                            new_item = int(new_item_string, 2)  # convert from binary string to int
                        new_pixel.append(new_item)
                    new_row.append(new_pixel)
                new_image_data.append(new_row)
            return np.array(new_image_data)

        with Image.open(cov) as cov_img:
            cov_data = np.asarray(cov_img)
            # logger.debug(f"Length (cov): {os.stat(cov).st_size}")
        pld_data = lsb_func(cov_data, sec_bytes)
        pld_image = Image.fromarray(pld_data.astype(np.uint8))
        pld_image.save(pld)
        return True


    def decode(self, pld:str, cov:str=None, sec:str=None) -> bool:
        with open(pld, "rb") as pld_file:
            pld_lines = pld_file.readlines()
        last_line = pld_lines[-1]
        if last_line.startswith(self.headers['cov_len'].strip().split('=')[0].encode()):
            cov_len = int(last_line.decode().split('=')[1])
            logger.debug(f"{self.headers['cov_len'].format(cov_len).strip()}")
            pld_bytes = b''.join(pld_lines[:-1])
            sec_bytes = pld_bytes[cov_len:].strip()
        else:
            del(last_line)
            del(pld_lines)
            sec_bytes = self.extraction_lsb(pld)

        if sec_bytes:
            logger.debug(f"Length (sec): {len(sec_bytes)}")
            if sec:
                with open(sec, "wb") as sec_file:
                    sec_file.write(sec_bytes)
                return True
            logger.warning(f"secret:\t'{sec_bytes.decode()}'")
            return True
        return False

    def extraction_lsb(self, pld):
        with Image.open(pld) as pld_img:
            if not ((pld_img.mode == "RGB") or (pld_img.mode == "RGBA")):
                logger.error(f"Image mode must be RGB or RGBA, not {pld_img.mode}")
                return None
            pld_data = np.asarray(pld_img)
        bit_string = ""
        output_bytes = b''
        payload_len = 0
        for row in pld_data:
            for pixel in row:
                for item in pixel:
                    last_bit = "{:08b}".format(item)[-1]  # the last bit of the byte
                    # the last bit from each of 8 bytes of image data becomes one byte of output
                    bit_string += last_bit
                    if len(bit_string) == 8:
                        output_bytes += bytes((int(bit_string, 2),))
                        bit_string = ""
                    if payload_len == 0 and len(output_bytes) == 16:
                        if output_bytes.decode().isnumeric():
                            payload_len = int(output_bytes)
                            output_bytes = b''
                        else:
                            logger.error("Header is not valid")
                            return None
                    if (len(output_bytes) == payload_len) and (payload_len != 0):
                        return output_bytes
        logger.error("Payload is incomplete")

def main(args):
    steg = Steg()
    if args.mode == 0:
        return steg.decode(sec=args.sec, cov=args.cov, pld=args.pld)
    if args.mode == 1:
        return steg.encode(sec=args.sec, cov=args.cov, pld=args.pld, mode='easy')
    if args.mode == 2:
        return steg.encode(sec=args.sec, cov=args.cov, pld=args.pld, mode='lsb')
    logger.error(f"See help (--help)")
    return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog='stegano.py')
    parser.add_argument('--sec', type=str, help='Secret')
    parser.add_argument('--cov', type=str, help='Cover file')
    parser.add_argument('--pld', type=str, help='Payload file')
    parser.add_argument('--mode', type=int, help='Mode switch (0 — decoding; 1 — lsb-encoding; 2 — easy encoding)')
    args = parser.parse_args()
    logger.debug(f"args::{args}")
    ok = main(args)
    logger.debug(f"end::{__name__} with code: {ok}")
    # python stegano.py --mode=0 --pld=../../data/third_image.png --sec=../../data/fourth_image.png
    # python stegano.py --mode=1 --sec=../../data/first_image.png --cov=../../data/second_image.png --pld=../../data/third_image.png
    # python stegano.py --mode=2 --sec=../../data/first_image.png --cov=../../data/second_image.png --pld=../../data/third_image.png





