import logging_config
logger = logging_config.get_logger(__name__)
logger.debug(f"start::{__name__}")
import os
import numpy as np
from PIL import Image

def encode(carrier_filename, output_filename, payload_bytes):
    with Image.open(carrier_filename) as source_image:
        image_data = np.asarray(source_image)  # the image as an array of rows of pixels
    payload_header = "{:016}".format(len(payload_bytes)).encode()
    payload = list(payload_header + payload_bytes)
    ##### LOG BLOCK
    image_capacity = np.prod(image_data.shape)
    cap_b = int(image_capacity)
    cap_B = int(image_capacity / 8)
    cap_KiB = round(float(image_capacity / (8*1024)),2)
    logger.info(f"carrier image: '{carrier_filename}'")
    logger.info(f"carrier image capacity: {cap_b} b = {cap_B} B = {cap_KiB} KiB")
    ##### LOG BLOCK

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

    new_image_array = np.array(new_image_data)  # Convert lists of data to a numpy array
    new_image = Image.fromarray(new_image_array.astype(np.uint8))  # Create image from the array
    new_image.save(output_filename)  # Save the new image as a file

def decode(infile):
    img = Image.open(infile)
    data = np.asarray(img)  # Get the pixel array of the image
    img.close()

    if not ((img.mode == "RGB") or (img.mode == "RGBA")):
        print(f"Error: Image mode must be RGB or RGBA, not {img.mode}")
        return

    bit_string = ""
    output_bytes = b''
    payload_len = 0
    for row in data:
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
                        logger.error("Error: Header is not valid")
                        return
                if (len(output_bytes) == payload_len) and (payload_len != 0):
                    return output_bytes
    logger.error("Error: Payload is incomplete")
    return

def generate_random_image(save_file='result_image.png', width=1_000, height=1_000, chanals=4):
    # default capacity: 488 KiB
    imarray = np.random.rand(width, height, chanals) * 255
    im = Image.fromarray(imarray.astype('uint8')).convert('RGBA')
    im.save(save_file)

def main(args):
    target_obj = args.target_obj
    result_obj = args.result_obj
    if args.e:
        assert (args.d is False)
        if os.path.isfile(target_obj):
            with open(target_obj, 'rb') as f:
                payload_bytes = f.read()
        else:
            payload_bytes = target_obj.encode()
        if args.img is None:
            carrier_filename = ".temp_image.png"
            generate_random_image(save_file=carrier_filename)
        else:
            carrier_filename = args.img
        encode(carrier_filename, result_obj, payload_bytes)
        if args.img is None:
            os.remove(carrier_filename)
        return
    if args.d:
        assert (args.e is False) and (args.img is None)
        result = decode(target_obj)
        logger.info(f'len:\t{len(result)}')
        logger.info(f'decode:\t{result.decode()}')
        result.decode()
        return
    logger.error(f"See help (--help)")
    return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog='stegano.py')
    parser.add_argument('target_obj', type=str, help="Either secret or file with payload")
    parser.add_argument('--img', type=str, help='Image (empty carrier)')
    parser.add_argument('result_obj', type=str, help='Encrypted/decrypted file')
    parser.add_argument('-e', action='store_true', default=False, help='turn on encrypting mode')
    parser.add_argument('-d', action='store_true', default=False, help='turn on decrypting mode')
    args = parser.parse_args()
    logger.debug(f"args::{args}")
    ok = main(args)
    logger.debug(f"end::{__name__}")


