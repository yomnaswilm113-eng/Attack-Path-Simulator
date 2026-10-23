from simulation_engine import create_network, simulate_detailed_path
from graph_module import (
    add_asset,
    remove_asset,
    add_connection,
    remove_connection,
    get_isolated_assets,
    get_asset_details,
    get_graph_summary,
    is_reachable,
    get_reachable_assets,
    get_weakly_connected_components
)
# Test 1: All paths are blocked
network = create_network()
network["App_Server"]["Customer_DB"]["enabled"] = False
network["Backup_Server"]["Customer_DB"]["enabled"] = False

result = simulate_detailed_path(
    network, "Employee_PC", "Customer_DB"
)

assert result["success"] is False
assert result["reason"] == "No valid path exists"
print("Test 1 passed: All paths blocked")


# Test 2: Target does not exist
network = create_network()

result = simulate_detailed_path(
    network, "Employee_PC", "Unknown_Server"
)

assert result["success"] is False
assert result["reason"] == "Target node not found"
print("Test 2 passed: Invalid target")


# Test 3: Start and target are the same
network = create_network()

result = simulate_detailed_path(
    network, "Employee_PC", "Employee_PC"
)

assert result["success"] is True
assert result["steps"] == 0
print("Test 3 passed: Same start and target")


# Test 4: Missing privilege, alternative path succeeds
network = create_network()
network["App_Server"]["Customer_DB"]["required_privilege"] = "admin"

result = simulate_detailed_path(
    network,
    "Employee_PC",
    "Customer_DB",
    available_privileges=[]
)

assert result["success"] is True
assert result["path"] == [
    "Employee_PC", "Backup_Server", "Customer_DB"
]
assert any(
    item["status"] == "rejected"
    and "privilege" in item["reason"].lower()
    for item in result["trace"]
)
print("Test 4 passed: Privilege check and alternative path")


print("\nAll 4 tests passed successfully!")
print("\n--- Graph Module Tests ---")

network = create_network()

# Test 5: Add a new asset
result = add_asset(
    network,
    "Web_Server",
    asset_type="server",
    criticality="high"
)
assert result["success"] is True
assert "Web_Server" in network
print("Test 5 passed: Add asset")

# Test 6: Reject a duplicate asset
result = add_asset(network, "Web_Server")
assert result["success"] is False
print("Test 6 passed: Reject duplicate asset")

# Test 7: Add a connection
result = add_connection(
    network,
    "Employee_PC",
    "Web_Server",
    required_privilege="admin"
)
assert result["success"] is True
assert network.has_edge("Employee_PC", "Web_Server")
print("Test 7 passed: Add connection")

# Test 8: Reject a connection to a missing asset
result = add_connection(
    network,
    "Employee_PC",
    "Unknown_Server"
)
assert result["success"] is False
print("Test 8 passed: Reject invalid connection")

# Test 9: Get asset details
result = get_asset_details(network, "Web_Server")
assert result["success"] is True
assert result["properties"]["asset_type"] == "server"
assert result["incoming_connections"] == ["Employee_PC"]
print("Test 9 passed: Get asset details")

# Test 10: Find isolated assets
isolated = get_isolated_assets(network)
assert "Isolated_Server" in isolated
print("Test 10 passed: Find isolated assets")

# Test 11: Get graph summary
summary = get_graph_summary(network)
assert summary["asset_count"] == 6
assert summary["connection_count"] == 5
print("Test 11 passed: Graph summary")

# Test 12: Remove a connection
result = remove_connection(
    network,
    "Employee_PC",
    "Web_Server"
)
assert result["success"] is True
assert not network.has_edge("Employee_PC", "Web_Server")
print("Test 12 passed: Remove connection")

# Test 13: Remove an asset
result = remove_asset(network, "Web_Server")
assert result["success"] is True
assert "Web_Server" not in network
print("Test 13 passed: Remove asset")

print("\nAll Graph Module tests passed!")
print("\n--- Topology Analysis Tests ---")

network = create_network()

# Test 14: Check if a directed path exists
result = is_reachable(
    network, "Employee_PC", "Customer_DB"
)
assert result["success"] is True
assert result["reachable"] is True
print("Test 14 passed: Directed path exists")

# Test 15: Check the reverse direction
result = is_reachable(
    network, "Customer_DB", "Employee_PC"
)
assert result["success"] is True
assert result["reachable"] is False
print("Test 15 passed: Direction is respected")

# Test 16: Get all reachable assets
result = get_reachable_assets(
    network, "Employee_PC"
)
assert result["success"] is True
assert set(result["assets"]) == {
    "App_Server",
    "Backup_Server",
    "Customer_DB"
}
assert result["count"] == 3
print("Test 16 passed: Reachable assets")

# Test 17: Analyze connected components
result = get_weakly_connected_components(network)
assert result["success"] is True
assert result["count"] == 2

components = [
    set(component)
    for component in result["components"]
]

assert {"Employee_PC", "App_Server", "Backup_Server", "Customer_DB"} in components
assert {"Isolated_Server"} in components
print("Test 17 passed: Connected components")

print("\nAll Topology Analysis tests passed!")
print("\n--- Asset Validation Tests ---")

network = create_network()

# Test 18: Reject an empty asset name
result = add_asset(network, "   ")
assert result["success"] is False
assert "name" in result["reason"].lower()
print("Test 18 passed: Empty asset name rejected")

# Test 19: Reject an empty asset type
result = add_asset(network, "New_Server", asset_type=" ")
assert result["success"] is False
print("Test 19 passed: Empty asset type rejected")

# Test 20: Reject an invalid criticality
result = add_asset(
    network,
    "New_Server",
    criticality="extreme"
)
assert result["success"] is False
print("Test 20 passed: Invalid criticality rejected")

# Test 21: Accept a valid criticality
# Test 21: Accept a valid criticality
result = add_asset(
    network,
    "Critical_Server",
    asset_type="server",
    criticality="critical"
)
assert result["success"] is True
assert network.nodes["Critical_Server"]["criticality"] == "critical"
print("Test 21 passed: Valid asset accepted")

print("\nAll Asset Validation tests passed!")
