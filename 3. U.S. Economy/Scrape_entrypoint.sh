# /bin/bash -c "source /app/env.source"

yum remove python3-pip -y
yum install wget -y
yum install which -y
yum install findutils -y
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py

yum install vim-minimal -y
# yum install python-pip -y
pip install -r requirements.txt
python3 daily_update.py
# python3 -v daily_update.py
    # adds verbose output logs, good for debugging
# tail -f /dev/null   # to keep the task running so it can be troubleshot