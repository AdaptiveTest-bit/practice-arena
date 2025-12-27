// Global state
let sessionId = null;
let currentChapter = null;
let currentQuestionId = null;
let questionsGenerated = 0;

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    await createSession();
    await loadCategories();
});

/**
 * Create a new session for deduplication tracking
 */
async function createSession() {
    try {
        const response = await fetch('/api/session', {
            method: 'POST'
        });
        const data = await response.json();
        sessionId = data.sessionId;
        console.log('Session created:', sessionId);
    } catch (error) {
        console.error('Error creating session:', error);
    }
}

/**
 * Load available categories from API
 */
async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const data = await response.json();

        const categoryGrid = document.getElementById('categoryGrid');
        categoryGrid.innerHTML = '';

        data.categories.forEach(category => {
            const btn = document.createElement('button');
            btn.className = 'category-btn';
            btn.innerHTML = `
                <span class="category-icon">${category.icon}</span>
                <div class="category-name">${category.name}</div>
                <div class="category-desc">${category.description}</div>
            `;
            btn.onclick = () => selectCategory(category.id, btn);
            categoryGrid.appendChild(btn);
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

/**
 * Select a category and fetch a question
 */
async function selectCategory(chapterId, buttonElement) {
    // Update active state
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    buttonElement.classList.add('active');

    currentChapter = chapterId;
    await fetchNewQuestion();
}

/**
 * Fetch a new question from the API
 */
async function fetchNewQuestion() {
    if (!currentChapter) {
        alert('Please select a chapter first');
        return;
    }

    if (!sessionId) {
        alert('Session not initialized. Please refresh the page.');
        return;
    }

    // Show loading state
    document.getElementById('questionCard').style.display = 'none';
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('loadingSpinner').style.display = 'flex';

    try {
        const response = await fetch('/api/question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sessionId: sessionId,
                chapter: currentChapter
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(`HTTP ${response.status}: ${errorData.detail || 'Failed to fetch question'}`);
        }

        const data = await response.json();

        if (data.success) {
            currentQuestionId = data.questionId;
            displayQuestion(data);
            questionsGenerated++;
            updateStats();
            document.getElementById('questionCard').style.display = 'block';
        } else {
            throw new Error(data.detail || 'Unknown error');
        }
    } catch (error) {
        console.error('Error fetching question:', error);
        document.getElementById('questionCard').style.display = 'none';
        document.getElementById('emptyState').style.display = 'block';
        alert('Error loading question: ' + error.message);
    } finally {
        // Hide loading state
        document.getElementById('loadingSpinner').style.display = 'none';
    }
}

/**
 * Display the question on the card
 */
function displayQuestion(data) {
    // Update topic badge
    document.getElementById('topicBadge').textContent = data.chapterName;
    document.getElementById('topicBadge').style.background = getCategoryColor(data.chapter);

    // Update question title
    document.getElementById('questionTitle').textContent = data.topic;

    // Update logical trap
    document.getElementById('trapText').textContent = data.logicalTrap;

    // Update data representation
    const dataContainer = document.getElementById('dataRepresentation');
    const dataRep = data.dataRepresentation || '';
    
    // Clear previous content
    dataContainer.innerHTML = '';
    
    // Check what type of data representation this is
    if (dataRep.includes('```')) {
        // It's a code/pre-formatted block
        const code = dataRep
            .replace(/```/g, '')
            .trim();
        const preElem = document.createElement('pre');
        const codeElem = document.createElement('code');
        codeElem.textContent = code;
        preElem.appendChild(codeElem);
        dataContainer.appendChild(preElem);
    } else if (dataRep.includes('|')) {
        // It's a markdown table
        dataContainer.innerHTML = parseMarkdownTable(dataRep);
    } else if (dataRep.trim().length > 0) {
        // It's plain text
        const preElem = document.createElement('pre');
        preElem.textContent = dataRep;
        dataContainer.appendChild(preElem);
    } else {
        dataContainer.innerHTML = '<p>No data to display</p>';
    }

    // Update question text
    document.getElementById('questionText').textContent = data.question;

    // Handle MCQ options
    if (data.options && data.options.length > 0) {
        displayMCQOptions(data.options, data.chapter);
        document.getElementById('mcqOptionsContainer').style.display = 'block';
        document.getElementById('revealSection').style.display = 'none';
    } else {
        document.getElementById('mcqOptionsContainer').style.display = 'none';
        document.getElementById('revealSection').style.display = 'block';
    }

    // Hide solution container
    document.getElementById('solutionContainer').style.display = 'none';

    // Show question card
    document.getElementById('questionCard').style.display = 'block';
}

/**
 * Display MCQ options
 */
function displayMCQOptions(options, category) {
    const optionsList = document.getElementById('optionsList');
    optionsList.innerHTML = '';

    options.forEach((option, index) => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option-item';
        
        const radioBtn = document.createElement('input');
        radioBtn.type = 'radio';
        radioBtn.name = 'question_option';
        radioBtn.value = index;
        radioBtn.id = `option_${index}`;
        radioBtn.onchange = () => highlightOption(index, category);
        
        const label = document.createElement('label');
        label.htmlFor = `option_${index}`;
        label.textContent = `${String.fromCharCode(65 + index)}) ${option}`;
        
        optionDiv.appendChild(radioBtn);
        optionDiv.appendChild(label);
        optionsList.appendChild(optionDiv);
    });
}

/**
 * Highlight selected option
 */
function highlightOption(index, category) {
    const options = document.querySelectorAll('.option-item');
    options.forEach((opt, idx) => {
        if (idx === index) {
            opt.classList.add('selected');
            opt.style.borderLeft = `4px solid ${getCategoryColor(category)}`;
        } else {
            opt.classList.remove('selected');
            opt.style.borderLeft = 'none';
        }
    });
}

/**
 * Submit MCQ answer and auto-reveal
 */
async function submitAnswer() {
    const selectedRadio = document.querySelector('input[name="question_option"]:checked');
    
    if (!selectedRadio) {
        alert('Please select an option first!');
        return;
    }

    const selectedIndex = parseInt(selectedRadio.value);

    try {
        const response = await fetch(`/api/check-answer/${currentQuestionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                selectedIndex: selectedIndex
            })
        });

        const data = await response.json();

        if (data.success) {
            // Disable options after submission
            document.querySelectorAll('input[name="question_option"]').forEach(radio => {
                radio.disabled = true;
            });

            // Highlight correct answer
            const correctOption = document.getElementById(`option_${data.correctIndex}`);
            if (correctOption) {
                correctOption.parentElement.classList.add('correct-answer');
                correctOption.parentElement.style.borderLeft = '4px solid #10b981';
            }

            // Highlight incorrect selection if wrong
            if (!data.isCorrect) {
                selectedRadio.parentElement.classList.add('wrong-answer');
                selectedRadio.parentElement.style.borderLeft = '4px solid #ef4444';
            }

            // Auto-reveal solution
            setTimeout(() => {
                revealSolution(data);
            }, 800);
        }
    } catch (error) {
        console.error('Error submitting answer:', error);
        alert('Error submitting answer. Please try again.');
    }
}

/**
 * Reveal solution after answer submission
 */
function revealSolution(data) {
    const solutionContainer = document.getElementById('solutionContainer');
    const solutionSteps = document.getElementById('solutionSteps');

    solutionSteps.innerHTML = '';
    data.solutionSteps.forEach((step, index) => {
        const li = document.createElement('li');
        li.textContent = step;
        solutionSteps.appendChild(li);
    });

    document.getElementById('answerText').textContent = data.answer;
    solutionContainer.style.display = 'block';

    // Hide MCQ and submit button
    document.getElementById('mcqOptionsContainer').style.display = 'none';
    document.getElementById('revealSection').style.display = 'block';
    document.getElementById('revealBtn').style.display = 'none';

    // Scroll to solution
    solutionContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Reveal the solution
 */
async function revealAnswer() {
    if (!currentQuestionId) return;

    try {
        const response = await fetch(`/api/reveal/${currentQuestionId}`);
        const data = await response.json();

        if (data.success) {
            // Display solution steps
            const stepsList = document.getElementById('solutionSteps');
            stepsList.innerHTML = '';
            data.solutionSteps.forEach(step => {
                const li = document.createElement('li');
                li.textContent = step;
                stepsList.appendChild(li);
            });

            // Display answer
            document.getElementById('answerText').textContent = data.answer;

            // Show solution container
            document.getElementById('solutionContainer').style.display = 'block';
            document.getElementById('revealBtn').style.display = 'none';

            // Scroll to solution
            document.getElementById('solutionContainer').scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }
    } catch (error) {
        console.error('Error revealing answer:', error);
        alert('Error loading solution. Please try again.');
    }
}

/**
 * Parse markdown table to HTML
 */
function parseMarkdownTable(markdown) {
    const lines = markdown.trim().split('\n').filter(line => line.trim());
    
    if (lines.length === 0 || !lines[0].includes('|')) {
        return `<pre><code>${escapeHtml(markdown)}</code></pre>`;
    }

    let html = '<table>';
    let isHeader = true;
    let headerProcessed = false;
    
    lines.forEach((line, index) => {
        // Skip separator lines (|---|---|...)
        if (line.includes('---') && line.includes('|')) {
            return;
        }
        
        const cells = line.split('|')
            .map(cell => cell.trim())
            .filter(cell => cell.length > 0);
        
        if (cells.length === 0) return;

        // First data row is the header
        if (isHeader && !headerProcessed) {
            html += '<thead><tr>';
            cells.forEach(cell => {
                // Remove markdown bold formatting
                const cleanCell = cell.replace(/\*\*/g, '');
                html += `<th>${escapeHtml(cleanCell)}</th>`;
            });
            html += '</tr></thead><tbody>';
            headerProcessed = true;
            isHeader = false;
        } else {
            // Data rows
            html += '<tr>';
            cells.forEach(cell => {
                // Remove markdown bold formatting
                const cleanCell = cell.replace(/\*\*/g, '');
                html += `<td>${escapeHtml(cleanCell)}</td>`;
            });
            html += '</tr>';
        }
    });
    
    html += '</tbody></table>';
    return html;
}

/**
 * Get category color
 */
function getCategoryColor(chapter) {
    const colors = {
        // Boxes & Sketches
        'dice_logic': '#ef4444',
        'cube_counting': '#f59e0b',
        'nets': '#8b5cf6',
        // Data Handling
        'data_handling': '#2563eb',
        // Shapes & Angles
        'clock_angles': '#ec4899',
        'symmetry': '#06b6d4',
        'rotation': '#14b8a6',
        // Number Systems
        'large_numbers': '#10b981',
        'factors_multiples': '#059669',
        // Fractions & Decimals
        'fractions_decimals': '#f97316',
        // Geometry & Measurement
        'geometry_measurement': '#7c3aed',
        // Data & Patterns
        'data_patterns': '#dc2626'
    };
    return colors[chapter] || '#2563eb';
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Update statistics
 */
function updateStats() {
    document.getElementById('questionsGenerated').textContent = questionsGenerated;
}
