// ROLE 1: Frontend Developer - All client-side logic here

// State management
let currentState = APP_STATE;
let graphData = null;
let network = null;

// Initialize the UI based on the current state
function initializeUI() {
    // Hide all pages
    document.querySelectorAll('.page-state').forEach(page => {
        page.style.display = 'none';
    });

    // Show the appropriate page based on state
    switch (currentState) {
        case 'NEEDS_INIT':
            document.getElementById('init-page').style.display = 'block';
            setupInitPage();
            break;
        case 'NOT_READY':
            document.getElementById('not-ready-page').style.display = 'block';
            break;
        case 'GENERATING':
            document.getElementById('loading-page').style.display = 'block';
            pollForCompletion();
            break;
        case 'ACTIVE':
            document.getElementById('app-page').style.display = 'block';
            setupAppPage();
            break;
    }
}

// Setup the initialization page
function setupInitPage() {
    const initBtn = document.getElementById('init-btn');
    initBtn.addEventListener('click', async () => {
        const topics = document.getElementById('topics-input').value;
        
        // Call the initialization API
        try {
            const response = await fetch('/api/initialize-course', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ course_id: COURSE_ID, topics: topics })
            });
            
            const result = await response.json();
            
            if (result.status === 'complete') {
                currentState = 'GENERATING';
                initializeUI();
            }
        } catch (error) {
            console.error('Initialization failed:', error);
            alert('Failed to initialize course. Please try again.');
        }
    });
}

// Poll for completion when in GENERATING state
async function pollForCompletion() {
    // TODO: Implement polling logic
    // Check the course status every few seconds
    // When status becomes ACTIVE, reload the page or update state
}

// Setup the main application page
async function setupAppPage() {
    // Load graph data
    await loadGraphData();
    
    // Initialize Vis.js network
    initializeGraph();
    
    // Setup chat interface
    setupChat();
    
    // Setup file toggle
    setupFileToggle();
}

// Load graph data from API
async function loadGraphData() {
    try {
        const response = await fetch(`/api/get-graph?course_id=${COURSE_ID}`);
        const data = await response.json();
        
        graphData = {
            nodes: JSON.parse(data.nodes),
            edges: JSON.parse(data.edges),
            data: JSON.parse(data.data)
        };
    } catch (error) {
        console.error('Failed to load graph data:', error);
    }
}

// Initialize the Vis.js graph visualization
function initializeGraph() {
    if (!graphData) return;
    
    const container = document.getElementById('graph-network');
    const data = {
        nodes: new vis.DataSet(graphData.nodes),
        edges: new vis.DataSet(graphData.edges)
    };
    
    const options = {
        // TODO: Configure Vis.js options
        // Set colors for topic vs file nodes
        // Configure physics, layout, etc.
    };
    
    network = new vis.Network(container, data, options);
    
    // Handle node clicks
    network.on('click', (params) => {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            showNodeDetails(nodeId);
        }
    });
}

// Show details for a clicked node
function showNodeDetails(nodeId) {
    const detailsDiv = document.getElementById('node-details');
    
    // TODO: Implement node details display
    // If it's a topic node, show summary and sources
    // If it's a file node, show link to file
    
    detailsDiv.innerHTML = `<p>Details for node: ${nodeId}</p>`;
}

// Setup the chat interface
function setupChat() {
    const sendBtn = document.getElementById('chat-send');
    const input = document.getElementById('chat-input');
    
    sendBtn.addEventListener('click', () => sendMessage());
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

// Send a chat message
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const query = input.value.trim();
    
    if (!query) return;
    
    // Add user message to chat
    addMessageToChat('user', query);
    input.value = '';
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ course_id: COURSE_ID, query: query })
        });
        
        const result = await response.json();
        
        // Add bot response to chat
        addMessageToChat('bot', result.answer, result.sources);
        
    } catch (error) {
        console.error('Chat failed:', error);
        addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.');
    }
}

// Add a message to the chat display
function addMessageToChat(sender, message, sources = []) {
    const messagesDiv = document.getElementById('chat-messages');
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}-message`;
    messageElement.innerHTML = `<p>${message}</p>`;
    
    if (sources.length > 0) {
        const sourcesHTML = sources.map(s => `<span class="source">${s}</span>`).join(', ');
        messageElement.innerHTML += `<div class="sources">Sources: ${sourcesHTML}</div>`;
    }
    
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Setup file toggle functionality
function setupFileToggle() {
    const toggleBtn = document.getElementById('toggle-files');
    
    // TODO: Implement file list toggle
    // Show/hide file nodes in the graph
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initializeUI);
