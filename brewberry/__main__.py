import sys
import main

if __name__ == '__main__':
    if '--fake' in sys.argv:
        import fakeio as io
    else:
        import raspio as io

    main.main(io)

