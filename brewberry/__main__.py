import sys
import main

if __name__ == '__main__':
    if '--fake' in sys.argv:
        import fakeio as io
        io.static_time = False
        import time
        io.time = time.time();
        io.INTERVAL = main.SAMPLER_INTERVAL
    else:
        import raspio as io

    main.main(io)

# vim:sw=4:et:ai
