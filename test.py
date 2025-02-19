import subprocess

lilypond_code = r"""
\version "2.24.0"
\relative c' {
  \key c \major
  \time 4/4
  c4 d e f | g a b c | c2 r2
}
"""

# Salva il file
with open("spartito.ly", "w") as f:
    f.write(lilypond_code)

# Genera l'immagine PNG ritagliata intorno alla battuta
subprocess.run(
    [
        "lilypond",
        "--png",
        "-dpreview",
        '-dpaper-size="a5"',
        "-dresolution=300",
        "spartito.ly",
    ]
)
