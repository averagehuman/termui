import re
import ast
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('termui/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


setup(
    name='termui',
    author='Gerard Flanagan',
    author_email='gmflanagan@outlook.com',
    version=version,
    url='http://github.com/averagehuman/click-termui',
    packages=find_packages(),
    description='Terminal interaction utiilities',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    cmdclass = {'test': Tox},
    tests_require=['tox'],
)
