export PYTHONPATH=/home/genjix/darkmarket
python tornadoloop.py 127.0.0.1&
sleep 5
python tornadoloop.py 127.0.0.2 tcp://127.0.0.1:12345 &
sleep 5
python tornadoloop.py 127.0.0.3 tcp://127.0.0.1:12345 &
sleep 5
python tornadoloop.py 127.0.0.4 tcp://127.0.0.1:12345 &
