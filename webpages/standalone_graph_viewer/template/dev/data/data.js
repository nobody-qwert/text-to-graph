const base64GzippedData1 = 'idejonaszoveg1';
const gzippedData1 = Uint8Array.from(atob(base64GzippedData1), c => c.charCodeAt(0));
const default_nodes_str = pako.ungzip(gzippedData1, { to: 'string' });

const base64GzippedData2 = 'idejonaszoveg2';
const gzippedData2 = Uint8Array.from(atob(base64GzippedData2), c => c.charCodeAt(0));
const default_edges_str = pako.ungzip(gzippedData2, { to: 'string' });

const base64GzippedData3 = 'idejonaszoveg3';
const gzippedData3 = Uint8Array.from(atob(base64GzippedData3), c => c.charCodeAt(0));
const default_metadata_str = pako.ungzip(gzippedData3, { to: 'string' });
