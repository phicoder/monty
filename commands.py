import os
import sys
import cmds
import types

__dir__ = os.path.dirname(__file__)


class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WARNING_BOX = '\x1b[0;37;41m'
    END_BOX = '\x1b[0m'


commandsMap = {}
for command in cmds.__all__:
    __import__("cmds." + command)
    module = sys.modules["cmds." + command]
    if not hasattr(module, 'description') or not hasattr(module, 'run') or type(module.description) != str or type(module.run) != types.FunctionType:
        continue
    commandsMap[command] = {
        'description': module.description,
        'run': module.run
    }


def usage():
    usage = ""

    with open(os.path.join(__dir__, 'monty.txt'), 'r') as f:
        usage += f.read() + "\n"

    usage += colors.WARNING + "Usage:\n" + colors.ENDC
    usage += "  command\n\n"

    usage += colors.WARNING + "Available commands:\n" + colors.ENDC

    spaces = max([len(command) for command in commandsMap.keys()]) + 2

    for command in sorted(commandsMap.keys()):
        usage += colors.OKGREEN + "  " + command + colors.ENDC
        usage += "%s%s\n" % ((spaces - len(command))
                             * " ", commandsMap[command]['description'])

    return usage


def commandExists(command):
    if command not in commandsMap.keys():
        text = "  Command \"%s\" is not defined.  " % command
        line = "\n" + len(text) * " " + "\n"
        print(colors.WARNING_BOX + line + text + line + colors.END_BOX)
        return False
    return True


def run(argv):
    command = argv[1]
    if commandExists(command):
        commandsMap[command]['run'](argv)
