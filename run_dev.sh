export PYTHONPATH=$PYTHONPATH:$PWD

killall -9 python
killall -9 python2

if which python2 2>/dev/null; then
    PYTHON=python2
else
    PYTHON=python
fi

# Running on the server because.
#$PYTHON ident/identity.py &

$PYTHON node/tornadoloop.py ppl/novaprospekt 127.0.0.1  &
sleep 1
$PYTHON node/tornadoloop.py ppl/genjix 127.0.0.2 tcp://127.0.0.1:12345  &
sleep 1
$PYTHON node/tornadoloop.py ppl/caedes 127.0.0.3 tcp://127.0.0.1:12345  &
sleep 1
$PYTHON node/tornadoloop.py ppl/s_tec 127.0.0.4 tcp://127.0.0.1:12345  &

