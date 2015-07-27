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
ssh -fN -L 11999:localhost:11991 hnykdan1@kmlinux.fjfi.cvut.cz
python nourisher/main.py -i localhost -p 11999 -n testsber --stdout ../nour.log -l 20 -r -R 1 -x -b firefox
git pull; rm -rf ../nour.log ../out.log; python watchdog.py -a "-i localhost -p 11999 -n testsber --stdout ../nour.log -l 20 -r  -e" -w 300 -m nourisher/main.py -l ../out.log 
```

další dependencies:
```
sudo apt-get update 
sudo apt-get upgrade
sudo apt-get install git gcc phantomjs python3-dev libxml2-dev libxslt1-dev zlib1g-dev virtualenv libjpeg-dev vim screen mongodb-clients libfreetype6 libfreetype6-dev zlib1g-dev
```
