# Binance DepthCache. Deploy on server Ubuntu 18.04.03 (DigitalOcean 4GB/2CPU)

## Install Python 3.8

**Make sure that you are logged in as root**

```
apt-get update
add-apt-repository ppa:jonathonf/python-3.8 -y
apt-get install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa -y
apt-get install python3.8 -y
apt-get install python3.8-dev -y
apt-get install python3.8-venv
apt-get install python3-distutils
apt-get install build-essential -y
wget https://bootstrap.pypa.io/get-pip.py
python3.8 get-pip.py
ln -s /usr/bin/python3.8 /usr/local/bin/python
```

## Install Git, DepthCache, Redis

```
apt-get install git-core
git clone https://github.com/volkovartem77/depthcache.git
```
```
apt-get install redis-server -y
chown redis:redis /var/lib/redis
```

## Creating virtualenv using Python 3.8

```
pip install virtualenv
virtualenv -p /usr/bin/python3.8 ~/depthcache/venv
cd ~/depthcache; . venv/bin/activate
pip install -r requirements.txt
python configure.py
deactivate
```


## Install & configure supervisor

```
apt-get install supervisor -y
cp depthcache.conf /etc/supervisor/conf.d/depthcache.conf
mkdir /var/log/depthcache
supervisorctl reread
supervisorctl reload
supervisorctl status
```

## Usage
Update from Git
```
supervisorctl status
supervisorctl stop all
cd ~/depthcache; git pull origin master
```
```
python configure.py
supervisorctl start all
```
