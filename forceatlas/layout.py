import multiprocessing as mp
import networkx as nx
import pandas as pd
import subprocess
import random

import pkg_resources
import tempfile
import os

classpath = (
    pkg_resources.resource_filename("forceatlas", "ext/forceatlas2.jar") +
    ":" +
    pkg_resources.resource_filename("forceatlas", "ext/gephi-toolkit-0.9.2-all.jar")
)

def temp_filename() -> str:
    return next(tempfile._get_candidate_names())
    
def fa2_layout(
    G,
    pos=None,
    iterations=50,
    threshold=None,
    directed=False,
    dim=2,
    splits=None,
    theta=1.2,
    update_iter=1,
    update_center=False,
    jitter_tolerance=1,
    lin_log_mode=False,
    repulsion=None,
    gravity=1,
    strong_gravity_mode=False,
    outbound_attraction_distribution=False,
    n_jobs=mp.cpu_count(),
    seed=None,
):
    """Position nodes using ForceAtlas2 force-directed algorithm.

    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G.

    pos : dict or None  optional (default=None)
        Initial positions for nodes as a dictionary with node as keys
        and values as a coordinate list or tuple.  If None, then use
        random initial positions.

    iterations : int  optional (default=50)
        Maximum number of iterations taken

    threshold : float or None  optional (default=None)
        Threshold for relative error in node position changes.
        The iteration stops if the error is below this threshold.
        
    directed : bool (default=False)
        Whether input graph is directed.

    dim : int (default: 2)
        Dimension of layout.
        
    splits : int or None  optional (default=None)
        Rounds of splits to use for Barnes-Hut tree building.
        Number of regions after splitting is 4^barnesHutSplits for 2D
        and 8^barnesHutSplits for 3D.
        
    theta : float (default=1.2)
        Theta of the Barnes Hut optimization.
        
    update_iter : int (default=1)
        Update Barnes-Hut tree every update_iter iterations.
        
    update_center : bool (default=False)
        Update Barnes-Hut region centers when not rebuilding
        Barnes-Hut tree.
        
    jitter_tolerance : float (default=1)
        How much swinging you allow. Above 1 discouraged.
        Lower gives less speed and more precision.
        
    lin_log_mode : bool (default=False)
        Switch ForceAtlas' model from lin-lin to lin-log. 
        Makes clusters more tight.
        
    repulsion : float or None  optional (default: 1)
        How much repulsion you want. More makes a more sparse graph.
        None will default to 2.0 if nodes >= 100, otherwise 10.0.
        
    gravity : float (default=1.0)
        Attracts nodes to the center.
        
    strong_gravity_mode : bool (default=False)
        A stronger gravity law
        
    outbound_attraction_distribution : bool (default=False)
        Distributes attraction along outbound edges.
        Hubs attract less and thus are pushed to the borders.
        
    n_jobs : int  optional (defaults to all cores)
        Number of threads to use for parallel computation.
        If None, defaults to all cores as detected by
        multiprocessing.cpu_count().

    seed : int or None  optional (default=None)
        Seed for random number generation for initial node position.
        If int, `seed` is the seed used by the random number generator,
        if None, the random number generator is chosen randomly.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node

    Examples
    --------
    >>> import forceatlas as fa2
    >>> G = nx.path_graph(4)
    >>> pos = fa2.fa2_layout(G)
    """
    try:
        if not isinstance(G, nx.Graph):
            empty_graph = nx.Graph()
            empty_graph.add_nodes_from(G)
            G = empty_graph
        
        mapping = {label: index for index, label in enumerate(G.nodes())}
        inverse_mapping = {index: label for label, index in mapping.items()}
        H = nx.relabel_nodes(G, mapping)
            
        temp_graph_filename = temp_filename() + ".net"
        nx.write_pajek(H, temp_graph_filename)
        
        output_filename = temp_filename() + ".coords"
        
        command = [
                "java",
                "-Djava.awt.headless=true",
                "-Xmx8g",
                "-cp",
                classpath,
                "kco.forceatlas2.Main",
                "--input",
                temp_graph_filename,
                "--output",
                output_filename,
                "--nthreads",
                str(n_jobs),
                "--barnesHutTheta",
                str(theta),
                "--barnesHutUpdateIter",
                str(update_iter),
                "--jitterTolerance",
                str(jitter_tolerance),
                "--gravity",
                str(gravity),
        ]
        
        if dim == 2:
            command.append("--2d")
            
        if seed is not None:
            command.extend(["--seed", str(seed)])
            
        if splits is not None:
            command.extend(["--barnesHutSplits", str(splits)])
            
        if update_center:
            command.append("--updateCenter")
            
        if lin_log_mode:
            command.append("--linLogMode")
            
        if repulsion is not None:
            command.extend(["--scalingRatio", str(repulsion)])
            
        if strong_gravity_mode:
            command.append("--strongGravityMode")
        
        if outbound_attraction_distribution:
            command.append("--outboundAttractionDistribution")
            
        if directed:
            command.append("--directed")
            
        if threshold is None:
            command.extend(["--nsteps", str(iterations)])
        else:
            command.extend([
                "--targetChangePerNode",
                str(threshold),
                "--targetSteps",
                str(iterations),
            ])
            
        if pos is not None:
            temp_pos_filename = temp_filename() + ".csv"
            pos_list = []
            for label, coords in pos.items():
                row = {"id": mapping[label], "x": coords[0], "y": coords[1]}
                if dim == 3:
                    row["z"] = coords[2]
                pos_list.append(row)
            pos_list = pd.DataFrame(pos_list)
            pos_list.to_csv(temp_pos_filename, sep='\t')
            command.extend(["--coords", temp_pos_filename])
            
        subprocess.check_call(command)
        
        coordinates = pd.read_csv(output_filename + ".txt", header=0, index_col=0, sep="\t").values
        
        if pos is not None:
            os.remove(temp_pos_filename)
            
        os.remove(temp_graph_filename)
        os.remove(output_filename + ".txt")
        
        if os.path.exists(output_filename + ".distances.txt"):
            os.remove(output_filename + ".distances.txt")
        
        pos = {inverse_mapping[i]: x for i, x in enumerate(coordinates)}
        
        return pos
    except Exception as e:
        raise e
    finally:
        for path in [temp_graph_filename, output_filename + ".txt", output_filename + ".distances.txt"]:
            if os.path.exists(path):
                os.remove(path)
                
        while True:
            try:
                os.remove(temp_pos_filename)
                break
            except KeyboardInterrupt:
                continue
            except:
                break
            