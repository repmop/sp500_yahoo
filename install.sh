curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py --user
[[ ":$PATH:" != *":`python2.7 -m site --user-base`/bin:"* ]] && PATH="`python2.7 -m site --user-base`/bin:${PATH}"
pip install virtualenv --user; export PATH="$PATH:/home/username/opt/python*/bin/python";  virtualenv venv; source venv/bin/activate; pip install  -r requirements.txt
