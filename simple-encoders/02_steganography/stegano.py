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

class Stegano:
    """LSB-method"""

    def __init__(self):
        pass

    def fractionalize(self, ):
        pass

    def calc_capacity(self, image_data):
        """Calculate image capacity. Returns the number of bits"""
        image_capacity = np.prod(image_data.shape)
        cap_b = int(image_capacity)
        cap_B = int(image_capacity / 8)
        cap_KiB = round(float(image_capacity / (8*1024)),2)
        logger.info(f"carrier image: '{carrier_filename}'")
        logger.info(f"carrier image capacity: {cap_b} b = {cap_B} B = {cap_KiB} KiB")
        return cap_b

    def insertion(self, image_data, payload_bytes):
        if args.lsb is not True:
            return self.insertion_lsb(image_data, payload_bytes)
        return self.insertion_easy(image_data, payload_bytes)

    def insertion_easy(self, image_data, payload_bytes):
        with open("out.jpg", "wb") as out:
            with open("a.jpg", "rb") as in_a:
                cover_image = in_a.read()
                ln_cover = len(cover_image)
                print(ln_cover)
                with open("b.pdf", "rb") as in_b:
                    hidden_data = in_b.read()
                    out.write(cover_image)
                    out.write(hidden_data)

    def insertion_lsb(self, image_data, payload_bytes):
        payload_header = "{:016}".format(len(payload_bytes)).encode()
        payload = list(payload_header + payload_bytes)
        new_image_data = []
        payload_bits = list()  # a list of bits, '1' and '0' strings
        for row in image_data:
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

    def extraction(self, image_data):
        if args.lsb is not True:
            return self.extraction_lsb(image_data)
        return self.extraction_easy(image_data)

    def extraction_easy(self, image_data):
        with open("out.jpg", "rb") as out:
            out_file = out.read()
            with open("b2.pdf", "wb") as b2:
                b2.write(out_file[ln_cover:])

    def extraction_lsb(self, image_data):
        bit_string = ""
        output_bytes = b''
        payload_len = 0
        for row in image_data:
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

    def encode(self, secret_obj:str, cover_image:str|None, output_image:str|None=None) -> bool:
        if cover_image:
            img = Image.open(cover_image)
        else:
            img = generate_random_image(filename=None)
        image_data = np.asarray(img)
        img.close()
        if os.path.isfile(secret_obj):
            with open(secret_obj, 'rb') as f:
                payload_bytes = f.read()
            logger.info(f"Encodes the file: '{secret_obj}'")
        else:
            payload_bytes = secret_obj.encode()
            logger.info(f"Encodes the phrase: '{secret_obj}'")
        new_image_data = self.insertion(image_data, payload_bytes)
        new_image = Image.fromarray(new_image_data.astype(np.uint8))
        output_image = output_image if output_image else f"{datetime.now().timestamp()}.png"
        new_image.save(output_image)
        return True

    def decode(self, encoded_image:str, secret_obj:str|None=None) -> bool:
        with Image.open(encoded_image) as img:
            if not ((img.mode == "RGB") or (img.mode == "RGBA")):
                logger.error(f"Image mode must be RGB or RGBA, not {img.mode}")
                return None
            image_data = np.asarray(img)
        output_bytes = self.extraction(image_data)
        if output_bytes is None:
            return False
        logger.info(f'len:\t{len(output_bytes)}')
        if secret_obj:
            with open(secret_obj, 'wb') as f:
                f.write(output_bytes)
        else:
            logger.warning(f"secret:\t'{output_bytes.decode()}'")
        return True


def main(args):
    steg = Stegano()
    if args.e:
        assert (args.d is False)
        return steg.encode(args.target, args.img, args.res)
    if args.d:
        assert (args.e is False) and (args.img is None)
        return steg.decode(args.target, args.res)
    logger.error(f"See help (--help)")
    return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog='stegano.py')
    parser.add_argument('target', type=str, help="Either secret or image with payload")
    parser.add_argument('--img', type=str, help='Cover image')
    parser.add_argument('--res', type=str, help='Resulting file')
    parser.add_argument('--lsb', action='store_true', default=False, help='turn on lsb mode')
    parser.add_argument('-e', action='store_true', default=False, help='turn on encrypting mode')
    parser.add_argument('-d', action='store_true', default=False, help='turn on decrypting mode')
    args = parser.parse_args()
    logger.debug(f"args::{args}")
    ok = main(args)
    logger.debug(f"end::{__name__}")


