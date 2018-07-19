import os
import urllib.request
import shutil
import json
import tempfile
from io import BytesIO
from zipfile import ZipFile


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


description = 'Adds required packages to your composer.json and installs them.'
workDir = os.getcwd()


def run(argv):
    if len(argv) < 3:
        return 0

    package = argv[2]
    version = ''
    if len(argv) == 4:
        version = argv[3]

    url = fetchPackageUrl(package, version)


def fetchPackageUrl(package, version):
    url = 'https://pypi.python.org/pypi/%s/json' % package
    try:
        resp = urllib.request.urlopen(url)
        data = json.loads(resp.read().decode(
            resp.info().get_param('charset') or 'utf-8'))
        processPackage(data, version)
    except urllib.error.HTTPError as e:
        printWarning(
            "Could not find package %s at any version for your minimum-stability (stable). Check the package spelling or your minimum-stability" % package)


def printWarning(rawText):
    width = shutil.get_terminal_size().columns - 4
    if (width > len(rawText)):
        width = len(rawText)
    emptyLine = (width + 3) * ' '

    print(colors.WARNING_BOX, emptyLine)

    while rawText != '':
        line = rawText[:width]
        rawText = rawText[width:]
        print('  ' + line.ljust(width + 2))

    print(emptyLine, colors.END_BOX)


def processPackage(meta, version):
    package = meta['info']['name']
    if not version:
        version = meta['info']['version']

    releases = meta['releases'].keys()
    if version not in releases:
        printWarning("Could not find package %s at version %s" %
                     (package, version))
        print('Please choose one of the following versions:\n%s' %
              (', '.join(releases)))
        return

    updateJson(package, version)
    release = meta['releases'][version]

    for meta in reversed(release):
        if (meta['packagetype'] == 'sdist'):
            downloadUrl = meta['url']
            downloadPackage(downloadUrl, package, version)
            return


montyJson = './monty.json'


def updateJson(package, version):
    if os.path.isfile(montyJson):
        f = open(montyJson)
        data = json.loads(f.read())
        f.close()
    else:
        data = json.loads('{"require": {}}')

    data['require'][package] = version

    with open(montyJson, 'w+') as f:
        json.dump(data, f, indent=4)


vendorDir = './vendor'


def downloadPackage(url, packageName, version):
    with tempfile.TemporaryDirectory() as tmpdirname:
        resp = urllib.request.urlopen(url)
        zipfile = ZipFile(BytesIO(resp.read()))
        zipfile.extractall(tmpdirname)

        path = os.path.join(tmpdirname, '%s-%s' % (packageName, version))
        print('export PYTHONPATH="%s/lib/python3.5/site-packages"' % path)
        os.system('python %s/setup.py install --prefix=%s' % (path, path))

        if not os.path.exists(vendorDir):
            os.mkdir(vendorDir)
            f = open(os.path.join(vendorDir, '__init__.py'), 'w+')
            f.close()

    # print(os.listdir(os.path.join(tmpdirname, '%s-%s' %
        #   (packageName, version), 'lib/python3.5/site-packages')))

    # shutil.move(os.path.join(tmpdirname, '%s-%s' %
        #  (packageName, version), 'lib/python3.5/site-packages', packageName), vendorDir)
