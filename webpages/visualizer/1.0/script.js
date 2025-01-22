const dataManager = new DataManager();
const renderer = new Renderer(dataManager);

const default_nodes_str = `id,label,type
0,AAA|0|1|2,aaa
1,BBB|0,bbb
2,CCC|0,bbb
3,BB1|0,bbb|ccc
4,BB2|0,aaa|bbb|ccc
5,DDD|0,ddd
6,XXX|0,xxx`;

const default_edges_str = `source,target,label
0,1,connected_to|0
0,1,has|0
1,3,connected_to|0
3,4,contains|0
4,2,has|0
2,5,connected_to|0
5,4,connected_to|0|1`;


const default_metadata_str = `[
  { "index": 0, "filename": "aaa.pdf", "sha256": "0000000" },
  { "index": 1, "filename": "bbb.pdf", "sha256": "0000000" },
  { "index": 2, "filename": "ccc.pdf", "sha256": "0000000" }
]`;

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