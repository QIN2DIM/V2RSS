# coding=utf-8
import os

# 设定根目录
basedir = os.path.dirname(__file__)
file_lists = []
# 指定想要统计的文件类型
whitelist = ['py']


# 遍历文件, 递归遍历文件夹中的所有
def getFile(base_dir):
    global file_lists
    for parent, dir_names, filenames in os.walk(base_dir):
        for filename in filenames:
            ext = filename.split('.')[-1]
            # 只统计指定的文件类型，略过一些log和cache文件
            if ext in whitelist:
                file_lists.append(os.path.join(parent, filename))


# 统计一个的行数
def countLine(fp_name):
    count = 0
    # 把文件做二进制看待,read.
    for file_line in open(fp_name, 'rb').readlines():
        if file_line != '' and file_line != '\n':  # 过滤掉空行
            count += 1
    print(fp_name + '----', count)
    return count


def __start__():
    getFile(basedir)
    total_line = 0
    for file_list in file_lists:
        total_line += countLine(file_list)

    print(basedir)
    print('total lines:', total_line)


if __name__ == '__main__':
    __start__()
