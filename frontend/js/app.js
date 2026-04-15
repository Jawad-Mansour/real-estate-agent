/**
 * HouseWise - Intelligent Property Valuation
 * Chat-style missing values with clean price display
 */

const API_BASE_URL = 'http://localhost:8000';

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

function navigateTo(page) {
    document.getElementById('pageChat').classList.add('hidden');
    document.getElementById('pageInfo').classList.add('hidden');
    document.getElementById('pageData').classList.add('hidden');
    document.getElementById('pageAffects').classList.add('hidden');
    document.getElementById(`page${page.charAt(0).toUpperCase() + page.slice(1)}`).classList.remove('hidden');
    
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
}

function hideCenteredIcon() {
    const centeredIcon = document.getElementById('centeredIcon');
    const chatMessages = document.getElementById('chatMessages');
    if (!hasMessages && centeredIcon && chatMessages) {
        hasMessages = true;
        centeredIcon.classList.add('hidden');
        chatMessages.classList.remove('hidden');
    }
}

function addMessage(content, isUser = false) {
    hideCenteredIcon();
    
    const chatMessages = document.getElementById('chatMessages');
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

function addExtractedMessage(extracted) {
    let featuresHtml = '<div class="flex flex-wrap gap-2 mt-2">';
    for (const [key, value] of Object.entries(extracted)) {
        if (value !== null) {
            const icons = { bedrooms: '🛏️', bathrooms: '🚿', neighborhood: '🏘️', basement: '🏠' };
            featuresHtml += `<span class="bg-green-50 text-green-700 px-2 py-1 rounded-full text-xs">${icons[key] || '📝'} ${key}: ${value}</span>`;
        }
    }
    featuresHtml += '</div>';
    addMessage(`I've extracted these details from your description:${featuresHtml}`);
}

function startMissingQuestions(missingFields) {
    currentState.missingFields = missingFields;
    currentState.currentQuestionIndex = 0;
    currentState.waitingForAnswer = true;
    currentState.collectedValues = {};
    askNextQuestion();
}

function askNextQuestion() {
    if (currentState.currentQuestionIndex >= currentState.missingFields.length) {
        calculatePrediction();
        return;
    }
    const field = currentState.missingFields[currentState.currentQuestionIndex];
    const config = FIELD_CONFIG[field] || { label: field, question: `Please provide ${field}:`, type: 'text' };
    currentState.currentField = field;
    addMessage(config.question);
    currentState.waitingForAnswer = true;
}

async function handleUserAnswer(answer) {
    if (!currentState.waitingForAnswer) return;
    addMessage(answer, true);
    const field = currentState.currentField;
    let value = answer.trim();
    if (['bathrooms', 'sqft_living', 'sqft_lot', 'year_built', 'garage_cars', 'condition', 'quality'].includes(field)) {
        value = parseFloat(value);
        if (isNaN(value)) { addMessage(`Please enter a valid number for ${FIELD_CONFIG[field]?.label || field}.`); return; }
    }
    currentState.collectedValues[field] = value;
    currentState.currentQuestionIndex++;
    currentState.waitingForAnswer = false;
    askNextQuestion();
}

async function calculatePrediction() {
    addMessage("Great! Let me calculate the value for you...");
    const overrideFeatures = { ...currentState.extractedFeatures, ...currentState.collectedValues };
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: currentState.originalQuery, override_features: overrideFeatures }) });
        const data = await response.json();
        if (data.status === 'complete') {
            displayPriceResult(data.predicted_price, data.explanation, data.key_factors, data.comparison);
            currentState.step = 'result';
            currentState.waitingForAnswer = false;
        } else { 
            addMessage(`Sorry, I couldn't calculate the price. ${data.message || 'Please try again.'}`); 
            resetChat(); 
        }
    } catch (error) { 
        addMessage('Error connecting to the valuation service. Please make sure the backend is running.'); 
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
        <div class="price-result-card bg-white rounded-2xl shadow-lg border border-gray-100 p-5 max-w-md">
            <div class="text-center mb-4">
                <div class="text-4xl font-bold price-amount">$${price.toLocaleString()}</div>
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
    if (currentState.waitingForAnswer) { await handleUserAnswer(query); queryInput.value = ''; queryInput.style.height = '48px'; return; }
    addMessage(query, true);
    queryInput.value = '';
    queryInput.style.height = '48px';
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query, override_features: null }) });
        const data = await response.json();
        if (data.status === 'incomplete') {
            currentState = { extractedFeatures: data.extracted_features || {}, missingFields: data.missing_fields || [], originalQuery: query, step: 'missing', currentQuestionIndex: 0, waitingForAnswer: false, currentField: null, collectedValues: {} };
            addExtractedMessage(currentState.extractedFeatures);
            addMessage(`I need a few more details to give you an accurate estimate.`);
            startMissingQuestions(currentState.missingFields);
        } else if (data.status === 'complete') { 
            displayPriceResult(data.predicted_price, data.explanation, data.key_factors, data.comparison); 
            currentState.step = 'result'; 
        } else { 
            addMessage(`Sorry, I encountered an issue: ${data.message || 'Please try again.'}`); 
        }
    } catch (error) { 
        addMessage('Sorry, I cannot connect to the valuation service. Please make sure the backend is running on port 8000.'); 
    }
}

function resetChat() {
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
    
    hasMessages = false;
    currentState = { extractedFeatures: {}, missingFields: [], originalQuery: '', step: 'input', currentQuestionIndex: 0, waitingForAnswer: false, currentField: null, collectedValues: {} };
    const queryInput = document.getElementById('queryInput');
    if (queryInput) {
        queryInput.value = '';
        queryInput.style.height = '48px';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    navigateTo('chat');
    document.getElementById('sendBtn')?.addEventListener('click', handleSendMessage);
    document.getElementById('newChatBtn')?.addEventListener('click', resetChat);
    document.getElementById('queryInput')?.addEventListener('keydown', (e) => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') handleSendMessage(); });
    document.getElementById('queryInput')?.addEventListener('input', function() { 
        this.style.height = 'auto'; 
        const newHeight = Math.min(this.scrollHeight, 120);
        this.style.height = newHeight + 'px'; 
    });
});