timeout -s INT 5s python -m cProfile -o try_gui.cprof try_gui.py
pyprof2calltree -k -i try_gui.cprof
