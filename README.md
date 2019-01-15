# pydeploy
A very simple easy-to-use deploy tool, deploy files from soure dir to dest dir, can view change difference, deploy with options. Write by python. 

一个简单易用的部署工具，用于文件变更，可以查看变更内容，自动部署变更，自动备份变更文件。

## 测试一下

1. 生成测试目录和文件

**testcase/prepare.sh**

    .
    |____dir2
    | |____commondir
    | | |____diffile
    | | |____samefile
    | |____removedir
    | | |____txt3
    | |____diffdir1
    | | |____txt2
    | | |____txt1
    |____dir1
    | |____commondir
    | | |____diffile
    | | |____samefile
    | |____removedir
    | | |____txt3
    | |____diffdir1
    | | |____txt2
    | | |____txt1

两个目录dir1,dir2准备好了，dir1是源，dir2是目的。

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

没有不同内容。
