import networkx as nx
def add_asset(
    network,
    asset_name,
    asset_type="unknown",
    criticality="medium",
    **attributes
):
    """Add a validated asset to the network."""
    if not isinstance(network, nx.DiGraph):
        return {"success": False, "reason": "Network must be a directed graph"}
    if not isinstance(asset_name, str) or not asset_name.strip():
        return {"success": False, "reason": "Asset name must be a non-empty string"}
    asset_name = asset_name.strip()
    if asset_name in network:
        return {"success": False, "reason": "Asset already exists"}
    if not isinstance(asset_type, str) or not asset_type.strip():
        return {"success": False, "reason": "Asset type must be a non-empty string"}
    if criticality not in {"low", "medium", "high", "critical"}:
        return {
            "success": False,
            "reason": "Criticality must be low, medium, high, or critical"
        }
    if "asset_type" in attributes or "criticality" in attributes:
        return {
            "success": False,
            "reason": "Reserved asset properties cannot be overridden"
        }
    network.add_node(
        asset_name,
        asset_type=asset_type.strip(),
        criticality=criticality,
        **attributes
    )
    return {
        "success": True,
        "asset": asset_name,
        "reason": "Asset added successfully"
    }
def remove_asset(network, asset_name):
    """Remove an asset and its connected edges."""
    if asset_name not in network:
        return {"success": False, "reason": "Asset not found"}
    network.remove_node(asset_name)
    return {
        "success": True,
        "asset": asset_name,
        "reason": "Asset removed successfully"
    }
def add_connection(
    network,
    source,
    target,
    enabled=True,
    required_privilege=None,
    **attributes
):
    """Add a validated directed connection between two assets."""
    if not isinstance(network, nx.DiGraph):
        return {"success": False, "reason": "Network must be a directed graph"}
    if source not in network:
        return {"success": False, "reason": f"Source asset not found: {source}"}
    if target not in network:
        return {"success": False, "reason": f"Target asset not found: {target}"}
    if source == target:
        return {"success": False, "reason": "An asset cannot connect to itself"}
    if network.has_edge(source, target):
        return {"success": False, "reason": "Connection already exists"}
    if not isinstance(enabled, bool):
        return {"success": False, "reason": "Enabled must be True or False"}
    if required_privilege is not None and (
        not isinstance(required_privilege, str)
        or not required_privilege.strip()
    ):
        return {
            "success": False,
            "reason": "Required privilege must be a non-empty string or None"
        }
    if "enabled" in attributes or "required_privilege" in attributes:
        return {
            "success": False,
            "reason": "Reserved connection properties cannot be overridden"
        }
    network.add_edge(
        source,
        target,
        enabled=enabled,
        required_privilege=required_privilege,
        **attributes
    )
    return {
        "success": True,
        "source": source,
        "target": target,
        "reason": "Connection added successfully"
    }
def remove_connection(network, source, target):
    """Remove a connection between two assets."""
    if not network.has_edge(source, target):
        return {"success": False, "reason": "Connection not found"}
    network.remove_edge(source, target)
    return {
        "success": True,
        "source": source,
        "target": target,
        "reason": "Connection removed successfully"
    }
def get_isolated_assets(network):
    """Return assets with no incoming or outgoing connections."""
    return [
        asset for asset in network.nodes
        if network.degree(asset) == 0
    ]
def get_asset_details(network, asset_name):
    """Return an asset's properties and its connections."""
    if asset_name not in network:
        return {"success": False, "reason": "Asset not found"}
    return {
        "success": True,
        "asset": asset_name,
        "properties": dict(network.nodes[asset_name]),
        "incoming_connections": list(network.predecessors(asset_name)),
        "outgoing_connections": list(network.successors(asset_name))
    }
def get_graph_summary(network):
    """Return a summary of the network topology."""
    return {
        "asset_count": network.number_of_nodes(),
        "connection_count": network.number_of_edges(),
        "assets": list(network.nodes),
        "isolated_assets": get_isolated_assets(network)
    }
def is_reachable(network, source, target):
    """Check whether a directed path exists between two assets."""
    if source not in network:
        return {
            "success": False,
            "reachable": False,
            "reason": f"Source asset not found: {source}"
        }
    if target not in network:
        return {
            "success": False,
            "reachable": False,
            "reason": f"Target asset not found: {target}"
        }
    reachable = nx.has_path(network, source, target)
    return {
        "success": True,
        "reachable": reachable,
        "reason": "A directed path exists" if reachable else "No directed path exists"
    }
def get_reachable_assets(network, start):
    """Return all assets reachable from a starting asset."""
    if start not in network:
        return {
            "success": False,
            "start": start,
            "assets": [],
            "reason": f"Starting asset not found: {start}"
        }
    reachable_assets = list(nx.descendants(network, start))
    return {
        "success": True,
        "start": start,
        "assets": reachable_assets,
        "count": len(reachable_assets),
        "reason": "Reachable assets retrieved successfully"
    }
def get_weakly_connected_components(network):
    """Group assets connected when edge directions are ignored."""
    components = [
        list(component)
        for component in nx.weakly_connected_components(network)
    ]
    return {
        "success": True,
        "components": components,
        "count": len(components),
        "reason": "Network components analyzed successfully"
    }