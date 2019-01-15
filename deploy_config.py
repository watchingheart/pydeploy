# coding=utf-8
# author: watchingheart
# email: jzgjava@163.com

app_name='moon'

test=True
if test:
    src = './testcase/testdeploy/dir1'
    dest = './testcase/testdeploy/dir2'
    bak = './testcase/bak'
    bak_exclude = None
else:
    src = '/home/bodi/source/moon'
    dest = '/home/bodi/moon'
    bak = '/home/bodi/bak'
    bak_exclude = 'log'

#变更时忽略掉不作变更的文件或目录
ignore = ('config.py', 'log')

# 是否删除目标目录中有，而源目录中没有的目录和文件
delete_dest = True

# 是否添加目标不存在的目录和文件
add_new = True

# 更新前先自动备份变更内容
auto_backup = True

# 是否只显示差别
show_diff_only = True
