import os

DRYRUN = False
out_type = 'opusenc' # mp3, opus, or opusenc
TEMP_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp')

def load_path_root(new=False):
    if new:
        with open('new_root', 'r') as f:
            path_root = f.read().strip()
    else:
        with open('root', 'r') as f:
            path_root = f.read().strip()
    return path_root

def mirror_directories(path_root, path_mirror):
    for root, dirs, files in os.walk(path_root):
        for d in dirs:
            rel_path = os.path.relpath(os.path.join(root, d), path_root)
            path_mirror_dir = os.path.join(path_mirror, rel_path)
            if not os.path.exists(path_mirror_dir):
                if DRYRUN:
                    print(f'Would create {path_mirror_dir}')
                else:
                    print(f'Creating {path_mirror_dir}')
                    os.makedirs(path_mirror_dir)

FFMPEG_FLAGS = {
    'mp3': '-ab 320k',
    'opus': '-c:a libopus -b:a 128k',
}

def flac_convert(path, new_path, out_type):
    if out_type == 'opusenc':
        if os.path.exists(f'{new_path}.opus'):
            return
        if DRYRUN:
            print(f'Would convert {path} to {new_path}.opus')
            return
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        if os.path.exists(f'{TEMP_DIR}/temp.opus'):
            os.remove(f'{TEMP_DIR}/temp.opus')

        print(f'Converting {path} to {new_path}.opus')
        os.system(f'opusenc --quiet --bitrate 128 "{path}" "{TEMP_DIR}\\temp.opus"')

        print('Moving file')
        os.system(f'move /Y "{TEMP_DIR}\\temp.opus" "{new_path}.opus"')
        print('Completed')
    else:
        if os.path.exists(f'{new_path}.{out_type}'):
            return
        if DRYRUN:
            print(f'Would convert {path} to {new_path}.{out_type}')
            return
        flags = FFMPEG_FLAGS[out_type]
        print(f'Converting {path} to {new_path}.{out_type}')
        os.system(f'ffmpeg -hide_banner -loglevel warning -i "{path}" {flags} -map_metadata 0 -id3v2_version 3 "{new_path}.{out_type}"')

def main():
    path_root = load_path_root()
    path_mirror = load_path_root(new=True)
    mirror_directories(path_root, path_mirror)
    for root, dirs, files in os.walk(path_root):
        for f in files:
            if f.endswith('.flac'):
                path = os.path.join(root, f)
                rel_path = os.path.relpath(path, path_root)
                new_path = os.path.join(path_mirror, rel_path[:-5])
                flac_convert(path, new_path, out_type)
            else:
                path = os.path.join(root, f)
                rel_path = os.path.relpath(path, path_root)
                new_path = os.path.join(path_mirror, rel_path)
                if not os.path.exists(new_path):
                    os.system(f'copy "{path}" "{new_path}"')

if __name__ == '__main__':
    main()