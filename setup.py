from setuptools import find_packages, setup

setup(
    name='jupyter-notebook-gist',
    use_scm_version={
        'version_scheme': 'post-release',
        'local_scheme': 'dirty-tag'
    },
    setup_requires=['setuptools_scm'],
    description='Create a gist from the Jupyter Notebook UI',
    author='Mozilla Firefox Data Platform',
    author_email='fx-data-platform@mozilla.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    license='MPL2',
    install_requires=[
        'ipython >= 4',
        'notebook >= 4.3.1',
        'jupyter',
        'requests',
        'six',
        'widgetsnbextension',
    ],
    url='https://github.com/mozilla/jupyter-notebook-gist',
    zip_safe=False,
)
