import random
import string

date_format = "%d/%m/%Y %H:%M"

# Convert rrggbb to ints
def hex_to_rgb(hex_color):
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)


# Convert r,g,b to hex
def rgb_to_hex(r, g, b):
    return hex(r)[2:].zfill(2) + hex(g)[2:].zfill(2) + hex(b)[2:].zfill(2)


def random_str(size=8):
	return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(size))