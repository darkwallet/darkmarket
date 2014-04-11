if which python2 2>/dev/null; then
    PYTHON=python2
else
    PYTHON=python
fi

$PYTHON node/tornadoloop.py 127.0.0.1 &
sleep 1
$PYTHON node/tornadoloop.py 127.0.0.2 tcp://127.0.0.1:12345 &
xdg-open http://localhost:8888
