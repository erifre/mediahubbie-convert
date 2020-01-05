import os, time, sys

def cleanup():
    path = "tmp/"
    now = time.time()
    diff = now - (86400)

    if os.path.isdir(path):
        for f in os.listdir(path):
            f = os.path.join(path, f)
            if os.stat(f).st_mtime < diff:
                if os.path.isfile(f):
                    print(f);
                    os.remove(f)
