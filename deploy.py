#!/usr/bin/python3
# author: watchingheart
# email: jzgjava@163.com

import os
from io import StringIO
import datetime
import filecmp
import difflib
import fire
import deploy_config


def tabs(count):
    return '    ' * count


def print_file(buffer, flag, path, file, level, newer=None, change_size=0):
    full_path = os.path.join(path, file)
    msg = '%s%s %s%s' % (tabs(level), flag, '/' if os.path.isdir(full_path) else '', file)
    buffer.write(msg)
    if os.path.isfile(full_path):
        if newer is not None:
            buffer.write(' NEWER' if newer else ' OLDER')
        if change_size != 0:
            buffer.write(' [{:+d} Bytes]'.format(change_size))
    buffer.write('\n')


def compare_stat(f1, f2):
    left_stat = os.stat(f1)
    right_stat = os.stat(f2)
    if left_stat.st_mtime > right_stat.st_mtime:
        newer = True
    elif left_stat.st_mtime < right_stat.st_mtime:
        newer = False
    else:
        newer = None
    change_size = left_stat.st_size - right_stat.st_size
    return newer, change_size


def print_cmp(cmp, level=0):
    buffer = StringIO()
    count: int = 0
    all_files = sorted(set(cmp.left_only) | set(cmp.common_files) | set(cmp.right_only))
    for f in all_files:

        if f in deploy_config.ignore:
            continue
        if f in cmp.left_only:  # 新增的变更文件或目录
            print_file(buffer, '+', cmp.left, f, level)
        elif f in cmp.right_only:  # 变更中不包括的文件或目录
            print_file(buffer, '-', cmp.right, f, level)
        elif f in cmp.same_files:  # 内容相同未变更的文件
            if deploy_config.show_diff_only:
                continue
            full_path = os.path.join(cmp.left, f)
            if os.path.isfile(full_path):
                newer, change_size = compare_stat(full_path, os.path.join(cmp.right, f))
                print_file(buffer, ' ', cmp.left, f, level, newer, change_size)
            else:
                print_file(buffer, ' ', cmp.left, f, level)
        else:  # 变更内容的文件
            full_path = os.path.join(cmp.left, f)
            if os.path.isfile(full_path):
                newer, change_size = compare_stat(full_path, os.path.join(cmp.right, f))
                print_file(buffer, '*', cmp.left, f, level, newer, change_size)
            else:
                print_file(buffer, '*', cmp.left, f, level)
        count += 1

    if level == 0:  # 最上一层输出打印信息
        print(buffer.getvalue(), end='')
        buffer.close()
        buffer = StringIO()
    for f in cmp.subdirs:  # 处理子目录
        if f in deploy_config.ignore:
            continue
        sub_count, sub_buffer = print_cmp(cmp.subdirs[f], level+1)
        count += sub_count
        if sub_count > 0:  # 判断目录是否有变更
            print_file(buffer, '*', cmp.left, f, level)
            buffer.write(sub_buffer.getvalue())
        else:
            if not deploy_config.show_diff_only:
                print_file(buffer, ' ', cmp.left, f, level)
        if level == 0:  # 最上一层输出打印信息
            print(buffer.getvalue(), end='')
            buffer.close()
            buffer = StringIO()
    return count, buffer


def mk_bak_dir():
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # 当前日期时间作为临时目录
    bak_dir = os.path.join(deploy_config.bak, now)
    if not os.path.exists(bak_dir):
        os.mkdir(bak_dir)
    return bak_dir


def backup_compare(bak_dir, cmp):
    if not deploy_config.auto_backup:
        return

    file_list = sorted(set(cmp.right_only) | set(cmp.diff_files) | set(cmp.subdirs))

    count = len(file_list)
    if count > 0:
        for f in file_list:
            if f in deploy_config.ignore:
                continue
            if (not deploy_config.delete_dest) and f in cmp.right_only:  # 目标目录中多余文件，如果不删除，不需要备份
                continue
            full_path = os.path.join(cmp.right, f)
            rel_path = os.path.relpath(cmp.right, deploy_config.dest)
            bak_path = os.path.join(bak_dir, rel_path)
            # 按目录层次创建目录
            os.makedirs(bak_path, exist_ok=True)
            if os.path.isdir(full_path):
                sub_cmp = cmp.subdirs.get(f, None)
                if sub_cmp is None:
                    cmd = 'cp -r %s %s' % (full_path, bak_path)
                    print('BACKUP: %s' % cmd)
                    os.system(cmd)
                else:
                    backup_compare(bak_dir, sub_cmp)
            else:
                cmd = 'cp %s %s' % (full_path, bak_path)
                print('BACKUP: %s' % cmd)
                os.system(cmd)


def deploy_compare(cmp, delete_no_used):
    change_count = 0
    # 新增的变更文件或目录
    count = len(cmp.left_only)
    if count > 0:
        if deploy_config.add_new:
            skip = 0
            for f in cmp.left_only:
                if f in deploy_config.ignore:
                    skip += 1
                    continue
                full_path = os.path.join(cmp.left, f)
                if os.path.isdir(full_path):
                    cmd = 'cp -r %s %s' % (full_path, cmp.right)
                else:
                    cmd = 'cp %s %s' % (full_path, cmp.right)
                print(' %s' % cmd)
                os.system(cmd)
            change = count - skip
            if change > 0:
                print(f'ADD ... {change}')
            change_count += change

    # 变更中不包括的文件或目录
    count = len(cmp.right_only)
    if count > 0:
        if delete_no_used:
            skip = 0
            for f in cmp.right_only:
                if f in deploy_config.ignore:
                    skip += 1
                    continue
                full_path = os.path.join(cmp.right, f)
                if os.path.isdir(full_path):
                    cmd = 'rm -r %s' % full_path
                else:
                    cmd = 'rm %s' % full_path
                print(' %s' % cmd)
                os.system(cmd)
            change = count - skip
            if change > 0:
                print(f'DELETE ... {change}')
            change_count += change

    # 变更内容的文件
    count = len(cmp.diff_files)
    if count > 0:
        skip = 0
        for f in cmp.diff_files:
            if f in deploy_config.ignore:
                skip += 1
                continue
            full_path = os.path.join(cmp.left, f)
            if os.path.isdir(full_path):
                deploy_compare(cmp.subdirs[f], delete_no_used)
            else:
                cmd = 'cp %s %s' % (full_path, cmp.right)
                print(' %s' % cmd)
                os.system(cmd)
            change = count - skip
            if change > 0:
                print(f'UPDATE ... {change}')
            change_count += change

    # 子目录
    for f in cmp.subdirs:
        if f in deploy_config.ignore:
            continue
        sub_count = deploy_compare(cmp.subdirs[f], delete_no_used)
        change_count += sub_count

    return change_count


class Deploy():

    config = deploy_config

    def __str__(self):
        return """
        config      查看配置参数
        view        显示配置文件内容
        backup_all  全量备份目标目录
        backup      增量备份目标变更文件
        deploy      增量变更
        """

    @staticmethod
    def diff(diff_file=None, swap=False, show_diff_only=True):
        deploy_config.show_diff_only = show_diff_only
        if diff_file is None:
            src = deploy_config.src
            dest = deploy_config.dest
        else:
            src = os.path.join(deploy_config.src, diff_file)
            dest = os.path.join(deploy_config.dest, diff_file)
        if swap:  # 交换源和目的
            src, dest = dest, src
        print('---------------------- DIFF --------------------')
        print(' from \t: %s' % src)
        print(' to \t: %s' % dest)
        print('------------------------------------------------')
        if os.path.isdir(src):  # 目录对比
            cmp = filecmp.dircmp(src, dest)
            total, buf = print_cmp(cmp)
            if total == 0:
                print()
                print('  No differences found.')
            print()
        else:  # 比较文件内容
            newer, change_size = compare_stat(src, dest)
            print(diff_file, end='')
            if newer is not None:
                print(' NEWER' if newer else ' OLDER', end='')
            if change_size != 0:
                print(' [%s Bytes]' % change_size, end='')
            print('\n')
            d = difflib.Differ()
            with open(src, 'r') as file1:
                content1 = file1.read().splitlines()
            with open(dest, 'r') as file2:
                content2 = file2.read().splitlines()
            if show_diff_only:
                print('\n'.join(difflib.unified_diff(content1, content2)))
                print()
            else:
                print('\n'.join(d.compare(content1, content2)))

    @staticmethod
    def backup_all():
        print('------------------ BACKUP ALL -------------------')
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        cmd = 'tar zcvf %s/%s_%s.tar.gz %s' % (deploy_config.bak, deploy_config.app_name, now, deploy_config.dest)
        if deploy_config.bak_exclude is not None:
            cmd = '%s --exclude %s' % (cmd, deploy_config.bak_exclude)
        print(cmd)
        flag = os.system(cmd)
        if flag != 0:
            print('  complete with error: %s' % flag)
        print('------------------------------------------------')
        print()

    @staticmethod
    def backup_change():
        src = deploy_config.src
        dest = deploy_config.dest
        bak = deploy_config.bak
        print('-------------------- BACKUP --------------------')
        print(' from \t: %s' % src)
        print(' to \t: %s' % dest)
        print(' bak \t: %s' % bak)
        print('------------------------------------------------')
        cmp = filecmp.dircmp(deploy_config.src, dest)
        backup_compare(mk_bak_dir(), cmp)

    @staticmethod
    def deploy(diff_file=None, swap=False, delete_dest=True, add_dest=True, auto_backup=None):
        deploy_config.delete_dest = delete_dest
        deploy_config.add_new = add_dest
        if auto_backup:
            deploy_config.auto_backup = auto_backup
        if diff_file is None:
            src = deploy_config.src
            dest = deploy_config.dest
        else:  # 子目录或文件
            src = os.path.join(deploy_config.src, diff_file)
            dest = os.path.join(deploy_config.dest, diff_file)
        if swap:  # 交换源和目的
            src, dest = dest, src
        print('-------------------- DEPLOY --------------------')
        print(' from \t: %s' % src)
        print(' to \t: %s' % dest)
        print('------------------------------------------------')
        if os.path.isdir(src):  # 目录对比
            cmp = filecmp.dircmp(src, dest)
            if deploy_config.auto_backup:
                backup_compare(mk_bak_dir(), cmp)
                print('------------------------------------------------')
            change_count = deploy_compare(cmp, deploy_config.delete_dest)
            if change_count == 0:
                print()
                print('  Nothing changed.')
                print()
        else:
            same = filecmp.cmp(src, dest)
            if same:
                print()
                print('  Same file content.')
                print('  Nothing changed.')
                print()
            else:
                if auto_backup:  # 自动备份文件
                    bak_dir = mk_bak_dir()
                    cmd = 'cp %s %s' % (dest, os.path.join(bak_dir, diff_file))
                    print('BACKUP: %s' % cmd)
                    os.system(cmd)
                cmd = 'cp %s %s' % (src, dest)
                print(' %s' % cmd)
                os.system(cmd)
                print()

    @staticmethod
    def view():
        print(open('deploy_config.py').read())


if __name__ == '__main__':
    fire.Fire(Deploy)
