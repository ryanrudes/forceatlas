# Gephi ForceAtlas2

[![PyPI download month](https://img.shields.io/pypi/dm/forceatlas.svg)](https://pypi.python.org/pypi/forceatlas/)
[![PyPI - Status](https://img.shields.io/pypi/status/forceatlas)](https://pypi.python.org/pypi/forceatlas/)
[![PyPI](https://img.shields.io/pypi/v/forceatlas)](https://pypi.python.org/pypi/forceatlas/)
![GitHub](https://img.shields.io/github/license/ryanrudes/forceatlas)

This package is a Python-friendly port of the multithreaded [Java implementation](https://github.com/klarman-cell-observatory/forceatlas2) of the Gephi ForceAtlas2 layout algorithm. It is compatible with [networkx](https://github.com/networkx/networkx) and supports both 2D and 3D layout.

## Installation
It can be installed with the default Python package manager via the command

```
pip install forceatlas
```

## Example
The package is consistent with networkx in documentation-style and function arguments. See the documentation for more details.
```python
import matplotlib.pyplot as plt
import forceatlas as fa2
import networkx as nx

G = nx.fast_gnp_random_graph(100, 0.1)
pos = fa2.fa2_layout(G, iterations = 10000, threshold = 1e-3)

nx.draw(G)
plt.savefig("graph.png")
```
