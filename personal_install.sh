# clone repository
cd /home/robert/code/github
git clone git://github.com/gambitproject/gambit.git gambit.git
cd gambit.git

# install packages
sudo apt-get install -y g++
sudo apt-get install -y autotools-dev
sudo apt-get install -y automake
sudo apt-get install -y libtool

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
sudo python get-pip.py 

# install cython module
sudo pip install cython

# this explained a probably I ran into: http://stackoverflow.com/questions/21530577/fatal-error-python-h-no-such-file-or-directory
sudo apt-get install python-dev

# the actual build
python setup.py build
sudo python setup.py install

# install deuces for solving poker hands
sudo pip install deuces

# install pudb for debugging and give permissions to the folder
sudo pip install pudb
sudo chmod 777 /home/vagrant/.config/pudb

# optional install to write games as xml format
sudo pip install lxml

# run tests
cd gambit/tests
sudo apt-get install python-nose
nosetests

# move downloaded files to ignored folder
cd ../../../..
mkdir downloads
mv ez_setup.py downloads/ez_setup.py
mv get-pip.py downloads/get-pip.py
mv setuptools-28.6.1.zip downloads/setuptools-28.6.1.zip