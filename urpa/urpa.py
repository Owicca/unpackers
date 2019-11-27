#!/usr/bin/env python3
import zlib, argparse, os, sys, pickle
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument('-p', dest="path", default="./", required=True)
parser.add_argument('-d', dest="dump", default="./dump", required=True)
parser.add_argument('-v', dest="verbose", action="store_true")
args = parser.parse_args()

filename = args.path

archives = [ ]
f = open(filename, "rb")
l = f.readline()

if l.startswith(b"RPA-3.0 "):
    offset = int(l[8:24], 16)
    key = int(l[25:33], 16)
    f.seek(offset)
    index = pickle.loads(zlib.decompress(f.read()))

    for k in index.keys():

        if len(index[k][0]) == 2:
            index[k] = [ (offset ^ key, dlen ^ key) for offset, dlen in index[k] ]
        else:
            index[k] = [ (offset ^ key, dlen ^ key, start) for offset, dlen, start in index[k] ]

            archives.append((filename, index))

            f.close()
            continue

        if l.startswith(b"RPA-2.0 "):
            offset = int(l[8:], 16)
            f.seek(offset)
            index = loads(zlib.decompress(f.read()))
            archives.append((filename, index))
            f.close()
            continue

        f.close()

        index = loads(zlib.decompress(open(filename, "rb").read()))
        archives.append((filename, index))

dump_dir = Path(args.dump)

if not dump_dir.is_dir():
    os.mkdir(dump_dir)


count = 0
with open(filename, "rb") as arch:
    for filename, file_info in archives:
        for file_path in file_info:
            count += 1
            if count >= len(file_info):
                break
            path_list = file_path.split("/")[:-1]
            directory = "/".join(path_list)
            directory = dump_dir / directory
            if args.verbose:
                print(f"Writing {file_path} in {directory}")
            if not directory.is_dir():
                os.mkdir(directory)

            with open(dump_dir / file_path, "wb+") as dump_file:
                offset, length, start = file_info[file_path][0]
                arch.seek(offset, 0)
                read_data = arch.read(length)
                dump_file.write(read_data)
