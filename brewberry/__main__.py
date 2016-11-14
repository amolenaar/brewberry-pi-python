import sys
import main

if __name__ == '__main__':
    if '--fake' in sys.argv:
        import fakeio as io
        import time
        io.time = time.time();
        io.time_updater = lambda t: time.time()
    else:
        import raspio as io

    main.main(io)

# vim:sw=4:et:ai
