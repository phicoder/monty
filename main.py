from sys import argv
import commands


def main():
    if len(argv) == 1:
        print(commands.usage())
        return 0
    commands.run(argv)


if __name__ == '__main__':
    main()
