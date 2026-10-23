const $ = (id) => document.getElementById(id);
let network = null;
let currentData = null;

function safeText(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[ch]));
}
function updateClock() {
  $("clock").textContent = new Date().toLocaleTimeString("en-GB", {hour12:false});
}
function renderInventory(data) {
  const rows = data.nodes.map(node => {
    const d = node.details || {};
    const isolated = node.group === "isolated";
    return `<tr data-node="${safeText(node.id)}">
      <td><div class="asset-name"><span class="asset-mini">${isolated ? "◇" : "▦"}</span><b>${safeText(node.id)}</b></div></td>
      <td class="role-tag">${isolated ? "Isolated node" : "Network asset"}</td>
      <td>${d.degree ?? 0}</td>
      <td><span class="status-badge ${isolated ? "status-isolated" : "status-connected"}">${isolated ? "ISOLATED" : "CONNECTED"}</span></td>
    </tr>`;
  }).join("");
  $("asset-rows").innerHTML = rows || '<tr><td colspan="4" class="table-empty">No assets in the current model.</td></tr>';
  $("inventory-count").textContent = `${data.nodes.length} ASSETS`;
  document.querySelectorAll("#asset-rows tr[data-node]").forEach(row => {
    row.addEventListener("click", () => selectNode(row.dataset.node));
  });
}
function selectNode(id) {
  if (!currentData) return;
  const node = currentData.nodes.find(n => n.id === id);
  if (!node) return;
  const d = node.details || {};
  $("empty-inspector").hidden = true;
  $("asset-inspector").hidden = false;
  $("selected-name").textContent = node.id;
  $("selected-id").textContent = node.id;
  $("selected-degree").textContent = d.degree ?? 0;
  $("selected-in").textContent = d.in_degree ?? "N/A";
  $("selected-out").textContent = d.out_degree ?? "N/A";
  const isolated = node.group === "isolated";
  $("asset-state").textContent = isolated ? "ISOLATED" : "CONNECTED";
  $("asset-state").className = `state-chip${isolated ? " state-isolated" : ""}`;
  $("selected-context").textContent = isolated
    ? "This asset has no direct edges in the current graph. Verify whether it should be connected or intentionally segmented."
    : "This asset participates in the current network graph. Connectivity alone does not prove an exploitable attack path.";
  if (network) network.selectNodes([id]);
}
async function loadNetwork() {
  $("engine-status").textContent = "Loading model…";
  $("model-state").textContent = "CONNECTING";
  try {
    const response = await fetch("/api/network", {cache:"no-store"});
    const data = await response.json();
    if (!response.ok || data.error) throw new Error(data.error || "Network API request failed");
    currentData = data;
    $("asset-count").textContent = data.summary.assets;
    $("connection-count").textContent = data.summary.connections;
    $("isolated-count").textContent = data.summary.isolated;
    $("graph-counts").textContent = `${data.summary.assets} ASSETS / ${data.summary.connections} LINKS`;
    $("engine-status").textContent = "Network model connected";
    $("model-state").textContent = "MODEL ONLINE";
    $("network").querySelector(".graph-loading")?.remove();
    renderInventory(data);
    if (typeof vis === "undefined") {
      $("network").innerHTML = '<div class="graph-loading"><b>Graph library unavailable</b><span>Check your internet connection and reload to load the graph library.</span></div><div class="graph-watermark">PATHFINDER / GRAPH ENGINE</div>';
      return;
    }
    const nodes = new vis.DataSet(data.nodes.map(n => ({
      ...n, shape:"dot", size:n.group === "isolated" ? 18 : 22,
      color: n.group === "isolated"
        ? {background:"#f4bd69",border:"#ffe0a5",highlight:{background:"#ffd58d",border:"#fff0c9"}}
        : {background:"#50e0d0",border:"#b0fff4",highlight:{background:"#8efff0",border:"#ffffff"}},
      borderWidth:2, font:{color:"#dbe9f5",size:12,face:"Manrope",strokeWidth:3,strokeColor:"#0a121e"},
      shadow:{enabled:true,color:n.group === "isolated" ? "#f4bd6940" : "#50e0d044",size:17,x:0,y:0}
    })));
    const edges = new vis.DataSet(data.edges.map((e,i) => ({
      ...e, id:i+1, color:{color:"#3d6977",highlight:"#50e0d0",hover:"#7ae8dc"},
      width:1.7, arrows:{to:{enabled:true,scaleFactor:.65}},
      smooth:{type:"dynamic",roundness:.35}
    })));
    const container = $("network");
    network = new vis.Network(container,{nodes,edges},{
      autoResize:true, interaction:{hover:true,tooltipDelay:150,hideEdgesOnDrag:false,dragNodes:true,zoomView:true},
      physics:{enabled:true,stabilization:{iterations:120,fit:true},barnesHut:{gravitationalConstant:-4200,centralGravity:.18,springLength:145,springConstant:.035,damping:.12,avoidOverlap:.7}},
      nodes:{chosen:{node:(values)=>{values.shadow=true;values.shadowSize=25;}}},
      edges:{selectionWidth:2,hoverWidth:2}
    });
    network.once("stabilizationIterationsDone",()=>network.fit({animation:{duration:450,easingFunction:"easeInOutQuad"}}));
    network.on("click", params => {
      if(params.nodes.length) selectNode(params.nodes[0]);
      else {
        $("empty-inspector").hidden = false;
        $("asset-inspector").hidden = true;
        network.unselectAll();
      }
    });
  } catch (error) {
    $("engine-status").textContent = "Model connection failed";
    $("model-state").textContent = "CONNECTION ERROR";
    $("network").innerHTML = `<div class="graph-loading"><b>Could not load network model</b><span>${safeText(error.message)}</span><span>Check that app.py is running and create_network() works.</span></div>`;
    console.error(error);
  }
}
$("fit-btn").addEventListener("click",()=>network?.fit({animation:{duration:450,easingFunction:"easeInOutQuad"}}));
$("refresh").addEventListener("click",loadNetwork);
$("search-btn").addEventListener("click",()=>{
  const q=$("node-search").value.trim().toLowerCase();
  if(!q||!currentData)return;
  const node=currentData.nodes.find(n=>n.id.toLowerCase().includes(q));
  if(node){selectNode(node.id);network?.focus(node.id,{scale:1.25,animation:{duration:500}});}
  else {$("node-search").setCustomValidity("No matching asset found");$("node-search").reportValidity();$("node-search").setCustomValidity("");}
});
$("node-search").addEventListener("keydown",e=>{if(e.key==="Enter")$("search-btn").click();});
document.querySelectorAll(".nav-item").forEach(link=>link.addEventListener("click",()=>{
  document.querySelectorAll(".nav-item").forEach(n=>n.classList.remove("active"));
  link.classList.add("active");
}));
updateClock();setInterval(updateClock,1000);loadNetwork();
