import os
import shutil

def flatten(p):
    dir_list = next(os.walk(p))[1]

    for dir in dir_list:
        dir = os.path.join(p, dir)
        files_by_number = {int(os.path.splitext(os.path.basename(f))[0]): f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))}

        max_file = max(files_by_number.values(), key=lambda x: files_by_number.keys()[files_by_number.values().index(x)])
        ext = os.path.splitext(os.path.basename(max_file))[1]

        shutil.copy(os.path.join(dir, max_file), os.path.join(p, dir + ext))

if __name__ == "__main__":
    flatten(".")
    print "Done!"