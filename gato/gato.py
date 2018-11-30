#!/usr/bin/env python
"""
Gato: GrAphical Terminal Output
"""

import os
import sys
import time
import array
import fcntl
import termios
import argparse
import tempfile
from collections import namedtuple as nt
from base64 import standard_b64encode

import appdirs
from PIL import Image

AppName = 'gato'
AppAuthor = 'jackolantern'

ScreenInfo = nt('ScreenInfo', ['numcols', 'numrows', 'width', 'height'])

def get_screen_info():
    """
    returns `ScreenInfo`
    """
    buf = array.array('H', [0, 0, 0, 0])
    fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, buf)
    return ScreenInfo(*buf)

def move_cursor_up(n):
    """
    Moves the cursor up `n` lines.
    """
    sys.stdout.buffer.write(b'\033[')
    sys.stdout.buffer.write(str(n).encode('ascii'))
    sys.stdout.buffer.write(b'A')
    sys.stdout.buffer.flush()

def save_cursor_postition():
    """
    Saves the position of the cursor.
    Used in conjunction with `restore_cursor_postition`.
    """
    sys.stdout.buffer.write(b'\033[s')
    sys.stdout.buffer.flush()

def restore_cursor_postition():
    """
    Restores the position of the cursor.
    Used in conjunction with `save_cursor_postition`.
    """
    sys.stdout.buffer.write(b'\033[u')
    sys.stdout.buffer.flush()

def display_png(fp, r=0, c=0, temporary=False):
    """
    Displays a 'png' image.
    """
    t = b't' if temporary else b'f'
    fp = standard_b64encode(fp.encode('utf-8'))
    sys.stdout.buffer.write(b'\033_Gf=100,t=%b,r=%d,c=%d,a=T;' % (t, r, c))
    sys.stdout.buffer.write(fp)
    sys.stdout.buffer.write(b'\033\\')
    sys.stdout.buffer.flush()

def extract_frames(path):
    """
    Extract frames from an animated gif.
    """
    height = 0
    frames = []
    frame = Image.open(path)
    nframes = 0
    while frame:
        _, fp = tempfile.mkstemp(suffix='.png')
        height = max(height, frame.size[1])
        frame.save(fp, format='png')
        frames.append((fp, frame.info['duration'] or 100))
        nframes += 1
        try:
            frame.seek(nframes)
        except EOFError:
            break
    return height, frames

def gif(args):
    """
    Displays an animated gif.
    """
    height, frames = extract_frames(args.gif)
    info = get_screen_info()
    cols = height // (info.height // info.numcols) + 1
    ## The following creates enough room to display the image.
    print('\n' * cols)
    move_cursor_up(cols)

    try:
        while True:
            for (fp, duration) in frames:
                save_cursor_postition()
                display_png(fp)
                restore_cursor_postition()
                time.sleep(10 / duration)
    except KeyboardInterrupt:
        print('\n' * cols)
    finally:
        for (fp, _) in frames:
            os.remove(fp)

def image(args):
    """
    Command to display an image.
    """
    img = Image.open(args.image)
    _, fp = tempfile.mkstemp(suffix='.png')
    img.save(fp, format='png')
    display_png(fp, temporary=True)
    sys.stdout.write('\n')

def emojify_text(path, text):
    """
    Command helper to emojify a block of text.
    """
    name = []
    state = 'normal'
    for c in text:
        # print(c, sep='.', file=sys.stderr)
        if c is None:
            break
        if c == ':':
            if state == 'normal':
                state = 'emoji'
            else:
                state = 'normal'
                if not name:
                    sys.stdout.write(':')
                    continue
                png = os.path.join(path, ''.join(name)) + '.png'
                if os.path.exists(png):
                    sys.stdout.flush()
                    display_png(png, 1, 2)
                else:
                    sys.stdout.write(':')
                    sys.stdout.write(''.join(name))
                    sys.stdout.write(c)
                name = []
        else:
            if state == 'normal':
                sys.stdout.write(c)
            else:
                if c in ' \t\n()!@#$%^&*~`\'"?/\\;<.':
                    state = 'normal'
                    sys.stdout.write(':')
                    sys.stdout.write(''.join(name))
                    sys.stdout.write(c)
                    name = []
                else:
                    name.append(c)
    if name or state == 'emoji':
        sys.stdout.write(':')
        sys.stdout.write(''.join(name))
    sys.stdout.write('\n')

def emojify(args):
    """
    Command to emojify text.
    """
    if args.emojify == '-':
        for line in sys.stdin:
            if not line:
                break
            emojify_text(args.path, line)
    else:
        emojify_text(args.path, args.emojify)

def main():
    """
    The entrypoint.
    """
    data_dir = appdirs.user_data_dir(AppName, AppAuthor)
    emoji_dir = os.path.join(data_dir, 'emoji')
    parser = argparse.ArgumentParser(
        description='Display images in the terminal.')
    parser.add_argument(
        '--image', metavar='PATH_TO_IMAGE', type=str,
        help='The path to the image to display.')
    parser.add_argument(
        '--gif', metavar='PATH_TO_ANIMATED_GIF', type=str,
        help='The path to the animated gif to display.')
    parser.add_argument(
        '--emojify', metavar='TEXT', type=str, help='Text to emojify.')
    parser.add_argument(
        '--path', metavar='PATH_TO_EMOJIS', type=str,
        default=emoji_dir,
        help='The path to the emoji files to use.  Defaults to "%s"' % emoji_dir)
    args = parser.parse_args()
    if args.gif:
        gif(args)
    elif args.image:
        image(args)
    elif args.emojify:
        emojify(args)

if __name__ == '__main__':
    main()
