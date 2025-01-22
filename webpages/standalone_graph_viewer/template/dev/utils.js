function parseCSV(csvString) {
    // Normalize line breaks to \n
    csvString = csvString.replace(/\r\n/g, '\n').replace(/\r/g, '\n');

    const lines = [];
    let currentLine = [];
    let currentValue = '';
    let insideQuotes = false;

    for (let i = 0; i < csvString.length; i++) {
        const char = csvString[i];
        const nextChar = csvString[i + 1];

        if (char === '"') {
            if (insideQuotes && nextChar === '"') {
                currentValue += '"';
                i++;
            } else {
                insideQuotes = !insideQuotes;
            }
        } else if (char === ',' && !insideQuotes) {
            currentLine.push(currentValue.trim());
            currentValue = '';
        } else if (char === '\n' && !insideQuotes) {
            currentLine.push(currentValue.trim());
            currentValue = '';
            if (currentLine.length > 0) {
                lines.push(currentLine);
                currentLine = [];
            }
        } else {
            currentValue += char;
        }
    }

    // Add any remaining data
    if (currentValue || currentValue === '') {
        currentLine.push(currentValue.trim());
    }
    if (currentLine.length > 0) {
        lines.push(currentLine);
    }

    if (lines.length === 0) {
        return { headers: [], data: [] };
    }

    const headers = lines[0];
    const data = lines.slice(1).map(line => {
        const obj = {};
        for (let i = 0; i < headers.length; i++) {
            obj[headers[i]] = line[i] || '';
        }
        return obj;
    });

    return { headers, data };
}


function buildGraphJSON(nodesData, edgesData, metadata) {
    function extractDocumentIDs(obj) {
        if (!obj.label) return;

        const parts = obj.label.split('|');
        obj.label = parts.shift();
        let docIds = parts.filter(Boolean);

        if (docIds.length === 0) {
          docIds = ["0"];
        }

        obj.document_ids = docIds;

        if (obj.type) {
            const typeParts = obj.type.split('|').filter(Boolean);
            obj.type = typeParts;
        }
    }
    function mapNodes(nodesData) {
        return nodesData.data.map(node => {
            return {
                id: node['id'],
                label: node['label'],
                type: node['type'],
            };
        });
    }

    function mapEdges(edgesData) {
        return edgesData.data.map(edge => {
            return {
                source: edge['source'],
                target: edge['target'],
                label: edge['label'],
            };
        });
    }

    const nodes = mapNodes(nodesData);
    const edges = mapEdges(edgesData);

    if (nodes.length > 0) {
        nodes.forEach(node => extractDocumentIDs(node));
    }
    if (edges.length > 0) {
        edges.forEach(edge => extractDocumentIDs(edge));
    }

    return { nodes, edges, metadata };
}
