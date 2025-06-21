
const express = require('express');
const cors = require('cors');
const app = express();
const port = process.env.PORT || 3000;

const { JSDOM } = require('jsdom');
const { window } = new JSDOM('');
global.window = window;
global.document = window.document;

app.use(cors());
app.use(express.json());

const script = require('vm');
const https = require('https');
let puter;

function loadPuter(callback) {
    https.get("https://js.puter.com/v2/", res => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
            const ctx = { console, setTimeout, clearTimeout, global, puter: {} };
            script.createContext(ctx);
            script.runInContext(data, ctx);
            puter = ctx.puter;
            callback();
        });
    });
}

app.post('/chat', async (req, res) => {
    const { prompt, model } = req.body;
    if (!puter) return res.status(503).json({ error: 'Puter.js not ready yet.' });

    try {
        const result = await puter.ai.chat(prompt, { model });
        const reply = result.message?.content?.[0]?.text || "(No response)";
        res.json({ reply });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

loadPuter(() => {
    app.listen(port, () => {
        console.log(`🚀 Puter.js API running on port ${port}`);
    });
});
