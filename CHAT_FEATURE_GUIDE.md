# AI Chat Feature Guide — Janchor Auto Tracker

A comprehensive guide for replicating the browser-based AI chat feature in other web applications.

---

## Table of Contents

1. [Why This Architecture](#1-why-this-architecture)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Prerequisites](#3-prerequisites)
4. [HTML Structure](#4-html-structure)
5. [CSS Styling](#5-css-styling)
6. [API Key Management](#6-api-key-management)
7. [System Prompt Construction](#7-system-prompt-construction)
8. [Data Preparation Strategy](#8-data-preparation-strategy)
9. [Prompt Caching for Cost Efficiency](#9-prompt-caching-for-cost-efficiency)
10. [Sending Messages to the API](#10-sending-messages-to-the-api)
11. [Response Parsing](#11-response-parsing)
12. [Rendering Segments](#12-rendering-segments)
13. [Code Execution in Browser](#13-code-execution-in-browser)
14. [Chart Rendering from AI Responses](#14-chart-rendering-from-ai-responses)
15. [Table Rendering from AI Responses](#15-table-rendering-from-ai-responses)
16. [Save and Export Feature](#16-save-and-export-feature)
17. [Download Data CSV](#17-download-data-csv)
18. [Cost Management and Monitoring](#18-cost-management-and-monitoring)
19. [Adaptation Guide for Other Apps](#19-adaptation-guide-for-other-apps)
20. [Common Pitfalls](#20-common-pitfalls)

---
## 1. Why This Architecture

### Direct Browser-to-API

This chat feature makes API calls directly from the browser to Anthropic, with no backend server. This is unusual but has significant advantages for self-contained tools:

**Advantages:**
- Zero server costs or maintenance
- No CORS proxy needed (Anthropic allows it with a special header)
- The entire app is a single HTML file — chat included
- User provides their own API key, so no billing management needed
- Data never leaves the browser except to Anthropic

**Trade-offs:**
- API key is stored in localStorage (acceptable for personal/team tools)
- Cannot hide the API key from the user (by design — it is their key)
- Rate limiting is per-key, not per-app

### The Key Enabler

Anthropic provides a special HTTP header that permits browser-to-API calls:

```
anthropic-dangerous-direct-browser-access: true
```

Without this header, CORS would block the request. This header signals to Anthropic that you understand the security implications of exposing your API key in browser code.

---

## 2. High-Level Architecture

```
User Types Question
      |
      v
sendChatMessage()
      |
      +-- Build conversation history (last 20 messages)
      +-- buildSystemPrompt()
      |      |
      |      +-- buildDataSummary()     -> metadata text
      |      +-- buildFullSegmentData() -> ALL raw data rows (pipe-delimited)
      |      +-- buildCrossSegSummary() -> other segments annual totals
      |
      +-- fetch() to api.anthropic.com/v1/messages
      |      |
      |      +-- system: [{text: systemPrompt, cache_control: {type: "ephemeral"}}]
      |      +-- messages: [user/assistant history]
      |      +-- model: claude-sonnet-4-20250514
      |
      v
Response received
      |
      v
parseAssistantResponse(text)
      |
      +-- Split into segments: text, js, chart, table
      |
      v
renderSegment() for each segment
      |
      +-- text   -> simpleMarkdown() -> innerHTML
      +-- js     -> run code -> display result
      +-- chart  -> JSON.parse() -> Plotly.newPlot()
      +-- table  -> JSON.parse() -> HTML table
```

---

## 3. Prerequisites

### External Libraries (CDN)

1. **Plotly.js** — For rendering charts from AI responses

```html
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
```

2. **SheetJS (xlsx)** — For Excel file parsing (optional, only for data upload)

```html
<script src="https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js"></script>
```

### API Access

- An Anthropic API key (starts with `sk-ant-...`)
- Obtained from https://console.anthropic.com/settings/keys

---

## 4. HTML Structure

The chat interface has two states: setup (API key entry) and active chat.

### Setup State

```html
<div id="chat-setup" class="chat-setup">
  <h3>Chat with Your Data</h3>
  <p>Ask questions, create charts, run calculations using AI.</p>
  <input type="password" id="api-key-input"
         placeholder="Enter your Anthropic API key (sk-ant-...)">
  <button class="btn btn-primary" id="btn-save-key">
    Save &amp; Start Chatting
  </button>
  <p class="chat-help">
    Get your API key from
    <a href="https://console.anthropic.com/settings/keys" target="_blank">
      console.anthropic.com
    </a>
  </p>
</div>
```

### Active Chat State

```html
<div id="chat-interface" style="display:none">
  <!-- Toolbar -->
  <div class="chat-toolbar">
    <button class="btn btn-outline" id="btn-chat-clear">Clear</button>
    <button class="btn btn-outline" id="btn-chat-export">Export Saved</button>
    <button class="btn btn-outline" id="btn-chat-remove-key">Remove Key</button>
    <button class="btn btn-outline" id="btn-chat-download-data">Download Data CSV</button>
    <span class="chat-model-info">Model: Claude Sonnet</span>
  </div>

  <!-- Suggestion Cards -->
  <div class="chat-suggestions" id="chat-suggestions">
    <div class="suggestion-card" data-prompt="What is the overall industry trend?">
      <strong>Industry Trend</strong>
      <p>Analyze overall volume trends</p>
    </div>
    <!-- ... more suggestion cards ... -->
  </div>

  <!-- Message Container -->
  <div class="chat-messages" id="chat-messages"></div>

  <!-- Input Area -->
  <div class="chat-input-area">
    <textarea id="chat-input" placeholder="Ask about your data..." rows="1"></textarea>
    <button class="btn btn-primary" id="btn-chat-send">Send</button>
  </div>
</div>
```

### Key Design Decisions

- **Two-state UI**: Setup vs. chat interface, toggled by `display:none`
- **Suggestion cards**: Pre-built prompts that users can click to get started
- **Textarea (not input)**: Allows multi-line questions; auto-resizes with CSS
- **Toolbar**: Clear, Export, Remove Key, Download Data — all destructive actions are explicit

---

## 5. CSS Styling

### Chat Container Layout

```css
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
```

### Message Bubbles

```css
.chat-msg {
  max-width: 85%;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.5;
  position: relative;
  word-wrap: break-word;
}
.chat-msg.user {
  background: #2563eb;
  color: #fff;
  align-self: flex-end;
  border-bottom-right-radius: 4px;
}
.chat-msg.assistant {
  background: #f3f4f6;
  color: #1f2937;
  align-self: flex-start;
  border-bottom-left-radius: 4px;
}
```

### Typing Indicator (3 bouncing dots)

```css
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  align-self: flex-start;
}
.typing-dot {
  width: 8px;
  height: 8px;
  background: #9ca3af;
  border-radius: 50%;
  animation: typingBounce 1.4s infinite ease-in-out;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-8px); }
}
```

### Code Result Styling

```css
.chat-code-result {
  background: #f0fdf4;
  border-left: 3px solid #059669;
  padding: 8px 12px;
  margin: 8px 0;
  font-family: monospace;
  font-size: 13px;
  white-space: pre-wrap;
  border-radius: 4px;
}
.chat-code-error {
  background: #fef2f2;
  border-left-color: #dc2626;
  color: #dc2626;
}
```

---

## 6. API Key Management

### Storage

```javascript
let chatApiKey = '';
try {
  chatApiKey = localStorage.getItem('janchor_api_key') || '';
} catch(e) {}
```

### Save Key

```javascript
document.getElementById('btn-save-key').addEventListener('click', function() {
  var key = document.getElementById('api-key-input').value.trim();
  if (!key.startsWith('sk-ant-')) {
    alert('Please enter a valid Anthropic API key starting with sk-ant-...');
    return;
  }
  chatApiKey = key;
  localStorage.setItem('janchor_api_key', key);
  renderChatTab();  // Switch from setup to chat interface
});
```

### Remove Key

```javascript
function removeChatApiKey() {
  chatApiKey = '';
  localStorage.removeItem('janchor_api_key');
  renderChatTab();  // Switch back to setup screen
}
```

### State Switching Logic

```javascript
function renderChatTab() {
  if (chatApiKey) {
    document.getElementById('chat-setup').style.display = 'none';
    document.getElementById('chat-interface').style.display = '';
    renderAllChatMessages();  // Restore previous chat history
  } else {
    document.getElementById('chat-setup').style.display = '';
    document.getElementById('chat-interface').style.display = 'none';
  }
}
```

### Security Notes

- The key is stored in localStorage — acceptable for personal/team tools
- The `type="password"` input masks the key during entry
- Users can remove the key at any time via the toolbar
- The key is never sent anywhere except to Anthropic

---

## 7. System Prompt Construction

The system prompt is the most important part of the chat feature. It determines the AI quality.

### Structure (6 layers)

```
Layer 1: Role Definition
   "You are an expert analyst for Indian auto industry state-wise primary sales data."

Layer 2: Instructions
   "You have the COMPLETE raw dataset for the [SEGMENT] segment below (N rows x M quarters).
    This is ALL the data. Read actual numbers from this table to answer questions."

Layer 3: Data Metadata
   - Current segment, subsegments, companies list, states list, zones list
   - Zone-state mapping

Layer 4: Reference Information
   - Fiscal year definitions (FY17 = Apr 2016 - Mar 2017)
   - Quarter definitions (Q1=Apr-Jun, Q2=Jul-Sep, etc.)
   - Partial year warnings

Layer 5: COMPLETE RAW DATA
   - ALL rows for current segment in pipe-delimited format
   - Industry total row first (for market share computation)

Layer 6: Helper Functions & Output Formats
   - Available JS functions the AI can use in code blocks
   - Supported output formats (text, js, chart, table)
   - Rules for accuracy and data citation
```

### The buildSystemPrompt() Function

```javascript
function buildSystemPrompt() {
  var nSegRows = 0;
  for (var i = 0; i < ROWS.length; i++) {
    if (ROWS[i][0] === currentSegment) nSegRows++;
  }

  return 'You are an expert analyst for Indian auto industry...' +
    'DATA OVERVIEW:\n' + buildDataSummary() + '\n\n' +
    'FISCAL YEAR REFERENCE:\n...' +
    '=== COMPLETE RAW DATA: ' + currentSegment + ' ===\n' +
    buildFullSegmentData() + '\n\n' +
    buildCrossSegSummary() + '\n\n' +
    'JS HELPER FUNCTIONS...\n' +
    'OUTPUT FORMATS...\n' +
    'RULES...';
}
```

### Why Send ALL the Data?

Sending complete raw data (not summaries) is a deliberate design choice:

1. **Accuracy**: The AI reads actual numbers — no hallucination risk
2. **Flexibility**: Any ad-hoc query works without pre-computing aggregations
3. **No backend**: No vector DB, no retrieval logic, no chunking needed
4. **Prompt caching**: The large system prompt is cached, so cost is only paid once

For our dataset (~500 rows per segment x 43 quarters), the pipe-delimited data is about 50-80K tokens — well within Claude model context windows.

---

## 8. Data Preparation Strategy

### Pipe-Delimited Format

We use pipe-delimited (`|`) format instead of CSV or JSON:

```
Subsegment|Zone|State|Manufacturer|Q1FY16|Q2FY16|...|Q3FY26
ALL|ALL|ALL|INDUSTRY TOTAL|150000|162000|...|185000
Cars|North|Delhi|Maruti Suzuki|5000|5200|...|6100
Cars|North|Delhi|Hyundai|2000|2100|...|2500
```

**Why pipe-delimited?**
- ~30% fewer tokens than CSV (no quoting needed, no escaping)
- ~60% fewer tokens than JSON
- Easy for the AI to parse visually
- No ambiguity with commas in values

### buildFullSegmentData()

```javascript
function buildFullSegmentData() {
  var lines = [];
  // Header row with all quarter labels
  lines.push('Subsegment|Zone|State|Manufacturer|' + QLABELS.join('|'));

  // Industry totals row FIRST (for easy market share computation)
  var indVols = getIndustryVols('All');
  var indRow = ['ALL|ALL|ALL|INDUSTRY TOTAL'];
  for (var q = 0; q < NQ; q++) indRow.push(Math.round(indVols[q]));
  lines.push(indRow.join('|'));

  // All data rows for current segment
  for (var i = 0; i < ROWS.length; i++) {
    if (ROWS[i][0] !== currentSegment) continue;
    var r = ROWS[i];
    var row = [r[1], r[2], r[3], r[4]];
    for (var q = 0; q < NQ; q++) row.push(r[5 + q]);
    lines.push(row.join('|'));
  }
  return lines.join('\n');
}
```

### buildCrossSegSummary()

Provides annual totals for OTHER segments so the AI can answer cross-segment questions without having all their row-level data:

```javascript
function buildCrossSegSummary() {
  // For each segment other than current:
  //   Sum all rows per FY and output as Segment|FY16|FY17|...|FY26
  // This allows cross-segment comparison at the annual level
  var allSegs = ['PV','2W','MHCV','LCV','3W'];
  var otherSegs = allSegs.filter(function(s) {
    return s !== currentSegment;
  });
  // ... sum rows per FY for each other segment
  // ... output as pipe-delimited annual totals
}
```

---

## 9. Prompt Caching for Cost Efficiency

### How It Works

Anthropic prompt caching stores system prompt content server-side. On repeat calls with the same system prompt, cached tokens are read at 90% discount.

### Implementation

The key is in the `system` parameter of the API call:

```javascript
system: [{
  type: 'text',
  text: buildSystemPrompt(),
  cache_control: { type: 'ephemeral' }
}]
```

The `cache_control: {type: "ephemeral"}` tells Anthropic to cache this content block. The cache is:

- **Content-based**: Same text = cache hit, regardless of session
- **Auto-expiring**: ~5 minutes TTL (time to live)
- **Per-model**: Cache is specific to the model used
- **Minimum size**: Must be at least 1024 tokens (easily met with our data)

### Cost Impact

For a typical segment with ~500 rows:
- System prompt: ~60,000 tokens
- First call: 60K input tokens at full price (~$0.18)
- Subsequent calls (within 5 min): 60K tokens at 10% price (~$0.018)
- **90% cost reduction on repeat queries**

### Cache Monitoring

```javascript
if (data.usage) {
  var u = data.usage;
  var cacheRead = u.cache_read_input_tokens || 0;
  var cacheCreate = u.cache_creation_input_tokens || 0;
  if (cacheRead > 0) {
    console.log('[Chat Cost] Cache READ: ' + cacheRead + ' (90% cheaper)');
  } else if (cacheCreate > 0) {
    console.log('[Chat Cost] Cache WRITE: ' + cacheCreate + ' (first call)');
  }
}
```

Check the browser console to verify caching is working. You should see "Cache READ" on the second and subsequent messages.

---

## 10. Sending Messages to the API

### The sendChatMessage() Function

```javascript
async function sendChatMessage(userText) {
  if (!userText || !userText.trim()) return;
  userText = userText.trim();

  // Hide suggestion cards after first message
  document.getElementById('chat-suggestions').style.display = 'none';

  // Add user message to history and DOM
  var userMsg = addChatMessage('user', userText);
  var container = document.getElementById('chat-messages');
  container.appendChild(createMsgDiv(userMsg));
  container.scrollTop = container.scrollHeight;

  // Clear input
  document.getElementById('chat-input').value = '';
  showTypingIndicator();

  // Build API messages (last 20 messages for context)
  var apiMessages = chatHistory.slice(-21, -1)
    .concat([{role:'user', content:userText}])
    .map(function(m) { return {role: m.role, content: m.content}; })
    .filter(function(m) {
      return m.role === 'user' || m.role === 'assistant';
    });

  // Ensure alternating user/assistant (API requirement)
  var cleaned = [];
  for (var i = 0; i < apiMessages.length; i++) {
    if (cleaned.length === 0 ||
        cleaned[cleaned.length-1].role !== apiMessages[i].role) {
      cleaned.push(apiMessages[i]);
    }
  }
  if (cleaned.length > 0 && cleaned[0].role !== 'user')
    cleaned.shift();

  try {
    var response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': chatApiKey,
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 4096,
        system: [{
          type: 'text',
          text: buildSystemPrompt(),
          cache_control: { type: 'ephemeral' }
        }],
        messages: cleaned
      })
    });

    removeTypingIndicator();

    if (!response.ok) {
      // Handle HTTP errors (401, 429, 529, etc.)
      var errData = {};
      try { errData = await response.json(); } catch(e2) {}
      var errMsg =
        response.status === 401 ? 'Invalid API key.'
        : response.status === 429 ? 'Rate limited. Please wait.'
        : response.status === 529 ? 'Claude is overloaded.'
        : 'API error (' + response.status + ')';
      var errMsgObj = addChatMessage('assistant', errMsg);
      container.appendChild(createMsgDiv(errMsgObj));
      return;
    }

    var data = await response.json();
    var assistantText = data.content[0].text || 'No response.';

    // Log cache usage (see Cost Management section)
    logCacheUsage(data.usage);

    var assistantMsg = addChatMessage('assistant', assistantText);
    container.appendChild(createMsgDiv(assistantMsg));
    container.scrollTop = container.scrollHeight;

  } catch(err) {
    removeTypingIndicator();
    var networkErr = addChatMessage('assistant',
      'Network error: ' + err.message);
    container.appendChild(createMsgDiv(networkErr));
  }
}
```

### Conversation History Management

- **Last 20 messages**: We send the most recent 20 messages as context
- **Alternating roles**: The API requires strict user/assistant alternation
- **Deduplication**: If two consecutive messages have the same role, the duplicate is dropped
- **First message must be user**: If history starts with assistant, it is removed

### Error Handling

| Status Code | Meaning | User Message |
|-------------|---------|--------------|
| 401 | Invalid API key | Check your key |
| 429 | Rate limited | Wait and retry |
| 529 | Overloaded | Try again shortly |
| Other | Server error | Shows status code |
| Network | Connection failed | Check internet |

---

## 11. Response Parsing

### parseAssistantResponse()

The AI response is plain text that may contain special code-fenced blocks. We parse these into typed segments:

```javascript
function parseAssistantResponse(text) {
  const segments = [];
  const regex = /```(js|javascript|chart|table)\n([\s\S]*?)```/g;
  let last = 0, match;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > last) {
      segments.push({type: 'text', content: text.slice(last, match.index)});
    }
    let type = match[1];
    if (type === 'javascript') type = 'js';
    segments.push({type, content: match[2]});
    last = regex.lastIndex;
  }
  if (last < text.length) {
    segments.push({type: 'text', content: text.slice(last)});
  }
  return segments;
}
```

### Segment Types

| Type | Fence | Content | Rendered As |
|------|-------|---------|-------------|
| text | (none) | Markdown text | HTML via simpleMarkdown() |
| js | ` ```js ` | JavaScript code | Run in browser, result displayed |
| chart | ` ```chart ` | Plotly JSON spec | Interactive Plotly chart |
| table | ` ```table ` | JSON with headers/rows | HTML table |

### How It Works

1. The regex scans for ` ```js `, ` ```chart `, or ` ```table ` blocks
2. Text between blocks becomes "text" segments
3. Content inside blocks becomes typed segments
4. The array of segments is rendered in order

---

## 12. Rendering Segments

### renderSegment() — The Type Dispatcher

```javascript
function renderSegment(seg, container, msgId) {
  if (seg.type === 'text') {
    // Convert markdown to HTML
    const d = document.createElement('div');
    d.innerHTML = simpleMarkdown(seg.content.trim());
    container.appendChild(d);

  } else if (seg.type === 'js') {
    // Run code and show result
    const result = executeChatCode(seg.content);
    const d = document.createElement('div');
    d.className = 'chat-code-result';
    if (result.success) {
      d.textContent = result.result !== undefined
        ? String(result.result) : '(executed)';
    } else {
      d.className += ' chat-code-error';
      d.textContent = 'Error: ' + result.error;
    }
    container.appendChild(d);

  } else if (seg.type === 'chart') {
    renderChatChart(seg, container, msgId);

  } else if (seg.type === 'table') {
    renderChatTable(seg, container);
  }
}
```

### simpleMarkdown() — Minimal Markdown Converter

We use a lightweight markdown converter (not a full library) that handles the basics:

```javascript
function simpleMarkdown(text) {
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>');
}
```

This handles: bold, italic, inline code, and line breaks. For a production app, consider marked.js for full markdown support.

---

## 13. Code Execution in Browser

### executeChatCode()

```javascript
function executeChatCode(code) {
  try {
    var result = (0, function(c){ return Function('return (' + c + ')')(); })(code);
    return { success: true, result: result };
  } catch(e) {
    return { success: false, error: e.message };
  }
}
```

### Why Dynamic Code Execution?

The AI generates JavaScript code that references the dashboard data functions (`getIndustryVols`, `getCompanyVols`, `filterRows`, `sumVolumes`, etc.). Dynamic execution allows this code to run in the same scope as the dashboard, with full access to:

- All data access functions
- Raw data arrays (ROWS, Q, FYS, etc.)
- Utility functions (fmt, computeShare, annualVols, etc.)
- Constants (NQ, NFY, QLABELS, PALETTE, COMPANY_COLORS)

### Security Considerations

- Code runs in the browser context — it can only affect the current page
- The code is generated by Claude, not by untrusted users
- There is no server-side execution
- The user has already trusted the app with their API key
- For public-facing apps, consider sandboxing (iframe, Web Worker)

### What the AI Can Compute

The system prompt tells the AI about available helper functions:

```
- getIndustryVols(sub), getCompanyVols(co, sub)
- getStateIndustryVols(state, sub), getStateCompanyVols(state, co, sub)
- getZoneIndustryVols(zone, sub), getZoneCompanyVols(zone, co, sub)
- filterRows(company, state, subseg, zone) -> row indices
- sumVolumes(rowIdxs) -> quarterly array
- annualVols(qVols) -> annual FY array
- computeShare(coVols, indVols) -> percentage array
- fmt(n) -> formatted string with commas
```

---

## 14. Chart Rendering from AI Responses

### How It Works

When the AI wants to show a chart, it outputs a ` ```chart ` block containing Plotly JSON:

```json
{
  "data": [
    {"x": ["Q1FY24","Q2FY24","Q3FY24"], "y": [45.2, 44.8, 46.1],
     "type": "scatter", "mode": "lines", "name": "Maruti Suzuki"}
  ],
  "layout": {"title": "Market Share Trend", "yaxis": {"title": "%"}}
}
```

### Rendering Code

```javascript
// Inside renderSegment() for type === 'chart':
const chartDiv = document.createElement('div');
chartDiv.className = 'chat-chart-container';
const chartId = 'chat-chart-' + msgId + '-' + Date.now();
const plotDiv = document.createElement('div');
plotDiv.id = chartId;
plotDiv.style.height = '400px';
chartDiv.appendChild(plotDiv);
container.appendChild(chartDiv);

// Parse and render with setTimeout for DOM attachment
const spec = JSON.parse(seg.content);
const traces = spec.data || spec.traces || [];
const layout = {
  ...PLOTLY_LAYOUT,
  margin: {l:70, r:30, t:30, b:90},
  ...(spec.layout || {})
};
setTimeout(function() {
  Plotly.newPlot(chartId, traces, layout, PLOTLY_CONFIG);
}, 50);
```

### Key Details

- **setTimeout(50ms)**: The DOM element must be attached before Plotly can render
- **PLOTLY_LAYOUT defaults**: Consistent styling with the rest of the dashboard
- **Copy button**: Each chart gets a copy-to-clipboard button using Plotly.toImage()
- **Error handling**: If JSON parsing fails, an error message is shown instead

### Copy Chart to Clipboard

```javascript
copyBtn.onclick = function() {
  Plotly.toImage(chartId, {format:'png', width:900, height:500})
    .then(function(url) {
      fetch(url).then(r => r.blob()).then(function(blob) {
        navigator.clipboard.write([
          new ClipboardItem({'image/png': blob})
        ]);
      });
    });
};
```

---

## 15. Table Rendering from AI Responses

### Format

The AI outputs ` ```table ` blocks with JSON:

```json
{
  "headers": ["Company", "FY25 Vol", "FY24 Vol", "YoY Growth"],
  "rows": [
    ["Maruti Suzuki", 500000, 480000, "4.2%"],
    ["Hyundai", 200000, 195000, "2.6%"]
  ]
}
```

### Rendering

```javascript
const spec = JSON.parse(seg.content);
let html = '<table><thead><tr>'
  + (spec.headers || []).map(h => '<th>' + h + '</th>').join('')
  + '</tr></thead><tbody>';
(spec.rows || []).forEach(function(row) {
  html += '<tr>' + row.map(function(c) {
    return '<td>' + c + '</td>';
  }).join('') + '</tr>';
});
html += '</tbody></table>';
d.innerHTML = html;
```

---

## 16. Save and Export Feature

### Star/Save Toggle

Each assistant message gets a star button. Clicking it toggles the saved flag:

```javascript
function toggleSaveMessage(msgId) {
  for (var i = 0; i < chatHistory.length; i++) {
    if (chatHistory[i].id === msgId) {
      chatHistory[i].saved = !chatHistory[i].saved;
      break;
    }
  }
  saveChatHistory();
  // Update star button visual
  var btn = document.querySelector(
    '[data-msg-id="' + msgId + '"] .chat-save-btn');
  if (btn) btn.classList.toggle('saved');
}
```

### Export as HTML Report

The export function generates a standalone HTML file containing all saved messages:

```javascript
function exportSavedMessages() {
  var saved = chatHistory.filter(function(m) { return m.saved; });
  if (saved.length === 0) {
    alert('No saved messages to export. Star messages first.');
    return;
  }

  // Build standalone HTML document with styling
  var html = '<!DOCTYPE html><html>...<style>...</style>...<body>';
  html += '<h1>Saved Insights - ' + currentSegment + '</h1>';

  saved.forEach(function(msg) {
    var segments = parseAssistantResponse(msg.content);
    segments.forEach(function(seg) {
      if (seg.type === 'text') {
        html += '<div>' + simpleMarkdown(seg.content) + '</div>';
      } else if (seg.type === 'chart') {
        // Capture chart as base64 image via Plotly.toImage()
      } else if (seg.type === 'table') {
        // Render table HTML directly
      }
    });
  });

  // Trigger download
  var blob = new Blob([html], {type: 'text/html'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'insights_' + currentSegment + '.html';
  a.click();
}
```

---

## 17. Download Data CSV

A button allows users to download the current segment data as CSV for use with external AI tools (ChatGPT, Claude web, etc.):

```javascript
document.getElementById('btn-chat-download-data')
  .addEventListener('click', function() {
    var lines = [];
    lines.push('Segment,Subsegment,Zone,State,Manufacturer,' + Q.join(','));
    for (var i = 0; i < ROWS.length; i++) {
      if (ROWS[i][0] !== currentSegment) continue;
      var r = ROWS[i];
      var row = [r[0], r[1], r[2], r[3], r[4]];
      for (var q = 0; q < NQ; q++) row.push(r[5+q]);
      lines.push(row.join(','));
    }
    var blob = new Blob([lines.join('\n')], {type:'text/csv'});
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = currentSegment + '_data.csv';
    a.click();
});
```

This gives users flexibility — they can use the built-in chat or export data for use elsewhere.

---

## 18. Cost Management and Monitoring

### Token Usage Breakdown

| Component | Tokens (approx.) | Notes |
|-----------|-------------------|-------|
| System prompt (role + instructions) | ~500 | Fixed |
| Data metadata | ~200 | Per segment |
| Raw data (pipe-delimited) | 40,000-80,000 | Depends on segment size |
| Cross-segment summary | ~500 | Annual totals only |
| Helper functions + rules | ~400 | Fixed |
| Conversation history | ~2,000 | Last 20 messages |
| AI response | ~500-2,000 | Variable |

### Cost Per Query (Approximate)

| Scenario | Input Cost | Output Cost | Total |
|----------|-----------|-------------|-------|
| First message (cache write) | $0.18 | $0.01 | ~$0.19 |
| Subsequent messages (cache read) | $0.018 | $0.01 | ~$0.03 |
| **Average over 10 messages** | | | **~$0.05/msg** |

### Monitoring in Console

The app logs cache usage to the browser console:

```
[Chat Cost] Input: 65000 tokens, Cache WRITE: 62000 (first call), Output: 800
[Chat Cost] Input: 65500 tokens, Cache READ: 62000 (90% cheaper), Output: 1200
```

Open DevTools (F12) > Console to see these logs.

### Tips for Cost Reduction

1. **Prompt caching**: Already implemented — 90% savings on system prompt
2. **Message history limit**: We send only last 20 messages, not the full history
3. **Segment-specific data**: Only current segment data is sent, not all segments
4. **Pipe-delimited format**: ~30% fewer tokens than CSV, ~60% fewer than JSON
5. **Use Claude Sonnet**: Better cost/performance ratio than Opus for this task

---

## 19. Adaptation Guide for Other Apps

### Step-by-Step: Adding AI Chat to Your Web App

#### Step 1: Define Your Data Format

Identify what data your AI needs. Create a function that serializes it as pipe-delimited text:

```javascript
function buildMyAppData() {
  var lines = [];
  lines.push('Column1|Column2|Column3');  // Header
  myData.forEach(function(row) {
    lines.push(row.col1 + '|' + row.col2 + '|' + row.col3);
  });
  return lines.join('\n');
}
```

#### Step 2: Write Your System Prompt

Follow the 6-layer structure:

```javascript
function buildSystemPrompt() {
  return 'You are an expert analyst for [YOUR DOMAIN].\n\n' +
    'INSTRUCTIONS: You have the complete dataset below...\n\n' +
    'DATA METADATA:\n' + buildMetadata() + '\n\n' +
    'REFERENCE INFO:\n...' +
    '=== COMPLETE DATA ===\n' + buildMyAppData() + '\n\n' +
    'AVAILABLE FUNCTIONS:\n- myFunc1(), myFunc2()...\n\n' +
    'OUTPUT FORMATS:\n1. Text (markdown)\n2. ```js blocks\n' +
    '3. ```chart blocks\n4. ```table blocks\n\n' +
    'RULES:\n- Always cite numbers from the data...';
}
```

#### Step 3: Copy the API Call Pattern

Use the `sendChatMessage()` function as a template. The key parts are:
- The `anthropic-dangerous-direct-browser-access` header
- The `cache_control: {type: "ephemeral"}` on system content
- The message history alternation logic

#### Step 4: Copy the Response Pipeline

1. `parseAssistantResponse()` — splits response into segments
2. `renderSegment()` — dispatches to type-specific renderers
3. `executeChatCode()` — for js blocks
4. Chart rendering — for chart blocks
5. Table rendering — for table blocks

#### Step 5: Expose Your Functions to Dynamic Code

Any function you want the AI to call in js blocks must be in the global scope. List them in the system prompt so the AI knows about them.

### Checklist for Replication

- [ ] HTML structure (setup screen + chat interface)
- [ ] CSS for message bubbles, typing indicator, code results
- [ ] API key storage and management (localStorage)
- [ ] System prompt with complete data
- [ ] sendChatMessage() with caching headers
- [ ] parseAssistantResponse() regex parser
- [ ] renderSegment() type dispatcher
- [ ] executeChatCode() for JS blocks
- [ ] Plotly chart rendering for chart blocks
- [ ] Table rendering for table blocks
- [ ] Chat history persistence (localStorage)
- [ ] Export saved messages feature
- [ ] Error handling (401, 429, 529, network errors)
- [ ] Console logging for cost monitoring

---

## 20. Common Pitfalls

### 1. Forgetting the Browser Access Header

Without `anthropic-dangerous-direct-browser-access: true`, CORS will block the request. The error will look like a network error, not a clear CORS message.

### 2. Non-Alternating Messages

The Anthropic API requires strict user/assistant alternation. If two user messages are consecutive, the API returns an error. Always clean the message array:

```javascript
var cleaned = [];
for (var i = 0; i < messages.length; i++) {
  if (cleaned.length === 0 ||
      cleaned[cleaned.length-1].role !== messages[i].role) {
    cleaned.push(messages[i]);
  }
}
if (cleaned.length > 0 && cleaned[0].role !== 'user')
  cleaned.shift();
```

### 3. System Prompt Too Small for Caching

Prompt caching requires a minimum of 1024 tokens in the system content. If your data is small, pad the system prompt with additional context or instructions.

### 4. Cache Not Working

Check:
- Is `cache_control: {type: "ephemeral"}` on the system content block?
- Is the system content structured as an array of objects, not a plain string?
- Is the content identical between calls? (Any change invalidates the cache)
- Are you within the 5-minute TTL window?

### 5. Charts Not Rendering

Common issues:
- The DOM element must exist before Plotly.newPlot() is called — use setTimeout()
- The chart container needs explicit height (Plotly does not auto-size to content)
- The AI might output invalid JSON — always wrap in try/catch

### 6. Scope Issues with Dynamic Code

Code from js blocks runs in the global scope. If your helper functions are inside a module or IIFE, the AI-generated code will not be able to access them. Ensure all functions listed in the system prompt are globally accessible.

### 7. Large Data Exceeding Context Window

If your dataset is too large for the model context, consider:
- Sending only relevant subsets (like we do per segment)
- Summarizing older data (annual instead of quarterly)
- Using pipe-delimited format to minimize tokens
- Splitting into multiple system content blocks

### 8. API Key Exposure in Network Tab

The API key is visible in the browser DevTools Network tab. This is expected and acceptable for personal/team tools. For public-facing applications, use a backend proxy instead of direct browser-to-API calls.

---

*Document generated: March 2026*
*For the Janchor Auto Tracker codebase — build_dashboard.py*
*Companion to: CODEBASE_MANUAL.md*
