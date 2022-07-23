from distutils.core import setup

setup(
   name = 'forceatlas',
   packages = ['forceatlas'],
   version = '0.1.0',
   license = 'GPLv3+',
   description = 'Python-friendly ForceAtlas2 library with networkx compatibility and support for thread-based parallelism',
   author = 'Ryan Rudes',
   author_email = 'ryanrudes@gmail.com',
   url = 'https://github.com/ryanrudes/forceatlas',
   download_url = 'https://github.com/ryanrudes/forceatlas/archive/refs/tags/v0.1.0.tar.gz',
   keywords = ['multithreading', 'networkx', 'forceatlas2', 'graph-layout', 'force-directed-graphs'],
   install_requires = ['networkx', 'pandas']
)
