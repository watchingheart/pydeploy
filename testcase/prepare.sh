mkdir -p bak
mkdir -p testdeploy
cd testdeploy
rm -r *
mkdir -p dir1
mkdir -p dir2
cd dir1
mkdir -p commondir
cd commondir
touch samefile
echo 'same' > samefile
touch diffile
echo 'file1' > diffile
cd ..
mkdir -p diffdir1
cd diffdir1
touch txt1
echo 'txt1' > txt1
touch txt2
echo 'txt2' > txt2
cd ..
mkdir -p removedir
cd removedir
touch txt3
echo 'txt3' > txt3
cd ../..
cd dir2
mkdir -p commondir
cd commondir
touch samefile
echo 'same' > samefile
touch diffile
echo 'file2' > diffile
cd ..
mkdir -p diffdir1
cd diffdir1
touch txt1
echo 'txt2' > txt1
cd ..
mkdir -p diffdir2
cd diffdir2
touch txt1
echo 'txt1' > txt1
touch txt2
echo 'txt2' > txt2
cd ../..
