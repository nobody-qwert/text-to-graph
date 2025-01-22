class DataManager {
    constructor() {
        this.graphData = {};
        this.nodeMap = null;

        /*------------------------------------------------*/

        this.operation_mode = 2;
        this.showNodeTypes = false;
        this.showRootDistance = false;
        this.max_distance_threshold = 1;
        this.DirectionMode = 3;

        /*------------------------------------------------*/

        this.nodeTypes = [];
        this.nodeTypes_Filtered = [];
        this.nodeTypeFilter = {};
        this.nodeTypeCounts = {};
        this.nodeLabelToNodeTypeMap = new Map();

        this.typeFiltered_NodeLabels = [];
        this.nodeFilter = {};
        this.nodeLabelEdgeCounts = {};
        this.typeFilteringNodes_Enabled = true;

        this.selectedNodesFiltered_EdgeLabels = [];
        this.edgeFilter = {};
        this.selectedNodesFiltered_EdgeLabelCounts = {};
        this.nodeFilteringEdges_Enabled = true;

        /*------------------------------------------------*/

        this.typeColorMap = {};

        this.input_NodeTypes = '';
        this.input_NodeLabels = '';
        this.input_EdgeLabels = '';

        this.nodeTypeSortOrder = 'count';
        this.nodeLabelSortOrder = 'count';
        this.edgeLabelSortOrder = 'count';
    }

    generateColor(type) {
        if (!this.typeColorMap[type]) {
            const hue = Object.keys(this.typeColorMap).length * 137.5 % 360; // Ensures different hues
            this.typeColorMap[type] = `hsl(${hue}, 70%, 50%)`; // Generate color in HSL
        }
        return this.typeColorMap[type];
    }

    loadGraphData(data) {
        this.graphData = data;

        console.log("Graph Data\n", dataManager.graphData)

        this.sanitizeGraphData();

        this.nodeMap = new Map();
        this.graphData.nodes.forEach(node => {this.nodeMap.set(node.id, node);});

        /*------------------------------------------------*/

        this.max_distance_threshold = 1;
        const slider = document.getElementById('valueSlider');
        slider.value = this.max_distance_threshold;
        slider.dispatchEvent(new Event("input"));

        this.DirectionMode = 3;

        /*------------------------------------------------*/

        this.nodeTypes = [];
        this.nodeTypeFilter = {};
        this.nodeTypeCounts = {};

        this.nodeLabels = null;
        this.typeFiltered_NodeLabels = [];
        this.nodeFilter = {};
        this.nodeLabelEdgeCounts = {};
        this.typeFilteringNodes_Enabled = true;

        this.selectedNodesFiltered_EdgeLabels = [];
        this.all_edgeLabels = [];
        this.edgeFilter = {};
        this.selectedNodesFiltered_EdgeLabelCounts = {};
        this.nodeFilteringEdges_Enabled = true;

        /*------------------------------------------------*/

        this.typeColorMap = {};

        this.input_NodeTypes = '';
        this.input_NodeLabels = '';
        this.input_EdgeLabels = '';

        this.nodeTypeSortOrder = 'count';
        this.nodeLabelSortOrder = 'count';
        this.edgeLabelSortOrder = 'count';

        /*----------------------------------------------------------------------------*/

        this.graphData.nodes.forEach(node => {
            node.type.forEach(t => {
                this.nodeTypeCounts[t] = (this.nodeTypeCounts[t] || 0) + 1;
            });
        });

        this.nodeTypes = Object.keys(this.nodeTypeCounts).map(type => ({ type }));

        /*----------------------------------------------------------------------------*/

        this.nodeLabelToNodeTypeMap = this.graphData.nodes.reduce((map, node) => {
            map[node.label] = node.type;
            return map;
        }, {});

        /*----------------------------------------------------------------------------*/

        this.computeNodeLabelEdgeCounts();

        /*----------------------------------------------------------------------------*/

        const edgeLabelCounts = this.graphData.edges.reduce((acc, edge) => {
            acc[edge.label] = (acc[edge.label] || 0) + 1;
            return acc;
        }, {});

        const all_edgeLabels = Object.keys(edgeLabelCounts).map(label => ({ label }));

        /*----------------------------------------------------------------------------*/

        this.setInitialFilter();
        this.updateNodeTypeFilter();
    }

    setInitialFilter() {
        const nodeTypes = this.nodeTypes;
        if (nodeTypes.length === 0) {
            return;
        }

        if (this.all_edgeLabels.length === 0) {
            return;
        }

        let counts = this.nodeTypeCounts;
        nodeTypes.sort((a, b) => (counts[b.type] || 0) - (counts[a.type] || 0));
        this.nodeTypeFilter[nodeTypes[3].type] = true;

        /*---------------------------------------------------------------------------------------*/
        let nodes_FilteredBy_Type = this.graphData.nodes;

        if (this.typeFilteringNodes_Enabled) {
            const selectedNodeTypes = this.getSelectedNodeTypes();

            nodes_FilteredBy_Type = nodes_FilteredBy_Type.filter(node =>
                selectedNodeTypes.includes(node.type)
            );
        }

        let nodeLabels = nodes_FilteredBy_Type.map(node => node.label);
        if (nodeLabels.length === 0) {
            console.error("setInitialFilter() - This shuld never happen!");
        }

        counts = this.nodeLabelEdgeCounts;
        nodeLabels.sort((a, b) => (counts[b] || 0) - (counts[a] || 0));

        nodeLabels.forEach((label) => {
            this.nodeFilter[label] = true;
        });

        /*------------------------------------------------------------------*/

        let selectedNodes = null;

        if (this.nodeFilteringEdges_Enabled) {
             selectedNodes = this.getSelectedNodes();
        } else {
             selectedNodes = this.graphData.nodes;
        }

        const selectedNodesId_Set = new Set(selectedNodes.map(node => node.id));

        const edges_FilteredBy_SelectedNodes = this.graphData.edges.filter(edge =>
            selectedNodesId_Set.has(edge.source) || selectedNodesId_Set.has(edge.target)
        );

        counts = edges_FilteredBy_SelectedNodes.reduce((acc, edge) => {
            acc[edge.label] = (acc[edge.label] || 0) + 1;
            return acc;
        }, {});

        let edgeLabels = Object.keys(counts).map(label => ({ label }));

        edgeLabels.sort((a, b) => (counts[b.label] || 0) - (counts[a.label] || 0));

        console.info("###",edgeLabels);
        console.info("#########################", edgeLabels[0].label, this.edgeFilter);
        this.edgeFilter[edgeLabels[0].label] = true;
    }

    sanitizeGraphData() {
        const validNodes = this.graphData.nodes.filter(node => {
            if (Number.isNaN(node.id)) {
                console.warn('Removing node without id:', node);
                return false;
            }
            if (!node.label) {
                console.warn('Removing node without label:', node);
                return false;
            }
            if (!node.type) {
                console.warn('Removing node without type:', node);
                return false;
            }
            return true;
        });

        const validNodeIds = new Set(validNodes.map(node => node.id));

        const nodeLabelCounts = validNodes.reduce((acc, node) => {
            acc[node.label] = (acc[node.label] || 0) + 1;
            return acc;
        }, {});

        const duplicates = Object.entries(nodeLabelCounts).filter(([label, count]) => count > 1);
        if (duplicates.length > 0) {
            console.error('Duplicate node labels found (case-insensitive):', duplicates.map(([label]) => label));
            throw new Error('Sanitization aborted due to duplicate node labels.');
        }

        console.info('valid nodes ids: ', validNodeIds);
        const validEdges = this.graphData.edges.filter(edge => {
            if (Number.isNaN(edge.source)) {
                console.warn('Removing edge with non number source:', edge);
                return false;
            }
            if (!validNodeIds.has(edge.source)) {
                console.warn('Removing edge with invalid source:', edge);
                return false;
            }
            if (Number.isNaN(edge.target) || !validNodeIds.has(edge.target)) {
                console.warn('Removing edge with invalid target:', edge);
                return false;
            }
            if (!edge.label) {
                console.warn('Removing edge without label:', edge);
                return false;
            }
            return true;
        });

        this.graphData.nodes = validNodes;
        this.graphData.edges = validEdges;

        console.info('Graph data sanitized. Remaining nodes:', validNodes.length, 'Remaining edges:', validEdges.length);
    }


    setNodeTypeSortOrder(order) {
        this.nodeTypeSortOrder = order;
    }

    setNodeLabelSortOrder(order) {
        this.nodeLabelSortOrder = order;
    }

    setEdgeLabelSortOrder(order) {
        this.edgeLabelSortOrder = order;
    }

    updateNodeTypeFilter(resetTo = null) {
        console.info("--> updateNodeTypeFilter()");

        if (this.typeFilteringNodes_Enabled) {
            this.nodeTypes_Filtered = this.nodeTypes;

            const filterValue = this.input_NodeTypes.toLowerCase();
            if (filterValue.length > 0) {
                this.nodeTypes_Filtered = this.nodeTypes_Filtered.filter(({ type }) => type.toLowerCase().includes(filterValue));
            }

            console.info("--> updateNodeTypeFilter() - this.nodeTypes_Filtered:", this.nodeTypes_Filtered.length);

            this.nodeTypeFilter = this.nodeTypeFilter || {};

            this.nodeTypes_Filtered.forEach(({ type }) => {
                if (resetTo !== null) {
                    this.nodeTypeFilter[type] = resetTo;
                } else {
                    this.nodeTypeFilter[type] = (this.nodeTypeFilter[type] !== undefined) ? this.nodeTypeFilter[type] : false;
                }
            });
        }

        this.updateNodeLabelFilter();
    }

    updateNodeLabelFilter(resetTo = null) {
        console.info("--> updateNodeLabelFilter() - ", this.typeFilteringNodes_Enabled)

        let nodes_FilteredBy_Type = this.graphData.nodes;

        if (this.typeFilteringNodes_Enabled) {
            const selectedNodeTypes = this.getSelectedNodeTypes();

            nodes_FilteredBy_Type = nodes_FilteredBy_Type.filter(node =>
                node.type.some(t => selectedNodeTypes.includes(t))
            );
        }

        this.typeFiltered_NodeLabels = nodes_FilteredBy_Type.map(node => node.label);

        const filterValue = this.input_NodeLabels.toLowerCase();
        if (filterValue.length > 0) {
            this.typeFiltered_NodeLabels = this.typeFiltered_NodeLabels.filter( label => label.toLowerCase().includes(filterValue));
        }

        this.nodeFilter = this.nodeFilter || {};
        this.typeFiltered_NodeLabels.forEach( label => {
            if (resetTo !== null) {
                this.nodeFilter[label] = resetTo;
            } else {
                this.nodeFilter[label] = (this.nodeFilter[label] !== undefined) ? this.nodeFilter[label] : false;
            }
        });

        this.updateEdgeLabelFilter();
    }

    updateEdgeLabelFilter(resetTo = null) {
        console.info("--> updateEdgeLabelFilter()");

        let selectedNodes = null;

        if (this.nodeFilteringEdges_Enabled && this.operation_mode!==2) {
             selectedNodes = this.getSelectedNodes();
             console.info("selectedNodes1", selectedNodes);
        } else {
             selectedNodes = this.graphData.nodes;
             console.info("selectedNodes2", selectedNodes);
        }

        const selectedNodesId_Set = new Set(selectedNodes.map(node => node.id));

        const edges_FilteredBy_SelectedNodes = this.graphData.edges.filter(edge =>
            selectedNodesId_Set.has(edge.source) || selectedNodesId_Set.has(edge.target)
        );

        this.selectedNodesFiltered_EdgeLabelCounts = edges_FilteredBy_SelectedNodes.reduce((acc, edge) => {
            acc[edge.label] = (acc[edge.label] || 0) + 1;
            return acc;
        }, {});

        this.selectedNodesFiltered_EdgeLabels = Object.keys(this.selectedNodesFiltered_EdgeLabelCounts).map(label => ({ label }));

        const filterValue = this.input_EdgeLabels.toLowerCase();
        if (filterValue.length > 0) {
            this.selectedNodesFiltered_EdgeLabels = this.selectedNodesFiltered_EdgeLabels.filter(({ label }) => label.toLowerCase().includes(filterValue));
        }

        this.edgeFilter = this.edgeFilter || {};
        this.selectedNodesFiltered_EdgeLabels.forEach(({ label }) => {
            if (resetTo !== null) {
                this.edgeFilter[label] = resetTo;
            } else {
                this.edgeFilter[label] = (this.edgeFilter[label] !== undefined) ? this.edgeFilter[label] : false;
            }
        });

        if (this.operation_mode === 1) {
            this.calculateRootDistances();
        }
    }

    selectAllNodeTypes(selectAll) {
        this.updateNodeTypeFilter(selectAll);
    }

    selectAllNodeLabels(selectAll) {
        this.updateNodeLabelFilter(selectAll);
    }

    selectAllEdgeLabels(selectAll) {
        this.updateEdgeLabelFilter(selectAll);
    }

    /*------------------------------------------------------*/

    setInputFilterFor_NodeTypes(filter) {
        this.input_NodeTypes = filter;
        this.updateNodeTypeFilter();
    }

    setInputFilterFor_NodeLabels(filter) {
        this.input_NodeLabels = filter;
        this.updateNodeLabelFilter();
    }

    setInputFilterFor_EdgeLabels(filter) {
        this.input_EdgeLabels = filter;
        this.updateEdgeLabelFilter();
    }

    /*------------------------------------------------------*/

    toggleNodeType(type) {
        console.info("--> toggleNodeType()");
        this.nodeTypeFilter[type] = !this.nodeTypeFilter[type];
        this.updateNodeLabelFilter();
    }

    toggleNodeLabel(label) {
        console.info("--> toggleNodeLabel()");
        this.nodeFilter[label] = !this.nodeFilter[label];
        this.updateEdgeLabelFilter();
    }

    toggleEdgeLabel(label) {
        console.info("--> toggleEdgeLabel() - ", label);
        this.edgeFilter[label] = !this.edgeFilter[label];
    }

    /*------------------------------------------------------*/

    getSelectedNodeTypes() {
        return Object.keys(this.nodeTypeFilter).filter(type => this.nodeTypeFilter[type]);
    }

    getSelectedNodes() {
        return this.graphData.nodes.filter(node =>
            this.nodeFilter[node.label]
        );
    }

    computeNodeLabelEdgeCounts() {
        this.nodeLabelEdgeCounts = {};

        const edges = this.graphData.edges;

        for (let i = 0; i < edges.length; i++) {
            const edge = edges[i];

            if (!edge.source) {
                console.warn('Edge without source:', edge);
                return;
            }
            if (!edge.target) {
                console.warn('Edge without target:', edge);
                return;
            }

            const sourceNode = this.nodeMap.get(edge.source);
            const targetNode = this.nodeMap.get(edge.target);

            if (!sourceNode) {
                console.warn(`Edge with source ${edge.source} has no matching node`);
            }
            if (!targetNode) {
                console.warn(`Edge with target ${edge.target} has no matching node`);
            }

            if (sourceNode && sourceNode.label) {
                if (this.nodeLabelEdgeCounts[sourceNode.label] === undefined) {
                    this.nodeLabelEdgeCounts[sourceNode.label] = 1
                }
                else
                {
                    this.nodeLabelEdgeCounts[sourceNode.label] += 1;
                }
            }
            if (targetNode && targetNode.label) {
                if (this.nodeLabelEdgeCounts[targetNode.label] === undefined) {
                    this.nodeLabelEdgeCounts[targetNode.label] = 1;
                }
                else
                {
                    this.nodeLabelEdgeCounts[targetNode.label] += 1;
                }
            }
        };
    }

    calculateRootDistances() {
        console.info("--> calculateRootDistances()");
        const nodes = this.graphData.nodes;
        const nodeMap = this.nodeMap;

        for (let i = 0; i < nodes.length; i++) {
            nodes[i].root_distance = undefined;
        }

        const rootNodes = this.getSelectedNodes();

        for (let i = 0; i < rootNodes.length; i++) {
            rootNodes[i].root_distance = 0;
        }

        const edges = this.graphData.edges;
        const filter = this.edgeFilter;

        const OutDirectionEnabled = (this.DirectionMode & 1) > 0;
        const InDirectionEnabled = (this.DirectionMode & 2) > 0;

        console.info("OutDirection:", OutDirectionEnabled, "InDirection:", InDirectionEnabled);

        const adjacencyList = {};

        for (let i = 0; i < edges.length; i++) {
            if (!filter[edges[i].label]) {
                continue;
            }
            const edge = edges[i];
            const source = edge.source;
            const target = edge.target;

            if (!adjacencyList[source]) adjacencyList[source] = [];
            if (!adjacencyList[target]) adjacencyList[target] = [];

            if (OutDirectionEnabled) {
                adjacencyList[source].push(target);
            }
            if (InDirectionEnabled) {
                adjacencyList[target].push(source);
            }
        }

        const queue = rootNodes.slice();
        let queueStart = 0;

        while (queueStart < queue.length) {
            const currentNode = queue[queueStart++];
            const currentDistance = currentNode.root_distance;
            const neighborIds = adjacencyList[currentNode.id];

            if (!neighborIds) continue;

            for (let i = 0; i < neighborIds.length; i++) {
                const neighborId = neighborIds[i];
                const neighborNode = nodeMap.get(neighborId);
                if (neighborNode) {
                    if (neighborNode.root_distance === undefined) {
                        const newDistance = currentDistance + 1;
                        neighborNode.root_distance = newDistance;
                        queue.push(neighborNode);
                    }
                }
            }
        }

    }

    getVisibleGraph() {
        console.info("--> getVisibleGraph() - operation_mode:", this.operation_mode);
        let message = "";

        if (this.operation_mode === 0) {
            const rootNodes = this.getSelectedNodes();
            const rootNodeIds = new Set(rootNodes.map(node => node.id));

            const edgesToInclude = new Set();
            const edgeLookupMap = new Map();
            const adjacencyList = {};

            this.graphData.edges.forEach(edge => {
                if (!adjacencyList[edge.source]) adjacencyList[edge.source] = [];
                adjacencyList[edge.source].push(edge.target);

                const key = `${edge.source}-${edge.target}`;
                edgeLookupMap.set(key, edge);
            });

            let graph_size_limit_reached = false

            for (const rootNode of rootNodes) {
                if (graph_size_limit_reached) {
                    break;
                }

                const visited = new Set();
                const queue = [];
                const predecessors = {};

                visited.add(rootNode.id);
                queue.push(rootNode.id);

                while (queue.length > 0 && !graph_size_limit_reached) {
                    const currentNodeId = queue.shift();

                    if (rootNodeIds.has(currentNodeId) && currentNodeId !== rootNode.id) {
                        let pathNodeId = currentNodeId;
                        while (pathNodeId !== rootNode.id && !graph_size_limit_reached) {
                            const predNodeId = predecessors[pathNodeId];
                            const key = `${predNodeId}-${pathNodeId}`;
                            const edge = edgeLookupMap.get(key);
                            if (edge) {
                                edgesToInclude.add(edge);

                                if (edgesToInclude.size > 1500) {
                                    message = "Incomplete Graph!\nSize is limited to avoid clutter.\nSelect fewer nodes!";
                                    graph_size_limit_reached = true;
                                }
                            }
                            pathNodeId = predNodeId;
                        }
                        continue;
                    }

                    const neighbors = adjacencyList[currentNodeId] || [];
                    for (const neighborId of neighbors) {
                        if (!visited.has(neighborId) && neighborId !== rootNode.id) {
                            visited.add(neighborId);
                            predecessors[neighborId] = currentNodeId;
                            queue.push(neighborId);
                        }
                    }
                }
            }

            const mergedEdgeMap = new Map();

            edgesToInclude.forEach(edge => {
                const key = `${edge.source}-${edge.target}`;
                if (mergedEdgeMap.has(key)) {
                    const existingEdge = mergedEdgeMap.get(key);
                    existingEdge.labels.push(edge.label);
                    existingEdge.document_ids.push(...edge.document_ids);
                } else {
                    mergedEdgeMap.set(key, {
                        source: edge.source,
                        target: edge.target,
                        labels: [edge.label],
                        document_ids: [ ...edge.document_ids ]
                    });
                }
            });

            const mergedEdges = Array.from(mergedEdgeMap.values()).map(edge => ({
                source: edge.source,
                target: edge.target,
                label: edge.labels,
                document_ids: edge.document_ids
            }));

            const connectedNodeIds = new Set();
            mergedEdges.forEach(edge => {
                connectedNodeIds.add(edge.source);
                connectedNodeIds.add(edge.target);
            });

            const visibleNodes = Array.from(connectedNodeIds).map(nodeId => this.nodeMap.get(nodeId));

            if (mergedEdges.length === 0) {
                if (rootNodes.length < 2) {
                    message = "Select a few Nodes!"
                } else {
                    if (mergedEdges.length === 0) {
                        message = "No connections found ... try selecting more Nodes!"
                    }
                }
            }

            return { visibleNodes, mergedEdges, message };

        } else if (this.operation_mode === 1) {
            const max_distance_threshold = this.max_distance_threshold
            const includeOutEdge = (this.DirectionMode & 1) > 0;
            const includeInEdge = (this.DirectionMode & 2) > 0;

            console.info("includeOutEdge:", includeOutEdge, "includeInEdge:", includeInEdge);
            console.info("DirectionMode:", this.DirectionMode, "max_distance_threshold:", max_distance_threshold);

            const connectedNodeIds = new Set();
            const edgeMap = new Map();

            const nodesWithRootDistance0 = new Set();
            const nodesWithinThreshold = new Set();

            const nodeMap = this.nodeMap;

            for (const [nodeId, node] of nodeMap.entries()) {
                if (node.root_distance !== undefined) {
                    if (node.root_distance === 0) {
                        nodesWithRootDistance0.add(nodeId);
                    }
                    if (node.root_distance <= max_distance_threshold) {
                        nodesWithinThreshold.add(nodeId);
                    }
                }
            }

            if (nodesWithRootDistance0.size === 0) {
                const visibleNodes = [];
                const mergedEdges = [];
                const message = "Select a few Nodes!";
                return { visibleNodes, mergedEdges, message };
            }

            const filter = this.edgeFilter;
            let edges = this.graphData.edges;
            edges = edges.filter(edge => filter[edge.label]);

            if (edges.length === 0) {
                const visibleNodes = [];
                const mergedEdges = [];
                const message = "Select a few Edges!";
                return { visibleNodes, mergedEdges, message };
            }

            for (const edge of edges) {
                if (!this.edgeFilter[edge.label]) {
                    continue;
                }

                const sourceNode = this.nodeMap.get(edge.source);
                const targetNode = this.nodeMap.get(edge.target);

                if (!sourceNode || !targetNode) {
                    continue;
                }

                if (sourceNode.root_distance === undefined || targetNode.root_distance === undefined) {
                    continue;
                }

                let includeEdge = false;
                const sourceWithinThreshold = nodesWithinThreshold.has(edge.source);
                const targetWithinThreshold = nodesWithinThreshold.has(edge.target);

                if (!sourceWithinThreshold || !targetWithinThreshold) {
                    continue;
                }

                if (includeOutEdge && includeInEdge) {
                    includeEdge = true;
                } else if (includeOutEdge) {
                    includeEdge = targetNode.root_distance > sourceNode.root_distance;
                } else if (includeInEdge) {
                    includeEdge = targetNode.root_distance < sourceNode.root_distance;
                }

                if (edgeMap.size > 1500) {
                    message = "Incomplete Graph!\nSize is limited to avoid clutter!";
                    break;
                }

                if (includeEdge) {
                    const key = `${edge.source}-${edge.target}`;

                    if (edgeMap.has(key)) {
                        const existingEdge = edgeMap.get(key);
                        existingEdge.labels.push(edge.label);
                        existingEdge.document_ids.push(...edge.document_ids);
                    } else {
                        edgeMap.set(key, {
                            source: edge.source,
                            target: edge.target,
                            labels: [edge.label],
                            document_ids: [ ...edge.document_ids ]
                        });
                    }

                    connectedNodeIds.add(edge.source);
                    connectedNodeIds.add(edge.target);
                }
            }

            const mergedEdges = Array.from(edgeMap.values()).map(edge => ({
                source: edge.source,
                target: edge.target,
                label: edge.labels,
                document_ids: edge.document_ids
            }));

            const visibleNodes = Array.from(connectedNodeIds).map(nodeId => this.nodeMap.get(nodeId));

            if (mergedEdges.length === 0) {
                if (this.selectedNodesFiltered_EdgeLabels.length === 0){
                    message = "Select Nodes which have at least one connection!"
                } else {
                    message = "No edges found for current filters!"
                }
            }

            console.info("mergedEdges.length:", mergedEdges.length)

            return { visibleNodes, mergedEdges, message };
        } else if (this.operation_mode === 2) {
            const connectedNodeIds = new Set();
            const edgeMap = new Map();

            const nodeMap = this.nodeMap;

            const filter = this.edgeFilter;
            let edges = this.graphData.edges;
            edges = edges.filter(edge => filter[edge.label]);

            console.info(filter);
            console.info(edges);

            if (edges.length === 0) {
                const visibleNodes = [];
                const mergedEdges = [];
                const message = "Select a few Edges!";
                return { visibleNodes, mergedEdges, message };
            }

            for (const edge of edges) {
                if (!this.edgeFilter[edge.label]) {
                    continue;
                }

                if (edgeMap.size > 1500) {
                    message = "Incomplete Graph!\nSize is limited to avoid clutter!";
                    break;
                }

                const key = `${edge.source}-${edge.target}`;

                if (edgeMap.has(key)) {
                    const existingEdge = edgeMap.get(key);
                    existingEdge.labels.push(edge.label);
                    existingEdge.document_ids.push(...edge.document_ids);
                } else {
                    edgeMap.set(key, {
                        source: edge.source,
                        target: edge.target,
                        labels: [edge.label],
                        document_ids: [ ...edge.document_ids ]
                    });
                }

                connectedNodeIds.add(edge.source);
                connectedNodeIds.add(edge.target);
            }

            const mergedEdges = Array.from(edgeMap.values()).map(edge => ({
                source: edge.source,
                target: edge.target,
                label: edge.labels,
                document_ids: edge.document_ids
            }));

            const visibleNodes = Array.from(connectedNodeIds).map(nodeId => this.nodeMap.get(nodeId));

            if (mergedEdges.length === 0) {
                message = "Something is not ok ... this should never happen!"
            }

            console.info("mergedEdges.length:", mergedEdges.length)

            return { visibleNodes, mergedEdges, message };
        }
    }
}


class Renderer {
     constructor(dataManager) {
        this.dataManager = dataManager;
        this.simulation = null;

        this.edgeFilterContainer = document.getElementById('edgeFilterContainer');
        this.nodeLabelFilterContainer = document.getElementById('nodeLabelFilterContainer');
        this.nodeTypeFilterContainer = document.getElementById('nodeTypeFilterContainer');

        this.svg = d3.select("#graph");

        this.zoom = null;
        this.zoomGroup = null;
        this.graphWidth = 0;
        this.graphHeight = 0;
    }

    resetZoom() {
        console.info("resetZoom()");
        if (!this.zoom || !this.zoomGroup) {
            console.warn("Zoom not initialized yet!");
            return;
        }

        this.zoomGroup.attr("transform", null); // Clear any existing transform
        const bounds = this.zoomGroup.node().getBBox();
        const fullWidth = bounds.width;
        const fullHeight = bounds.height;
        const midX = bounds.x + fullWidth / 2;
        const midY = bounds.y + fullHeight / 2;

        console.log("Bounding box:", bounds);
        if (bounds.width === 0 || bounds.height === 0) {
            console.warn("Invalid Bounding Box!");
            return;
        }

        const svg = this.svg;
        const width = this.graphWidth;
        const height = this.graphHeight;

        const scale = 0.9 / Math.max(fullWidth / width, fullHeight / height);
        const translate = [width / 2 - scale * midX, height / 2 - scale * midY];

        console.log("BBox:", bounds);
        console.log("Scale:", scale);
        console.log("Translate:", translate);

        svg.transition().duration(500).call(
            this.zoom.transform,
            d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
        );
    }

    renderNodeTypes(graph_changed = false) {
        console.info("--> renderNodeTypes()");
        const dataManager = this.dataManager;
        const container = this.nodeTypeFilterContainer;
        container.innerHTML = '';

        if (dataManager.typeFilteringNodes_Enabled) {
            const nodeTypes = dataManager.nodeTypes_Filtered;
            console.info("nodeTypes -----------------------> ", nodeTypes);

            if (nodeTypes.length === 0) {
                container.innerHTML = '<p>No types available</p>';
                return;
            }

            const counts = dataManager.nodeTypeCounts;

            if (dataManager.nodeTypeSortOrder === 'alphabetical') {
                nodeTypes.sort((a, b) => a.type.localeCompare(b.type));
            } else {
                nodeTypes.sort((a, b) => (counts[b.type] || 0) - (counts[a.type] || 0));
            }

            nodeTypes.forEach(({ type }) => {
                const typeElement = document.createElement('div');
                typeElement.className = 'filter-option';
                typeElement.innerHTML = `
                    <label>
                        <input type="checkbox" class="node-type-checkbox" data-type="${type}" ${dataManager.nodeTypeFilter[type] ? 'checked' : ''}>
                        <span>${type}<span class="count-label">${counts[type] || 0}</span></span>
                    </label>`;
                container.appendChild(typeElement);
            });

            container.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                checkbox.addEventListener('change', (event) => {
                    const type = event.target.dataset.type;
                    dataManager.toggleNodeType(type);
                    this.renderNodeLabels();
                });
            });

        } else {
            container.innerHTML = '<span class="empty_filter">Filtering Disabled!</span>';
        }

        this.renderNodeLabels(graph_changed)
    }

    renderNodeLabels(graph_changed = false) {
        console.info("--> renderNodeLabels()");

        const dataManager = this.dataManager;
        const container = this.nodeLabelFilterContainer;
        container.innerHTML = '';

        let nodeLabels =  dataManager.typeFiltered_NodeLabels;

        const selectedNodesCount = Object.values(dataManager.nodeFilter).filter(value => value === true).length;
        const counter_element = document.getElementById('counter_nodes')
        counter_element.innerText = selectedNodesCount;
        counter_element.style.background = selectedNodesCount > 0 ? 'black':'silver'

        const counts = dataManager.nodeLabelEdgeCounts;
        console.info("--> renderNodeLabels() - typeFiltered_NodeLabels.length: " + nodeLabels.length);

        if (dataManager.nodeLabelSortOrder === 'alphabetical') {
            nodeLabels.sort((a, b) => a.localeCompare(b));
        } else {
            nodeLabels.sort((a, b) => (counts[b] || 0) - (counts[a] || 0));
        }

        if (nodeLabels.length > 0) {
            nodeLabels.forEach(label => {
                let nodeTypeStr = '';
                if (dataManager.showNodeTypes) {
                    nodeTypeStr = " (" + dataManager.nodeLabelToNodeTypeMap[label] +")"
                }

                const labelElement = document.createElement('div');
                labelElement.className = 'filter-option';
                labelElement.innerHTML = `
                    <label>
                        <input type="checkbox" data-label="${label}" ${dataManager.nodeFilter[label] ? 'checked' : ''}>
                        <span>${label}<span class="NodeLabelTypeStr">${nodeTypeStr}</span><span class="count-label">${counts[label] || 0}</span></span>
                    </label>`;
                container.appendChild(labelElement);
            });

            container.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                checkbox.addEventListener('change', (event) => {
                    const label = event.target.dataset.label;
                    dataManager.toggleNodeLabel(label);
                    this.renderNodeLabels(true);
                });
            });
        } else {
            const labelElement = document.createElement('div');
                labelElement.className = 'span';
                labelElement.innerHTML = `
                    <span class="empty_filter">select a category first ...</span>`;
                container.appendChild(labelElement);
        }


        this.renderEdgeLabels(graph_changed);
    }

    renderEdgeLabels(graph_changed = false) {
        console.info("--> renderEdgeLabels()");
        const dataManager = this.dataManager;
        const container = this.edgeFilterContainer;
        container.innerHTML = '';

        let edgeLabels = dataManager.selectedNodesFiltered_EdgeLabels;
        const counts = dataManager.selectedNodesFiltered_EdgeLabelCounts;

        const selectedEdgesCount = Object.values(dataManager.edgeFilter).filter(value => value === true).length;
        const counter_element = document.getElementById('counter_edges')
        counter_element.innerText = selectedEdgesCount;
        counter_element.style.background = selectedEdgesCount > 0 ? 'black':'silver'


        if (dataManager.edgeLabelSortOrder === 'alphabetical') {
            edgeLabels.sort((a, b) => a.label.localeCompare(b.label));
        } else {
            edgeLabels.sort((a, b) => (counts[b.label] || 0) - (counts[a.label] || 0));
        }

        if (edgeLabels.length > 0) {
            if (dataManager.operation_mode!==2) {
                edgeLabels.forEach(({ label }) => {
                    const labelElement = document.createElement('div');
                    labelElement.className = 'filter-option';
                    labelElement.innerHTML = `
                        <label>
                            <input type="checkbox" data-label="${label}" ${dataManager.edgeFilter[label] ? 'checked' : ''}>
                            <span>${label}<span class="count-label">${counts[label] || 0}</span></span>
                        </label>`;

                    container.appendChild(labelElement);
                });
            } else {
                edgeLabels.forEach(({ label }) => {
                    const labelElement = document.createElement('div');
                    labelElement.className = 'filter-option';
                    labelElement.innerHTML = `
                        <label>
                            <input type="checkbox" class="node-type-checkbox" data-label="${label}" ${dataManager.edgeFilter[label] ? 'checked' : ''}>
                            <span>${label}<span class="count-label">${counts[label] || 0}</span></span>
                        </label>`;

                    container.appendChild(labelElement);
                });
            }

            container.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                checkbox.addEventListener('change', (event) => {
                    const label = event.target.dataset.label;
                    dataManager.toggleEdgeLabel(label);
                    console.info("Toggle: ", event);
                    if (dataManager.operation_mode === 1) {
                        dataManager.calculateRootDistances()
                    }
                    this.renderEdgeLabels(true);
                });
            });

        } else {
            const labelElement = document.createElement('div');
                labelElement.className = 'span';
                labelElement.innerHTML = `
                    <span class="empty_filter">select some nodes ...</span>`;
                container.appendChild(labelElement);
        }

        if (graph_changed) {
            this.renderGraph()
        }
    }

    renderGraph() {
        console.info("--> renderGraph()");
        const dataManager = this.dataManager;
        const svg = this.svg;

        if (this.simulation) {
           this.simulation.stop();
           this.simulation = null;
        }
        svg.selectAll("*").remove();

        svg.on(".zoom", null);
        svg.on("*", null);

        const width = svg.node().clientWidth;
        const height = svg.node().clientHeight;

        this.graphWidth = width;
        this.graphHeight = height;

        const { visibleNodes: nodes, mergedEdges: edges, message: algoMessage } = dataManager.getVisibleGraph();

        const zoomGroup = svg.append("g");
        this.zoomGroup = zoomGroup;

        if (nodes.length === 0) {
            svg.append("text")
                .attr("x", width / 2)
                .attr("y", height / 2)
                .attr("text-anchor", "middle")
                .attr("class", "empty-graph-message")
                .text(algoMessage);
            return;
        }

        svg.append("defs").append("marker")
            .attr("id", "arrowhead")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 10)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#999");

        const links = edges.map(edge => {
            return {
                source: dataManager.nodeMap.get(edge.source),
                target: dataManager.nodeMap.get(edge.target),
                label: edge.label,
                document_ids: edge.document_ids
            };
        });

        this.simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(150))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("x", d3.forceX(width / 2).strength(0.05))
            .force("y", d3.forceY(height / 2).strength(0.05))
            .force("collision", d3.forceCollide().radius(30));

        const simulation = this.simulation;

        const link = zoomGroup.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("class", "link")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .attr("stroke-width", 2)
            .attr("marker-end", "url(#arrowhead)");

        link.on("mouseover", (event, d) => {
                const tooltipHTML = d.label.map((lbl, idx) => {
                    const docId = d.document_ids[idx];
                    return `${d.source.label} <strong>${lbl}</strong><sub>${docId}</sub> ${d.target.label}`;
                }).join("<br>");

                tooltip.style.visibility = "visible";
                tooltip.innerHTML = tooltipHTML;
            })
            .on("mousemove", (event) => {
                tooltip.style.top = `${event.pageY + 10}px`;
                tooltip.style.left = `${event.pageX + 10}px`;
            })
            .on("mouseout", () => {
                tooltip.style.visibility = "hidden";
            });

        const linkLabels = zoomGroup.append("g")
            .selectAll("text")
            .data(links)
            .join("text")
            .attr("class", "link-label")
            .text(d => d.label);


        linkLabels.on("mouseover", (event, d) => {
                const tooltipHTML = d.label.map((lbl, idx) => {
                    const docId = d.document_ids[idx];
                    return `${d.source.label} <strong>${lbl}</strong><sub>${docId}</sub> ${d.target.label}`;
                }).join("<br>");

                tooltip.style.visibility = "visible";
                tooltip.innerHTML = tooltipHTML;
            })
            .on("mousemove", (event) => {
                tooltip.style.top = `${event.pageY + 10}px`;
                tooltip.style.left = `${event.pageX + 10}px`;
            })
            .on("mouseout", () => {
                tooltip.style.visibility = "hidden";
            });

        const tooltip = document.getElementById("tooltip");

        const nodeLabelCounts = dataManager.nodeLabelEdgeCounts;
        const counts = Object.values(nodeLabelCounts);
        const maxCount = counts.length > 0 ? Math.max(...counts) : 1;
        const minCount = counts.length > 0 ? Math.min(...counts) : 0;

        function getNodeRadius(label) {
            const count = nodeLabelCounts[label] || 0;
            if (maxCount === minCount) {
                return 10;
            }
            return 10 + ((count - minCount) * (30 - 10) / (maxCount - minCount));
        }

        const node = zoomGroup.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(nodes)
            .join("g")
            .call(d3.drag()
                .on("start", dragStarted)
                .on("drag", dragged)
                .on("end", dragEnded))
            .on("mouseover", (event, d) => {
                tooltip.style.visibility = "visible";
                tooltip.innerHTML = `
                    <strong>${d.label}</strong> ${d.type}
                    <br>
                    <span style="color: gray;">Document: ${d.document_ids.map(id => `${id}`).join(',')}</span>
                `;
            })
            .on("mousemove", (event) => {
                tooltip.style.top = `${event.pageY + 10}px`;
                tooltip.style.left = `${event.pageX + 10}px`;
            })
            .on("mouseout", () => {
                tooltip.style.visibility = "hidden";
            });

        node.append("circle")
            .attr("r", d => getNodeRadius(d.label))
            .attr("fill", d => dataManager.generateColor(d.type));

        const rootNodes = dataManager.getSelectedNodes();
        const rootNodeIds = new Set(rootNodes.map(node => node.id));
        nodes.forEach(node => {
            node.isRootNode = dataManager.operation_mode == 2 ? true : rootNodeIds.has(node.id);
        });

        node.append("text")
            .attr("class", "label")
            .attr("text-anchor", "middle")
            .attr("dy", d => -(getNodeRadius(d.label) + 3))
            .style("font-weight", d => d.isRootNode  ? "bold" : "normal")
            .style("font-size", d => d.isRootNode ? "15px" : "12px")
            .style("font-family", d => d.isRootNode ? "Comic Sans MS" : "sans-serif")
            .text(d => d.label);

        if (dataManager.showRootDistance && dataManager.operation_mode === 1) {
            node.append("text")
                .attr("dy", 4)
                .attr("class", "distance-label")
                .style("font-size", "10px")
                .style("text-anchor", "middle")
                .text(d => d.root_distance);
        }

        simulation.on("tick", () => {
            link
                .attr("x1", d => {
                    const r = getNodeRadius(d.source.label);
                    const dx = d.target.x - d.source.x;
                    const dy = d.target.y - d.source.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    const offsetX = dx * (r/dist);
                    return d.source.x + offsetX;
                })
                .attr("y1", d => {
                    const r = getNodeRadius(d.source.label);
                    const dx = d.target.x - d.source.x;
                    const dy = d.target.y - d.source.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    const offsetY = dy * (r/dist);
                    return d.source.y + offsetY;
                })
                .attr("x2", d => {
                    const r = getNodeRadius(d.target.label);
                    const dx = d.target.x - d.source.x;
                    const dy = d.target.y - d.source.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    const offsetX = dx * (r/dist);
                    return d.target.x - offsetX;
                })
                .attr("y2", d => {
                    const r = getNodeRadius(d.target.label);
                    const dx = d.target.x - d.source.x;
                    const dy = d.target.y - d.source.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    const offsetY = dy * (r/dist);
                    return d.target.y - offsetY;
                });

            const t = 0.3;
            linkLabels
                .attr("x", d => {
                    const sx = d.source.x, sy = d.source.y, tx = d.target.x, ty = d.target.y;
                    return sx + (tx - sx) * t;
                })
                .attr("y", d => {
                    const sx = d.source.x, sy = d.source.y, tx = d.target.x, ty = d.target.y;
                    return sy + (ty - sy) * t;
                });

            node
                .attr("transform", d => `translate(${d.x},${d.y})`);
        });

        if (algoMessage !== "") {
          const lines = algoMessage.split('\n');
          const messageGroup = svg.append("g")
            .attr("class", "warning-message-group");

          messageGroup.attr("transform", `translate(${width / 2}, ${height / 2 - (lines.length - 1) * 20 / 2})`);

          const textElement = messageGroup.append("text")
            .attr("text-anchor", "middle")
            .attr("class", "warning-graph-message");

          lines.forEach((line, index) => {
            textElement.append("tspan")
              .attr("x", 0)
              .attr("dy", index === 0 ? 0 : 40)
              .text(line);
          });
        }

        const zoom = d3.zoom()
            .scaleExtent([0.2, 3])
            .on("zoom", (event) => {
                zoomGroup.attr("transform", event.transform);
            });
        this.zoom = zoom;
        svg.call(zoom);

        function dragStarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragEnded(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
    }

}

function renderMetadataLegend(dataManager) {
    const legendContainer = document.getElementById('metadataLegend');
    legendContainer.innerHTML = '';

    console.log("Metadata Renderer", dataManager.graphData.metadata)

    const metadata = dataManager.graphData.metadata || [];
    if (metadata.length === 0) {
        legendContainer.textContent = 'No metadata available.';
        return;
    }

    const title = document.createElement('div');
    title.style.fontWeight = 'bold';
    title.style.marginBottom = '8px';
    title.textContent = 'Documents';
    legendContainer.appendChild(title);

    metadata.forEach((item) => {
         let displayFilename = item.filename;
        if (displayFilename && displayFilename.length > 48) {
            displayFilename = displayFilename.substring(0, 48) + '...';
        }

        const itemDiv = document.createElement('div');
        itemDiv.style.marginBottom = '4px';
        itemDiv.innerText = `${(item.index)}. ${displayFilename}`;
        legendContainer.appendChild(itemDiv);
    });
}
