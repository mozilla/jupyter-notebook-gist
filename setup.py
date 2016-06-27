import sys
from setuptools import find_packages, setup

tests_require = [
    'coverage>=4.0',
    'pytest-isort',
    'pytest-cache>=1.0',
    'flake8<3.0.0',
    'pytest-flake8>=0.5',
    'pytest>=2.8.0',
    'pytest-wholenodeid',
]

needs_pytest = set(['pytest', 'test', 'ptr']).intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []


setup(
    name='jupyter-notebook-gist',
    version='0.4a1',
    description='Create a gist from the Jupyter Notebook UI',
    author='Mozilla Telemetry',
    author_email='telemetry@lists.mozilla.org',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    license='MPL2',
    install_requires=[
        'ipython >= 4',
        'notebook >= 4.2',
        'jupyter',
        'requests',
        'widgetsnbextension',
    ],
    setup_requires=[] + pytest_runner,
    tests_require=tests_require,
    url='https://github.com/mozilla/jupyter-notebook-gist',
    zip_safe=False,
)
