import networkx as nx
from itertools import islice


def create_network():
    network = nx.DiGraph()

    network.add_edge("Employee_PC", "App_Server")
    network.add_edge("App_Server", "Customer_DB")
    network.add_edge("Employee_PC", "Backup_Server")
    network.add_edge("Backup_Server", "Customer_DB")
    network.add_node("Isolated_Server")

    return network


def find_all_paths(network, start, target, max_paths=20, cutoff=None):
    if start not in network:
        return {
            "success": False,
            "reason": "Start node not found",
            "paths": []
        }

    if target not in network:
        return {
            "success": False,
            "reason": "Target node not found",
            "paths": []
        }

    if (
        not isinstance(max_paths, int)
        or isinstance(max_paths, bool)
        or max_paths < 1
    ):
        return {
            "success": False,
            "reason": "max_paths must be a positive integer",
            "paths": []
        }

    if cutoff is not None and (
        not isinstance(cutoff, int)
        or isinstance(cutoff, bool)
        or cutoff < 0
    ):
        return {
            "success": False,
            "reason": "cutoff must be a non-negative integer",
            "paths": []
        }

    if start == target:
        return {
            "success": True,
            "paths": [[start]],
            "count": 1,
            "truncated": False,
            "reason": "Start and target are the same node"
        }

    if cutoff is None:
        cutoff = max(0, len(network.nodes) - 1)

    path_generator = nx.all_simple_paths(
        network,
        source=start,
        target=target,
        cutoff=cutoff
    )

    collected = list(islice(path_generator, max_paths + 1))
    truncated = len(collected) > max_paths
    paths = collected[:max_paths]

    if not paths:
        return {
            "success": False,
            "paths": [],
            "count": 0,
            "truncated": False,
            "reason": "No path exists within the cutoff"
        }

    return {
        "success": True,
        "paths": paths,
        "count": len(paths),
        "truncated": truncated,
        "reason": (
            "Path limit reached; more paths may exist"
            if truncated else None
        )
    }


def simulate_detailed_path(
    network,
    start,
    target,
    available_privileges=None
):
    trace = []

    if available_privileges is None:
        available_privileges = []

    if start not in network:
        return {
            "success": False,
            "path": [],
            "steps": 0,
            "trace": trace,
            "reason": "Start node not found"
        }

    if target not in network:
        return {
            "success": False,
            "path": [],
            "steps": 0,
            "trace": trace,
            "reason": "Target node not found"
        }

    if start == target:
        return {
            "success": True,
            "path": [start],
            "steps": 0,
            "trace": trace,
            "reason": "Start and target are the same node"
        }

    paths = nx.all_simple_paths(
        network,
        source=start,
        target=target,
        cutoff=max(0, len(network.nodes) - 1)
    )

    checked_paths = 0

    for path in paths:
        if checked_paths >= 100:
            break

        checked_paths += 1
        candidate_trace = []
        path_valid = True

        for i in range(len(path) - 1):
            source = path[i]
            target_node = path[i + 1]

            edge_data = network.get_edge_data(
                source,
                target_node
            ) or {}

            if edge_data.get("enabled", True) is False:
                candidate_trace.append({
                    "from": source,
                    "to": target_node,
                    "status": "rejected",
                    "reason": "Connection is disabled"
                })
                path_valid = False
                break

            required_privilege = edge_data.get("required_privilege")

            if (
                required_privilege is not None
                and required_privilege not in available_privileges
            ):
                candidate_trace.append({
                    "from": source,
                    "to": target_node,
                    "status": "rejected",
                    "reason": (
                        f"Missing required privilege: "
                        f"{required_privilege}"
                    )
                })
                path_valid = False
                break

            candidate_trace.append({
                "from": source,
                "to": target_node,
                "status": "accepted",
                "reason": "Transition conditions satisfied"
            })

        trace.extend(candidate_trace)

        if path_valid:
            return {
                "success": True,
                "path": path,
                "steps": len(path) - 1,
                "trace": trace,
                "reason": "Target reached successfully"
            }

    return {
        "success": False,
        "path": [],
        "steps": 0,
        "trace": trace,
        "reason": (
            "No valid path exists"
            if checked_paths > 0
            else "No path exists in the network"
        )
    }