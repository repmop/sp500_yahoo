curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user
[[ ":$PATH:" != *":`python3.8 -m site --user-base`/bin:"* ]] && PATH="`python3.8 -m site --user-base`/bin:${PATH}"
pip3 install virtualenv --user; export PATH="$PATH:/home/username/opt/python*/bin/python";  virtualenv venv; source venv/bin/activate; pip install  -r requirements.txt
