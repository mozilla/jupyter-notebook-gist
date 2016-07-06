from setuptools import find_packages, setup

setup(
    name='jupyter-notebook-gist',
    version='0.4.0',
    description='Create a gist from the Jupyter Notebook UI',
    author='Mozilla Firefox Data Platform',
    author_email='fx-data-platform@mozilla.com',
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
    url='https://github.com/mozilla/jupyter-notebook-gist',
    zip_safe=False,
)
