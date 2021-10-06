# -*- coding: utf-8 -*-
# Time       : 2021/9/16 23:06
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os


def pack_by_armor(main_file, logo_path: str = None, one_file: bool = True, headless: bool = True,
                  obfuscate_mode: str = None):
    logo_path = "" if logo_path is None else f"-i {logo_path}"
    one_file = "-F" if one_file is True else ""
    headless = "-w" if headless is True else ""
    obfuscate_mapping = {
        'super': "--advanced 2",
        'advanced': "--advanced 1",
        'VM-s': "--advanced 3",
        'VM-a': "--advanced 4",
    }
    obfuscate_mode = obfuscate_mapping['VM-a'] if obfuscate_mode is None else obfuscate_mapping[obfuscate_mode]

    # os.system('pyarmor pack -e "-i flash_auto.ico -F -w" -x "--advanced 4" .\main.py')#
    print(f'pyarmor pack -e "{logo_path} {one_file} {headless}" -x "{obfuscate_mode}" {main_file}')
    os.system(f'pyarmor pack -e "{logo_path} {one_file} {headless}" -x "{obfuscate_mode}" {main_file}')


if __name__ == '__main__':
    pack_by_armor(
        './panel.py',
        'pack/logo.ico',
        obfuscate_mode="super"
    )
