from chip8.emulator import Emulator
import sys


def main():
    argc = len(sys.argv)
    argv = sys.argv
    if argc < 2:
        print('You must provide a file to load')
        return -1
    filename = argv[1]
    print(f'ROM to load is: {filename}')
    emulator: Emulator = None
    with open(filename, 'rb') as f:
        buffer = f.read()
        emulator = Emulator(buffer, filename)

    return emulator.run()


if __name__ == '__main__':
    retc = main()
    exit(retc)
