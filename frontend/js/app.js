/**
 * HouseWise - Intelligent Property Valuation
 * Works with both local development and Docker deployment
 */

// Auto-detect API URL (works locally and in Docker)
const API_BASE_URL = window.location.origin;

// Mobile drawer functions
function openDrawer() {
    const drawer = document.querySelector('.mobile-drawer');
    const overlay = document.querySelector('.drawer-overlay');
    if (drawer) drawer.classList.add('open');
    if (overlay) overlay.classList.add('open');
}

function closeDrawer() {
    const drawer = document.querySelector('.mobile-drawer');
    const overlay = document.querySelector('.drawer-overlay');
    if (drawer) drawer.classList.remove('open');
    if (overlay) overlay.classList.remove('open');
}

// Complete state reset function
function resetState() {
    currentState = {
        extractedFeatures: {},
        missingFields: [],
        originalQuery: '',
        step: 'input',
        currentQuestionIndex: 0,
        waitingForAnswer: false,
        currentField: null,
        collectedValues: {}
    };
    hasMessages = false;
}

let currentState = {
    extractedFeatures: {},
    missingFields: [],
    originalQuery: '',
    step: 'input',
    currentQuestionIndex: 0,
    waitingForAnswer: false,
    currentField: null,
    collectedValues: {}
};

let hasMessages = false;

const FIELD_CONFIG = {
    bedrooms: { label: 'bedrooms', icon: '🛏️', question: 'How many bedrooms does the property have?', type: 'number', placeholder: 'e.g., 3' },
    bathrooms: { label: 'bathrooms', icon: '🚿', question: 'How many bathrooms does the property have?', type: 'number', placeholder: 'e.g., 2' },
    sqft_living: { label: 'living area', icon: '📐', question: 'What is the living area in square feet?', type: 'number', placeholder: 'e.g., 1800' },
    sqft_lot: { label: 'lot area', icon: '📏', question: 'What is the lot area in square feet?', type: 'number', placeholder: 'e.g., 10000' },
    year_built: { label: 'year built', icon: '📅', question: 'What year was the property built?', type: 'number', placeholder: 'e.g., 2005' },
    garage_cars: { label: 'garage capacity', icon: '🚗', question: 'How many cars can the garage hold?', type: 'number', placeholder: 'e.g., 2' },
    condition: { label: 'condition', icon: '🔧', question: 'Rate the condition from 1 (poor) to 10 (excellent):', type: 'number', placeholder: 'e.g., 5' },
    quality: { label: 'quality', icon: '⭐', question: 'Rate the overall quality from 1 (poor) to 10 (excellent):', type: 'number', placeholder: 'e.g., 6' },
    heating: { label: 'heating type', icon: '🔥', question: 'What type of heating does it have? (GasA, GasW, Wall, Grav, OthW)', type: 'text', placeholder: 'e.g., GasA' },
    central_air: { label: 'central air', icon: '❄️', question: 'Does it have central air conditioning? (Y/N)', type: 'text', placeholder: 'Y or N' },
    basement: { label: 'basement quality', icon: '🏠', question: 'What is the basement quality? (Ex, Gd, TA, Fa, Po, None)', type: 'text', placeholder: 'e.g., TA' },
    neighborhood: { label: 'neighborhood', icon: '🏘️', question: 'Which neighborhood is the property in?', type: 'text', placeholder: 'e.g., NAmes, StoneBr' }
};

function extractNumberFromText(text) {
    if (!text) return NaN;
    const match = text.match(/\d+\.?\d*/);
    if (match) return parseFloat(match[0]);
    return NaN;
}

function parseGarageAnswer(text) {
    const lower = text.toLowerCase().trim();
    if (lower === 'no garage' || lower === 'none' || lower === '0') return 0;
    return extractNumberFromText(text);
}

function navigateTo(page) {
    closeDrawer();
    
    const pages = ['pageChat', 'pageInfo', 'pageData', 'pageAffects'];
    pages.forEach(p => {
        const el = document.getElementById(p);
        if (el) el.classList.add('hidden');
    });
    
    const targetPage = document.getElementById(`page${page.charAt(0).toUpperCase() + page.slice(1)}`);
    if (targetPage) targetPage.classList.remove('hidden');
    
    const navBtns = document.querySelectorAll('.nav-btn');
    navBtns.forEach(btn => {
        btn.classList.remove('active', 'bg-primary', 'text-white', 'shadow-md');
        btn.classList.add('text-gray-600', 'hover:bg-gray-100');
    });
    
    const activeBtn = document.getElementById(`nav${page.charAt(0).toUpperCase() + page.slice(1)}`);
    if (activeBtn) {
        activeBtn.classList.add('active', 'bg-primary', 'text-white', 'shadow-md');
        activeBtn.classList.remove('text-gray-600', 'hover:bg-gray-100');
    }
    
    const bottomItems = document.querySelectorAll('.bottom-nav-item');
    bottomItems.forEach(item => {
        item.classList.remove('active');
    });
    
    const bottomNavMap = {
        'chat': 0,
        'info': 1,
        'data': 3,
        'affects': 4
    };
    const index = bottomNavMap[page];
    if (index !== undefined && bottomItems[index]) {
        bottomItems[index].classList.add('active');
    }

    if (page === 'data') {
        loadTrainingData();
    }
}

function addMessage(content, isUser = false) {
    const chatMessages = document.getElementById('chatMessages');
    const centeredIcon = document.getElementById('centeredIcon');
    
    if (!hasMessages && chatMessages && centeredIcon) {
        hasMessages = true;
        centeredIcon.classList.add('hidden');
        chatMessages.classList.remove('hidden');
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex ${isUser ? 'justify-end user-message' : 'justify-start ai-message'} message-animate`;
    
    if (isUser) {
        messageDiv.innerHTML = `<div class="bg-gradient-to-r from-primary to-secondary text-white rounded-2xl rounded-tr-none p-3 max-w-md shadow-sm"><p class="text-sm">${escapeHtml(content)}</p></div>`;
    } else {
        messageDiv.innerHTML = `<div class="bg-white rounded-2xl rounded-tl-none shadow-sm border border-gray-100 p-4 max-w-md"><div class="flex items-center gap-2 mb-2"><div class="w-6 h-6 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center"><i class="fas fa-robot text-white text-xs"></i></div><span class="font-semibold text-gray-800 text-sm">AI Assistant</span></div><div class="text-gray-600 text-sm">${content}</div></div>`;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function setLoading(loading) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const sendBtn = document.getElementById('sendBtn');
    if (loadingIndicator) {
        if (loading) loadingIndicator.classList.remove('hidden');
        else loadingIndicator.classList.add('hidden');
    }
    if (sendBtn) sendBtn.disabled = loading;
}

let trainingDataCache = null;

async function loadTrainingData() {
    const loadingBar = document.getElementById('trainingDataLoading');
    const errorBox = document.getElementById('trainingDataError');
    const contentSection = document.getElementById('trainingDataContent');

    if (loadingBar) loadingBar.classList.remove('hidden');
    if (errorBox) errorBox.classList.add('hidden');
    if (contentSection) contentSection.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/api/training-data`);
        if (!response.ok) throw new Error(`Server responded with status ${response.status}`);
        const data = await response.json();
        trainingDataCache = data;
        renderTrainingData(data);
        return data;
    } catch (error) {
        if (errorBox) {
            errorBox.textContent = `Unable to load training data: ${error.message}`;
            errorBox.classList.remove('hidden');
        }
        console.error('Training data error:', error);
        return null;
    } finally {
        if (loadingBar) loadingBar.classList.add('hidden');
    }
}

function renderTrainingData(data) {
    if (!data) return;
    
    const formatCurrency = (value) => `$${Number(value).toLocaleString()}`;

    const totalRowsEl = document.getElementById('statTotalRows');
    const medianPriceEl = document.getElementById('statMedianPrice');
    const meanPriceEl = document.getElementById('statMeanPrice');
    
    if (totalRowsEl) totalRowsEl.textContent = Number(data.stats.total_rows).toLocaleString();
    if (medianPriceEl) medianPriceEl.textContent = formatCurrency(data.stats.median_price);
    if (meanPriceEl) meanPriceEl.textContent = formatCurrency(data.stats.mean_price);

    const featuresBody = document.getElementById('selectedFeaturesBody');
    if (featuresBody) {
        featuresBody.innerHTML = data.selected_features.map(f => `
            <tr class="border-b border-gray-100 hover:bg-gray-50">
                <td class="px-4 py-3 font-medium text-gray-900">${f.name}</td>
                <td class="px-4 py-3 text-gray-600">${f.description}</td>
                <td class="px-4 py-3"><span class="px-2 py-1 rounded-full text-xs font-medium ${f.impact === 'High' ? 'bg-green-100 text-green-700' : f.impact === 'Medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'}">${f.impact}</span></td>
                <td class="px-4 py-3 text-gray-500 text-sm">${f.explanation || '—'}</td>
            </tr>
        `).join('');
    }

    const sampleHeader = document.getElementById('sampleDataHeader');
    const sampleBody = document.getElementById('sampleDataBody');
    const sampleColumns = ['Bedroom AbvGr', 'bathrooms', 'Gr Liv Area', 'Lot Area', 'Year Built', 'Garage Cars', 'Overall Qual', 'SalePrice'];
    
    if (sampleHeader) {
        sampleHeader.innerHTML = `<tr>${sampleColumns.map(col => `<th class="px-4 py-3 text-left text-gray-600 font-medium">${col}</th>`).join('')}</tr>`;
    }
    
    if (sampleBody) {
        sampleBody.innerHTML = data.sample_data.map(row => `
            <tr class="border-b border-gray-100 hover:bg-gray-50">
                ${sampleColumns.map(col => `<td class="px-4 py-3 text-gray-700">${row[col] ?? '—'}</td>`).join('')}
            </tr>
        `).join('');
    }

    const correlationBars = document.getElementById('correlationBars');
    if (correlationBars) {
        correlationBars.innerHTML = Object.entries(data.correlations).map(([feature, correlation]) => {
            const width = Math.min(100, Math.max(0, Math.round(correlation * 100)));
            return `
                <div>
                    <div class="flex justify-between text-sm mb-1"><span>${feature}</span><span class="font-semibold text-primary">${(correlation * 100).toFixed(1)}%</span></div>
                    <div class="h-2 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-gradient-to-r from-primary to-secondary rounded-full" style="width: ${width}%"></div></div>
                </div>
            `;
        }).join('');
    }

    const contentSection = document.getElementById('trainingDataContent');
    if (contentSection) contentSection.classList.remove('hidden');
}

function addExtractedMessage(extracted) {
    const nonNullEntries = Object.entries(extracted).filter(([_, v]) => v !== null && v !== undefined && v !== 'None');
    
    if (nonNullEntries.length === 0) {
        addMessage("I couldn't extract any property details from your description. Could you please provide more specific information?");
        return;
    }
    
    let featuresHtml = '<div class="flex flex-wrap gap-2 mt-2">';
    for (const [key, value] of nonNullEntries) {
        const icons = { bedrooms: '🛏️', bathrooms: '🚿', neighborhood: '🏘️', basement: '🏠', quality: '⭐', condition: '🔧', garage_cars: '🚗', year_built: '📅', sqft_living: '📐', sqft_lot: '📏', heating: '🔥', central_air: '❄️' };
        featuresHtml += `<span class="bg-green-50 text-green-700 px-2 py-1 rounded-full text-xs">${icons[key] || '📝'} ${key}: ${value}</span>`;
    }
    featuresHtml += '</div>';
    addMessage(`I've extracted these details from your description:${featuresHtml}`);
}

function startMissingQuestions(missingFields, resetCollected = true, showIntroMessage = true) {
    if (!missingFields || missingFields.length === 0) {
        calculatePrediction();
        return;
    }
    
    if (showIntroMessage) {
        const totalQuestions = missingFields.length;
        const progressText = totalQuestions === 1 ? "one more detail" : `${totalQuestions} more details`;
        addMessage(`I need ${progressText} to give you an accurate estimate. Let's go through them one by one:`);
    }
    
    currentState.missingFields = missingFields;
    currentState.currentQuestionIndex = 0;
    currentState.waitingForAnswer = true;
    if (resetCollected) {
        currentState.collectedValues = {};
    }
    askNextQuestion();
}

function askNextQuestion() {
    if (currentState.currentQuestionIndex >= currentState.missingFields.length) {
        calculatePrediction();
        return;
    }
    const field = currentState.missingFields[currentState.currentQuestionIndex];
    const config = FIELD_CONFIG[field];
    if (!config) {
        console.warn(`Unknown missing field requested: ${field}. Skipping it.`);
        currentState.currentQuestionIndex++;
        askNextQuestion();
        return;
    }
    
    const currentNum = currentState.currentQuestionIndex + 1;
    const total = currentState.missingFields.length;
    const progressIndicator = total > 1 ? ` (${currentNum}/${total})` : '';
    
    currentState.currentField = field;
    addMessage(`${config.icon} ${config.question}${progressIndicator}`);
    currentState.waitingForAnswer = true;
}

async function handleUserAnswer(answer) {
    if (!currentState.waitingForAnswer) return;
    addMessage(answer, true);
    
    const field = currentState.currentField;
    const config = FIELD_CONFIG[field];
    let value = answer.trim();
    
    if (config) {
        if (field === 'garage_cars') {
            value = parseGarageAnswer(value);
            if (isNaN(value)) {
                addMessage(`❌ Please enter a valid number for garage capacity (0-5).`);
                return;
            }
        } else if (['bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 'year_built', 'condition', 'quality'].includes(field)) {
            let extractedNum = extractNumberFromText(value);
            if (!isNaN(extractedNum)) {
                value = extractedNum;
            } else {
                value = parseFloat(value);
            }
            if (isNaN(value)) {
                addMessage(`❌ Please enter a valid number for ${config.label}.`);
                return;
            }
        }
    }
    
    currentState.collectedValues[field] = value;
    currentState.currentQuestionIndex++;
    currentState.waitingForAnswer = false;
    askNextQuestion();
}

async function calculatePrediction() {
    const missingCollected = currentState.missingFields.filter(field =>
        currentState.collectedValues[field] === undefined ||
        currentState.collectedValues[field] === null ||
        currentState.collectedValues[field] === ''
    );

    const overrideFeatures = { ...currentState.extractedFeatures, ...currentState.collectedValues };

    if (missingCollected.length > 0) {
        addMessage(`Still missing: ${missingCollected.join(', ')}. Please provide these.`);
        currentState.currentQuestionIndex = currentState.missingFields.findIndex(f => missingCollected.includes(f));
        askNextQuestion();
        return;
    }

    addMessage("✨ Perfect! I have all the information I need. Let me calculate your property's value...");
    setLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, { 
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify({ query: currentState.originalQuery, override_features: overrideFeatures }) 
        });
        const data = await response.json();
        setLoading(false);
        
        if (data.status === 'complete') {
            displayPriceResult(data.predicted_price, data.explanation, data.key_factors, data.comparison);
            currentState.step = 'result';
            currentState.waitingForAnswer = false;
        } else if (data.status === 'incomplete') {
            const missing = data.missing_fields || [];
            const extracted = data.extracted_features || {};

            const filteredExtracted = {};
            for (const [key, value] of Object.entries(extracted)) {
                if (value !== null && value !== undefined) {
                    filteredExtracted[key] = value;
                }
            }

            currentState.extractedFeatures = { ...currentState.extractedFeatures, ...filteredExtracted };
            currentState.missingFields = missing;
            currentState.step = 'missing';
            currentState.currentQuestionIndex = 0;
            currentState.waitingForAnswer = false;
            currentState.currentField = null;

            addMessage(`I still need ${missing.length} more detail(s): ${missing.join(', ')}. Let's continue:`);
            startMissingQuestions(missing, false, false);
        } else {
            addMessage(`❌ Sorry, I couldn't calculate the price. ${data.message || 'Please try again.'}`); 
        }
    } catch (error) { 
        setLoading(false);
        addMessage('❌ Error connecting to the valuation service. Please make sure the backend is running.'); 
    }
}

function displayPriceResult(price, explanation, keyFactors, comparison) {
    const gaugePercent = Math.min(100, Math.max(0, ((price - 120000) / 130000) * 100));
    let factorsHtml = '<div class="flex flex-wrap gap-2 mt-3">';
    if (keyFactors && keyFactors.length) { 
        keyFactors.forEach(f => { 
            factorsHtml += `<span class="bg-blue-50 text-blue-700 px-3 py-1.5 rounded-full text-xs font-medium">${f}</span>`; 
        }); 
    }
    factorsHtml += '</div>';
    
    const comparisonText = comparison || (price > 160000 ? 'Above median' : 'Below median');
    const comparisonColor = price > 160000 ? 'text-success' : 'text-warning';
    
    const resultMessage = `
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-5 max-w-md">
            <div class="text-center mb-4">
                <div class="text-4xl font-bold text-primary">$${price.toLocaleString()}</div>
                <div class="text-sm ${comparisonColor} mt-1 font-medium">${comparisonText}</div>
            </div>
            <div class="bg-gray-100 rounded-full h-1.5 mb-4 overflow-hidden">
                <div class="bg-gradient-to-r from-green-500 via-yellow-500 to-blue-600 h-1.5 rounded-full transition-all duration-500" style="width: ${gaugePercent}%"></div>
            </div>
            <div class="text-gray-600 text-sm leading-relaxed mb-4">${explanation}</div>
            <div class="border-t border-gray-100 pt-3">
                <div class="text-xs font-semibold text-gray-500 mb-2">📊 Key value drivers</div>
                ${factorsHtml}
            </div>
        </div>
    `;
    
    addMessage(resultMessage);
}

async function handleSendMessage() {
    const queryInput = document.getElementById('queryInput');
    const query = queryInput?.value.trim();
    if (!query) return;

    // If waiting for answer, handle user response
    if (currentState.waitingForAnswer) { 
        await handleUserAnswer(query); 
        queryInput.value = ''; 
        queryInput.style.height = '48px'; 
        return; 
    }
    
    // New conversation - reset state
    if (currentState.step === 'input' || currentState.step === 'result') {
        console.log("Starting new conversation");
        resetState();
        // Clear chat messages visually
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            while (chatMessages.children.length > 0) {
                chatMessages.removeChild(chatMessages.lastChild);
            }
        }
        const centeredIcon = document.getElementById('centeredIcon');
        if (centeredIcon) {
            centeredIcon.classList.remove('hidden');
            if (chatMessages) chatMessages.classList.add('hidden');
        }
        hasMessages = false;
    }
    
    addMessage(query, true);
    queryInput.value = '';
    queryInput.style.height = '48px';
    setLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, { 
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify({ query, override_features: null }) 
        });
        const data = await response.json();
        setLoading(false);
        
        if (data.status === 'complete') { 
            // COMPLETE: Show price immediately
            displayPriceResult(data.predicted_price, data.explanation, data.key_factors, data.comparison); 
            currentState.step = 'result';
            currentState.waitingForAnswer = false;
        } else if (data.status === 'incomplete') {
            // INCOMPLETE: Extract features and ask for missing
            const extracted = data.extracted_features || {};
            const missing = data.missing_fields || [];
            
            const filteredExtracted = {};
            for (const [key, value] of Object.entries(extracted)) {
                if (value !== null && value !== undefined) {
                    filteredExtracted[key] = value;
                }
            }
            
            currentState = { 
                extractedFeatures: filteredExtracted, 
                missingFields: missing, 
                originalQuery: query, 
                step: 'missing', 
                currentQuestionIndex: 0, 
                waitingForAnswer: false, 
                currentField: null, 
                collectedValues: {} 
            };
            
            // Show what was extracted
            if (Object.keys(filteredExtracted).length > 0) {
                addExtractedMessage(filteredExtracted);
            }
            
            // Start asking for missing fields
            if (missing.length > 0) {
                const totalQuestions = missing.length;
                const progressText = totalQuestions === 1 ? "one more detail" : `${totalQuestions} more details`;
                addMessage(`I need ${progressText} to give you an accurate estimate. Let's go through them one by one:`);
                startMissingQuestions(missing, true, false);
            } else {
                // Should not happen - if no missing, should be complete
                calculatePrediction();
            }
        } else { 
            addMessage(`Sorry, I encountered an issue: ${data.message || 'Please try again.'}`); 
        }
    } catch (error) { 
        setLoading(false);
        addMessage('Sorry, I cannot connect to the valuation service. Please make sure the backend is running on port 8000.'); 
    }
}

function resetChat() {
    resetState();  // Reset state FIRST
    
    navigateTo('chat');
    
    const chatMessages = document.getElementById('chatMessages');
    const centeredIcon = document.getElementById('centeredIcon');
    
    if (chatMessages) {
        while (chatMessages.children.length > 0) {
            chatMessages.removeChild(chatMessages.lastChild);
        }
        chatMessages.classList.add('hidden');
    }
    if (centeredIcon) {
        centeredIcon.classList.remove('hidden');
    }
    
    const queryInput = document.getElementById('queryInput');
    if (queryInput) {
        queryInput.value = '';
        queryInput.style.height = '48px';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    resetState();  // ← ADD THIS - Initialize state on page load
    navigateTo('chat');
    
    const sendBtn = document.getElementById('sendBtn');
    const newChatBtn = document.getElementById('newChatBtn');
    const queryInput = document.getElementById('queryInput');
    
    if (sendBtn) sendBtn.addEventListener('click', handleSendMessage);
    if (newChatBtn) newChatBtn.addEventListener('click', resetChat);
    
    if (queryInput) {
        queryInput.addEventListener('keydown', (e) => { 
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage(); 
            }
        });
        queryInput.addEventListener('input', function() { 
            this.style.height = 'auto'; 
            const newHeight = Math.min(this.scrollHeight, 120);
            this.style.height = newHeight + 'px'; 
        });
    }
});