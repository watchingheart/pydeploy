# pydeploy
A very simple easy-to-use deploy tool, deploy files from source dir to destination dir, can view change difference, deploy with options. Write by python. 

一个简单易用的部署工具，用于文件变更，可以查看变更内容，自动部署变更，自动备份变更文件。

## 测试一下

1. 生成测试目录和文件

**testcase/prepare.sh**

在testcase下建立两个目录，bak - 备份目录，testdeploy - 测试部署。

testdeploy下生成的目录结构如下：

    .
    ├── dir1
    │   ├── commondir
    │   │   ├── diffile
    │   │   └── samefile
    │   ├── diffdir1
    │   │   ├── txt1
    │   │   └── txt2
    │   └── removedir
    │       └── txt3
    └── dir2
        ├── commondir
        │   ├── diffile
        │   └── samefile
        ├── diffdir1
        │   └── txt1
        └── diffdir2
            ├── txt1
            └── txt2

两个目录dir1、dir2准备好了，dir1是源，dir2是目的。

2. diff查看一下

**./deploy.py diff**

    ---------------------- DIFF --------------------
     from 	: ./testcase/testdeploy/dir1
     to 	: ./testcase/testdeploy/dir2
    ------------------------------------------------
    - /diffdir2
    + /removedir
    * /commondir
        * diffile
    * /diffdir1
        * txt1
        + txt2
        
    - 是源没有的
    + 是目的没有的
    * 是两边不一样的
    前面是空格是一样的文件
    
    此处只显示差异，所以没有相同文件。
    
        
3. 部署变更

**./deploy.py deploy**

    -------------------- DEPLOY --------------------
     from 	: ./testcase/testdeploy/dir1
     to 	: ./testcase/testdeploy/dir2
    ------------------------------------------------
     cp -r ./testcase/testdeploy/dir1/removedir ./testcase/testdeploy/dir2
    ... 1 added.
     rm -r ./testcase/testdeploy/dir2/diffdir2
    ... 1 deleted.
     cp ./testcase/testdeploy/dir1/commondir/diffile ./testcase/testdeploy/dir2/commondir
    ... 1 overwrited.
     cp ./testcase/testdeploy/dir1/diffdir1/txt2 ./testcase/testdeploy/dir2/diffdir1
    ... 1 added.
     cp ./testcase/testdeploy/dir1/diffdir1/txt1 ./testcase/testdeploy/dir2/diffdir1
    ... 1 overwrited.
    
 4. 再对比一下
 
 **./deploy.py diff**

    ---------------------- DIFF --------------------
     from 	: ./testcase/testdeploy/dir1
     to 	: ./testcase/testdeploy/dir2
    ------------------------------------------------
    
    部署后目录结构：
    
    .
    ├── dir1
    │   ├── commondir
    │   │   ├── diffile
    │   │   └── samefile
    │   ├── diffdir1
    │   │   ├── txt1
    │   │   └── txt2
    │   └── removedir
    │       └── txt3
    └── dir2
        ├── commondir
        │   ├── diffile
        │   └── samefile
        ├── diffdir1
        │   ├── txt1
        │   └── txt2
        └── removedir
            └── txt3

没有不同内容。

## 备份变更

**./deploy.py backup**

    -------------------- BACKUP --------------------
     from 	: ./testcase/testdeploy/dir1
     to 	: ./testcase/testdeploy/dir2
     bak 	: ./testcase/bak
    ------------------------------------------------
    BACKUP: cp ./testcase/testdeploy/dir2/commondir/diffile ./testcase/bak/20190115_131505/commondir
    BACKUP: cp ./testcase/testdeploy/dir2/diffdir1/txt1 ./testcase/bak/20190115_131505/diffdir1
    BACKUP: cp -r ./testcase/testdeploy/dir2/diffdir2 ./testcase/bak/20190115_131505/.

## 全量备份

**./deploy.py backup_all**

    ------------------ BACKUP ALL -------------------
    tar zcvf ./testcase/bak/moon_20190115_131633.tar.gz ./testcase/testdeploy/dir2
    a ./testcase/testdeploy/dir2
    a ./testcase/testdeploy/dir2/diffdir2
    a ./testcase/testdeploy/dir2/commondir
    a ./testcase/testdeploy/dir2/diffdir1
    a ./testcase/testdeploy/dir2/diffdir1/txt1
    a ./testcase/testdeploy/dir2/commondir/diffile
    a ./testcase/testdeploy/dir2/commondir/samefile
    a ./testcase/testdeploy/dir2/diffdir2/txt2
    a ./testcase/testdeploy/dir2/diffdir2/txt1
    ------------------------------------------------

## 配置选项

    # 应用名称，作为备份包的前缀
    app_name = 'test'

    # 变更源目录
    src = './testcase/testdeploy/dir1'
    
    # 变更目的目录
    dest = './testcase/testdeploy/dir2'
    
    # 备份目录
    bak = './testcase/bak'
    
    # 备份排除的目录和文件，可多个，如：('log')
    bak_exclude = None

    #变更忽略
    ignore = ('config.py', 'log')

    # 是否删除目标目录中有，而源目录中没有的目录和文件
    delete_dest = True

    # 是否添加目标不存在的目录和文件
    add_new = True

    # 更新前先自动备份变更内容
    auto_backup = True

    # 是否只显示差别
    show_diff_only = True

## TODO

 - [X] 比较源和目的文件的新旧，提供选项来进行设置变更。

 - [X] 对变更文件内容进行比较，输出对比报告
