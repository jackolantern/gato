# GrAphical Terminal Output

Outputs images in a KiTTY terminal: https://sw.kovidgoyal.net/kitty/

Gato differs from KiTTY's builtin `icat` command in that it can display
animated gifs and it can "emojify" text.

Example usage:

To display an animated gif:
```bash
gato --gif ~/img/animated/ed.3.gif
```

To emojify text:
```bash
gato --emojify - <<< "The worst situation: :no_mouth: :beer:"
```

By default, the `--emojify` option causes `gato` to look for files in the
OS specific application data directory.  On Arch Linux this is evidently
`$HOME/.local/share/gato/emoji`.  Any 'png' format files in that directory
which have a "file extension" of `.png` will be found and displayed by `gato`.
A different directory can be specified by using the `--path` option.

