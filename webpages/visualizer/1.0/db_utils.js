let db = null;

const graphsDropdown = document.getElementById('graphs');

window.initSqlJs({
    locateFile: filename => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/${filename}`
}).then(SQL => {
    document.getElementById('fileInput').addEventListener('change', event => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function () {
                const Uints = new Uint8Array(reader.result);
                db = new SQL.Database(Uints);
                loadGraphs();
            };
            reader.readAsArrayBuffer(file);
        }
    });
});

function loadGraphs() {
    const query = `
        SELECT Graphs.id, Configurations.chunk_size, Configurations.padding_size
        FROM Graphs
        JOIN Configurations ON Graphs.config_id = Configurations.id
    `;
    const res = db.exec(query);
    const graphs = document.getElementById('graphs');
    graphs.innerHTML = '';
    if (res.length > 0) {
        const rows = res[0].values;

        rows.forEach(row => {
            const [id, chunk_size, padding_size] = row;

            const optionText = `Graph ID: ${id} (Chunk Size: ${chunk_size}, Padding Size: ${padding_size})`;
            const option = document.createElement('option');
            option.value = id;
            option.textContent = optionText;
            graphs.appendChild(option);
        });

        const container = document.getElementById('graphs-browser-container');
        container.classList.remove('hidden');
        container.style.visibility = 'visible';
        container.style.display = 'flex';
        document.getElementById('generate').addEventListener('click', generateGraphJSON);
    } else {
        alert('No graphs found in the database.');
    }
}

function generateGraphJSON() {
    const graphId = document.getElementById('graphs').value;
    const stmt = db.prepare("SELECT nodes, edges, metadata FROM Graphs WHERE id = ?");
    stmt.bind([graphId]);
    if (stmt.step()) {
        const row = stmt.get();
        const nodesCSV = row[0];
        const edgesCSV = row[1];
        const metadata_str = row[2];

        const nodesData = parseCSV(nodesCSV);
        const edgesData = parseCSV(edgesCSV);
        metadata = {}

        try {
            metadata = JSON.parse(metadata_str);
            console.log("Graph metadata:\n", metadata)
        } catch (error) {
            console.error('Could not parse Graph metadata. Invalid JSON string:', error);
        }

        nodesData.data = nodesData.data.filter(obj => {
            return Object.values(obj).some(value => value.trim() !== '');
        });

        const graphJSON = buildGraphJSON(nodesData, edgesData, metadata);
        console.log(JSON.stringify(graphJSON, null, 2));

        dataManager.loadGraphData(graphJSON);
        renderer.renderNodeTypes(true);
        renderMetadataLegend(dataManager);
    } else {
        alert('Graph not found.');
    }
    stmt.free();
}