# Nourisher

Pro spuštění je potřeba:

```
mkdir sber
cd sber
virtualenv --python=/usr/bin/python3 .venv
ln -s .venv/bin/activate
source activate
git clone https://github.com/kotrfa/nourisher.git
pip install -r nourisher/requirements.txt
ssh -fN -L 11995:localhost:11994 hnykdan1@kmlinux.fjfi.cvut.cz
python nourisher/nourisher/main.py -i localhost -p 11995 -n testsber --random
```

další dependencies:
```
sudo apt-get update 
sudo apt-get upgrade
sudo apt-get install git gcc phantomjs python3-dev libxml2-dev libxslt1-dev zlib1g-dev virtualenv libjpeg-dev vim screen mongodb-clients libfreetype6 libfreetype6-dev zlib1g-dev
```
