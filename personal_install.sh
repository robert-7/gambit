# clone repository
cd /home/robert/code/github
git clone git://github.com/gambitproject/gambit.git gambit.git
cd gambit.git

# install packages
sudo apt-get install autotools-dev
sudo apt-get install automake
sudo apt-get install libtool
###### don't know if necessary ####
# sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 1397BC53640DB551
# sudo apt-get update
###################################
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

# necessary install stuff
wget https://bootstrap.pypa.io/ez_setup.py
sudo python ez_setup.py

# get pip (explanation here: https://pip.pypa.io/en/stable/installing/)
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py 

pip install cython

# this explained a probably I ran into: http://stackoverflow.com/questions/21530577/fatal-error-python-h-no-such-file-or-directory
sudo apt-get install python-dev

# needed for compilations
sudo apt-get install g++

# the actual build
python setup.py build
sudo python setup.py install

# run tests
cd gambit/tests
sudo apt-get install python-nose
nosetests
