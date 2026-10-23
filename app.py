from flask import Flask, render_template, jsonify
from simulation_engine import create_network

app = Flask(__name__)


def network_payload():
    """Build dashboard graph data from the project's actual network model."""
    graph = create_network()

    nodes = []
    for node, attrs in graph.nodes(data=True):
        nodes.append({
            "id": str(node),
            "label": str(node).replace("_", "\n"),
            "group": "isolated" if graph.degree(node) == 0 else "asset",
            "details": {
                "type": attrs.get("type", "Network asset"),
                "degree": int(graph.degree(node)),
                "in_degree": int(graph.in_degree(node)) if graph.is_directed() else None,
                "out_degree": int(graph.out_degree(node)) if graph.is_directed() else None,
            },
        })

    edges = [
        {"from": str(source), "to": str(target), "arrows": "to"}
        for source, target in graph.edges()
    ]

    return {
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "assets": graph.number_of_nodes(),
            "connections": graph.number_of_edges(),
            "isolated": sum(1 for node in graph.nodes if graph.degree(node) == 0),
            "components": None,
        },
    }


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/network")
def api_network():
    try:
        return jsonify(network_payload())
    except Exception as exc:
        app.logger.exception("Could not load the network model")
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True)
