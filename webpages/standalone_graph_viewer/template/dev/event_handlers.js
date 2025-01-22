document.getElementById('selectEdgesOnlyBtn').addEventListener('click', function() {
    dataManager.operation_mode = 2;

    const btn0 = document.getElementById('selectEdgesOnlyBtn');
    const btn1 = document.getElementById('selectRoutesOnlyBtn');
    const btn2 = document.getElementById('selectExploreModeBtn');
    btn0.classList.add('checked');
    btn1.classList.remove('checked');
    btn2.classList.remove('checked');

    const edgeLabelFilterToggleBtn = document.getElementById('edgeLabelFilterToggleBtn');
    edgeLabelFilterToggleBtn.style.display = 'none';

    const graphControls = document.getElementById('graphControls');
    graphControls.style.display = 'none';

    const nodeTypeControls = document.getElementById('nodeTypeControls');
    const nodeLabelControls = document.getElementById('nodeLabelControls');
    const edgeLabelControls = document.getElementById('edgeLabelControls');
    nodeTypeControls.style.display = 'none';
    nodeLabelControls.style.display = 'none';
    edgeLabelControls.style.display = 'flex';

    title = document.getElementById('edgeLabelTitle');
    title.innerHTML = 'Relationships';
    title.style.background = '';

    dataManager.updateEdgeLabelFilter();
    renderer.renderEdgeLabels(true);
});

document.getElementById('selectRoutesOnlyBtn').addEventListener('click', function() {
    dataManager.operation_mode = 0;

    const btn0 = document.getElementById('selectEdgesOnlyBtn');
    const btn1 = document.getElementById('selectRoutesOnlyBtn');
    const btn2 = document.getElementById('selectExploreModeBtn');
    btn0.classList.remove('checked');
    btn1.classList.add('checked');
    btn2.classList.remove('checked');


    const graphControls = document.getElementById('graphControls');
    graphControls.style.display = 'none';

    const nodeTypeControls = document.getElementById('nodeTypeControls');
    const nodeLabelControls = document.getElementById('nodeLabelControls');
    const edgeLabelControls = document.getElementById('edgeLabelControls');
    nodeTypeControls.style.display = 'flex';
    nodeLabelControls.style.display = 'flex';
    edgeLabelControls.style.display = 'none';

    dataManager.updateNodeLabelFilter();
    renderer.renderNodeLabels(true);
});

document.getElementById('selectExploreModeBtn').addEventListener('click', function() {
    dataManager.operation_mode = 1;

    const btn0 = document.getElementById('selectEdgesOnlyBtn');
    const btn1 = document.getElementById('selectRoutesOnlyBtn');
    const btn2 = document.getElementById('selectExploreModeBtn');
    btn0.classList.remove('checked');
    btn1.classList.remove('checked');
    btn2.classList.add('checked');

    const graphControls = document.getElementById('graphControls');
    graphControls.style.display = 'block'

    const nodeTypeControls = document.getElementById('nodeTypeControls');
    const nodeLabelControls = document.getElementById('nodeLabelControls');
    const edgeLabelControls = document.getElementById('edgeLabelControls');
    nodeTypeControls.style.display = 'flex';
    nodeLabelControls.style.display = 'flex';
    edgeLabelControls.style.display = 'flex';

    const edgeLabelFilterToggleBtn = document.getElementById('edgeLabelFilterToggleBtn');
    edgeLabelFilterToggleBtn.style.display = 'flex';

    title = document.getElementById('edgeLabelTitle');
    if (dataManager.nodeFilteringEdges_Enabled) {
        title.innerHTML = 'Edges of Selected Nodes';
        title = document.getElementById('edgeLabelTitle');
        title.style.background = 'yellow';
    } else {
        title.innerHTML = 'All Edges';
    }

    dataManager.updateNodeTypeFilter();
    renderer.renderNodeTypes(true); // must re-render due to Select all button needs update!
});

/*------------------------------------------------------------------------------*/



function selectAllNodeTypes(selectAll) {
    if (dataManager.typeFilteringNodes_Enabled) {
        console.info("--> selectAllNodeTypes()");
        dataManager.selectAllNodeTypes(selectAll);
        renderer.renderNodeTypes()
    }
}

function selectAllNodes(selectAll) {
    console.info("--> selectAllNodes()");
    dataManager.selectAllNodeLabels(selectAll);
    renderer.renderNodeLabels(true)
}

function selectAllEdges(selectAll) {
    console.info("--> selectAllEdges()");
    dataManager.selectAllEdgeLabels(selectAll);
    renderer.renderEdgeLabels(true)
}

/*------------------------------------------------------------------------------*/

document.getElementById('DirectionBtn').addEventListener('click', function() {
    dataManager.DirectionMode = (dataManager.DirectionMode) % 3 + 1;

    const btn = document.getElementById('DirectionBtn');

    switch (dataManager.DirectionMode) {
        case 1:
            btn.innerHTML = '🡸🌐🡺';
            break;
        case 2:
            btn.innerHTML = '🡺🌐🡸';
            break;
        case 3:
            btn.innerHTML = '🡺🌐🡺';
            break;
        default:
            console.error('DirectionMode has an invalid value:', dataManager.DirectionMode);
            break;
    }

    dataManager.calculateRootDistances();
    renderer.renderGraph();
});

/*---------------------Slider Container ----------------------------------*/

document.getElementById('valueSlider').addEventListener('input', function() {
    const newValue = parseInt(this.value, 10);
    dataManager.max_distance_threshold = newValue;
    renderer.renderGraph();
});

document.getElementById('showRootDistanceBtn').addEventListener('click', function() {
    this.classList.toggle('selected'); // Optionally add a 'selected' class for visual feedback
    dataManager.showRootDistance = this.classList.contains('selected');
    renderer.renderGraph();
});

document.getElementById('showNodeTypesBtn').addEventListener('click', function() {
    this.classList.toggle('selected');
    dataManager.showNodeTypes = this.classList.contains('selected');
    renderer.renderNodeLabels();
});


/*--------------------------------------------------------------------------------------*/
/*                                                                                      */
/*                                  FILTER AREA                                         */
/*                                                                                      */
/*--------------------------------------------------------------------------------------*/


/*-----------------------------------------------------------------*/

function toggleNodeTypeSortOrder() {
    if (dataManager.typeFilteringNodes_Enabled) {
        const btn = document.getElementById('sortNodeTypesToggleBtn');
        if (dataManager.nodeTypeSortOrder === 'count') {
            dataManager.setNodeTypeSortOrder('alphabetical');
            btn.innerHTML = '🔼';
        } else {
            dataManager.setNodeTypeSortOrder('count');
            btn.innerHTML = '🔽';
        }

        renderer.renderNodeTypes();
    }
}

function toggleNodeLabelSortOrder() {
    const btn = document.getElementById('sortNodeLabelsToggleBtn');
    if (dataManager.nodeLabelSortOrder === 'count') {
        dataManager.setNodeLabelSortOrder('alphabetical');
        btn.innerHTML = '🔼';
    } else {
        dataManager.setNodeLabelSortOrder('count');
        btn.innerHTML = '🔽';
    }
    renderer.renderNodeLabels();
}

function toggleEdgeLabelSortOrder() {
    const btn = document.getElementById('sortEdgeLabelsToggleBtn');
    if (dataManager.edgeLabelSortOrder === 'count') {
        dataManager.setEdgeLabelSortOrder('alphabetical');
        btn.innerHTML = '🔼';
    } else {
        dataManager.setEdgeLabelSortOrder('count');
        btn.innerHTML = '🔽';
    }
    renderer.renderEdgeLabels();
}

//////////////////////////////////////////////////////////
//                    Toggle Filters                    //
//////////////////////////////////////////////////////////

document.getElementById('nodeLabelFilterToggleBtn0').addEventListener('click', function() {
    this.classList.toggle('checked');
    dataManager.typeFilteringNodes_Enabled = this.classList.contains('checked');

    btn = document.getElementById('nodeLabelFilterToggleBtn')
    btn.classList.toggle('checked');

    title = document.getElementById('nodeLabelTitle');
    if (dataManager.typeFilteringNodes_Enabled) {
        title.innerHTML = 'Nodes from Category';
        title.style.background = 'yellow';
    } else {
        title.innerHTML = 'All Nodes';
        title.style.background = '';
    }

    dataManager.updateNodeLabelFilter();
    renderer.renderNodeTypes();
});

document.getElementById('nodeLabelFilterToggleBtn').addEventListener('click', function() {
    this.classList.toggle('checked');
    dataManager.typeFilteringNodes_Enabled = this.classList.contains('checked');

    btn = document.getElementById('nodeLabelFilterToggleBtn0')
    btn.classList.toggle('checked');

    title = document.getElementById('nodeLabelTitle');
    if (dataManager.typeFilteringNodes_Enabled) {
        title.innerHTML = 'Nodes from Category';
        title.style.background = 'yellow';
    } else {
        title.innerHTML = 'All Nodes';
        title.style.background = '';
    }

    dataManager.updateNodeLabelFilter();
    renderer.renderNodeTypes();
});

document.getElementById('edgeLabelFilterToggleBtn').addEventListener('click', function() {
    this.classList.toggle('checked');
    dataManager.nodeFilteringEdges_Enabled = this.classList.contains('checked');

    title = document.getElementById('edgeLabelTitle');
    if (dataManager.nodeFilteringEdges_Enabled) {
        title.innerHTML = 'Edges of Selected Nodes';
        title.style.background = 'yellow';
    } else {
        title.innerHTML = 'All Edges';
        title.style.background = '';
        document.getElementById('edgeLabelControls').style.border = '1px solid #d3d3d3';

    }


    dataManager.updateEdgeLabelFilter();
    renderer.renderNodeLabels();
});


///////////////////////////////////////////////////////////////////////
//    User Input for filtering stuff                                 //
///////////////////////////////////////////////////////////////////////


const input_NodeTypes = document.getElementById('filterNodeTypes');
const clearButton_NodeTypes = document.getElementById('clearButtonNodeTypes');
clearButton_NodeTypes.addEventListener('click', () => {
    input_NodeTypes.value = '';
    input_NodeTypes.dispatchEvent(new Event('input'));
});
input_NodeTypes.addEventListener('input', (event) => {
    if (event.target.value.length > 20) {
        event.target.value = event.target.value.substring(0, 20);
    }

    dataManager.setInputFilterFor_NodeTypes(event.target.value);
    renderer.renderNodeTypes();
});

// ---------------------------------

const input_NodeLabels = document.getElementById('filterNodeLabels');
const clearButton_NodeLabels = document.getElementById('clearButtonNodeLabels');
clearButton_NodeLabels.addEventListener('click', () => {
    input_NodeLabels.value = '';
    input_NodeLabels.dispatchEvent(new Event('input'));
});
input_NodeLabels.addEventListener('input', (event) => {
    if (event.target.value.length > 20) {
        event.target.value = event.target.value.substring(0, 20);
    }

    dataManager.setInputFilterFor_NodeLabels(event.target.value);
    renderer.renderNodeLabels();
});

// ---------------------------------

const input_EdgeLabels = document.getElementById('filterEdgeLabels');
const clearButton_EdgeLabels = document.getElementById('clearButtonEdgeLabels');
clearButton_EdgeLabels.addEventListener('click', () => {
    input_EdgeLabels.value = '';
    input_EdgeLabels.dispatchEvent(new Event('input'));
});
input_EdgeLabels.addEventListener('input', (event) => {
    if (event.target.value.length > 20) {
        event.target.value = event.target.value.substring(0, 20);
    }

    dataManager.setInputFilterFor_EdgeLabels(event.target.value);
    renderer.renderEdgeLabels();
});


/*----------------------------------------------------------------------------*/

function togglePanel() {
    const container = document.getElementById('mainContainer');
    //const button = document.getElementById('collapseButton');

    container.classList.toggle('collapsed');
    //button.innerHTML = container.classList.contains('collapsed') ? '&raquo;' : '&laquo;';

    renderer.renderGraph();
}


/*----------------------------------------------------------------------------*/

document.addEventListener('DOMContentLoaded', () => {
    const tooltip = document.getElementById('tooltip');

    const buttonsWithTooltips = [
        {
            id: 'selectEdgesOnlyBtn',
            tooltipText: 'Discover Relationships',
        },
        {
            id: 'selectRoutesOnlyBtn',
            tooltipText: 'Find Routes',
        },
        {
            id: 'selectExploreModeBtn',
            tooltipText: 'Explore Graph',
        },
        {
            id: 'DirectionBtn',
            tooltipText: 'Edge Directions',
        },
        {
            id: 'showNodeTypesBtn',
            tooltipText: 'Show Category',
        },
        {
            id: 'nodeLabelFilterToggleBtn0',
            tooltipText: 'Category Filtering',
        },
        {
            id: 'nodeLabelFilterToggleBtn',
            tooltipText: 'Category Filtering',
        },
        {
            id: 'edgeLabelFilterToggleBtn',
            tooltipText: 'Node Filtering',
        },
        {
            id: 'valueSlider',
            tooltipText: 'Distance Threshold',
        },
        {
            id: 'resetZoomBtn',
            tooltipText: 'Zoom & Fit To Screen',
        },
        {
            id: 'counter_nodes',
            tooltipText: 'Number of selected nodes',
        },
        {
            id: 'counter_edges',
            tooltipText: 'Number of selected edges',
        },
        {
            id: 'showRootDistanceBtn',
            tooltipText: 'Show Node Distances',
        }



    ];

    buttonsWithTooltips.forEach(({ id, tooltipText }) => {
        const button = document.getElementById(id);

        if (!button) {
            console.warn(`Button with ID "${id}" not found in DOM.`);
            return;
        }

        button.addEventListener('mouseenter', (event) => {
            tooltip.textContent = tooltipText;
            tooltip.style.visibility = 'visible';
            tooltip.style.left = `${event.pageX + 10}px`;
            tooltip.style.top = `${event.pageY + 10}px`;
        });

        button.addEventListener('mousemove', (event) => {
            tooltip.style.left = `${event.pageX + 10}px`;
            tooltip.style.top = `${event.pageY + 10}px`;
        });

        button.addEventListener('mouseleave', () => {
            tooltip.style.visibility = 'hidden';
        });
    });
});


document.getElementById("resetZoomBtn").addEventListener("click", () => {
   renderer.resetZoom();
});