#!/usr/bin/env bash
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000
nohup pipenv run python web.py &