# clone repository
GIT_INSTALL_DIR=/home/vagrant/Desktop/code/github
mkdir -p $GIT_INSTALL_DIR
cd $GIT_INSTALL_DIR
git clone git://github.com/gambitproject/gambit.git gambit.git
cd gambit.git

# install packages
sudo apt-get install -y g++
sudo apt-get install -y autotools-dev
sudo apt-get install -y automake
sudo apt-get install -y libtool
sudo apt-get install -y libwxgtk2.8-dev libwxgtk2.8-dbg

# do make our program?
mkdir m4
aclocal
libtoolize
automake --add-missing
autoconf
./configure
make
sudo make install

# Now switch to ./src/python to finish python setup
cd src/python

# necessary install python modules, ensuring you have the most updated python version
sudo apt-get upgrade -y python
wget https://bootstrap.pypa.io/ez_setup.py
sudo python ez_setup.py

# get pip (explanation here: https://pip.pypa.io/en/stable/installing/)
wget https://bootstrap.pypa.io/get-pip.py
mkdir -p /home/vagrant/.cache/pip/http
sudo -H python get-pip.py 

# install cython module
sudo -H pip install cython

# this explained a probably I ran into: 
# http://stackoverflow.com/questions/21530577/fatal-error-python-h-no-such-file-or-directory
sudo apt-get install -y python-dev

# the actual build
python setup.py build
sudo python setup.py install

# install deuces for solving poker hands
sudo -H pip install deuces

# install pudb for debugging and give permissions to the folder
sudo -H pip install pudb
mkdir -p /home/vagrant/.config/pudb
sudo chmod 777 /home/vagrant/.config/pudb

# optional install to write games as xml format
sudo -H pip install lxml

# run tests
cd gambit/tests
sudo apt-get install -y python-nose
nosetests

# move downloaded files to ignored folder
cd /home/vagrant/Desktop/code/github/gambit.git/src/python
mkdir downloads
mv ez_setup.py downloads/ez_setup.py
mv get-pip.py downloads/get-pip.py
mv setuptools-* downloads/
