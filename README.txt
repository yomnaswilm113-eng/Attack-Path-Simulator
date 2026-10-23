PATHFINDER dashboard replacement files

1. Copy app.py into your existing Attackpathsimulator project folder, replacing its old app.py.
2. Copy the templates folder's index.html into your existing templates folder, replacing the old index.html.
3. Copy the static folder (style.css and app.js) into your existing project folder. If a static folder already exists, replace these two files only.
4. Keep graph_module.py and simulation_engine.py and all other existing project files unchanged.
5. In the VS Code terminal, stop the old Flask server with Ctrl+C.
6. Run: python app.py
7. Open: http://127.0.0.1:5000

This dashboard reads the network graph from simulation_engine.create_network() via /api/network.
Vulnerability findings and risk score are intentionally marked as pending until real assessment data is integrated.
The interactive graph uses the vis-network CDN and therefore needs internet access to load that library.
