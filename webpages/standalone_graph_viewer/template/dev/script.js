const dataManager = new DataManager();
const renderer = new Renderer(dataManager);

const default_nodesData = parseCSV(default_nodes_str);
const default_edgesData = parseCSV(default_edges_str);
default_metadata = JSON.parse(default_metadata_str);

console.info("Def Nodes:\n",default_nodesData);
console.info("Def Edges:\n",default_edgesData);

const defaultGraphData = buildGraphJSON(default_nodesData, default_edgesData, default_metadata);

console.log(JSON.stringify(defaultGraphData, null, 2));

dataManager.loadGraphData(defaultGraphData);
renderer.renderNodeTypes(true);
renderMetadataLegend(dataManager);