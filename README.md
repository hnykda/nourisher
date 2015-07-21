# Nourisher

Pro spuštění je potřeba:

```
mkdir sber
cd sber
git clone git@github.com:kotrfa/nourisher.git
virtualenv --python=/usr/bin/python3 .venv
ln -s .venv/bin/activate
source activate
pip install -r nourisher/requirements.txt
ssh -fN -L 11995:localhost:11994 hnykdan1@kmlinux.fjfi.cvut.cz
python nourisher/main.py -i localhost -p 11995 -n testsber --random
```
