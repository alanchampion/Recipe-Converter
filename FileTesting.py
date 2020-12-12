import tempfile
import subprocess
import os

def edit(data):
    fdes = -1
    path = None
    fp = None
    try:
        fdes, path = tempfile.mkstemp(suffix='.txt', text=True)
        fp = os.fdopen(fdes, 'w+')
        fdes = -1
        fp.write(data)
        fp.close()
        fp = None

        editor = (os.environ.get('VISUAL') or
                  os.environ.get('EDITOR') or
                  'vim')
        subprocess.check_call([editor, path])

        fp = open(path, 'r')
        return fp.read()
    finally:
        if fp is not None:
            fp.close()
        elif fdes >= 0:
            os.close(fdes)
        if path is not None:
            try:
                os.unlink(path)
            except OSError:
                pass

# text = edit('Hello, World!')
# print(text)

from subprocess import call

EDITOR = os.environ.get('EDITOR', 'vim')
initial_message = b"Please edit the file:"

with tempfile.NamedTemporaryFile(suffix=".tmp", dir=os.getcwd(), delete=False) as tmp:
    tmp.write(initial_message)
    tmp.flush()
    call([EDITOR, "-n", tmp.name])
    #file editing in vim happens here
    #file saved, vim closes
    #do the parsing with `tempfile` using regular File operations
    tmp.seek(0)
    print(tmp.read().decode('ascii'))
    tmp.close()
    file = open(tmp.name, "r")
    print(file.read())
    # os.unlink(tmp.name)