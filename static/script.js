// ============================================================================
// ADAPTIVE LEARNING SYSTEM - Frontend Integration Script
// Integrates all API endpoints and manages student learning flow
// ============================================================================

const API_BASE_URL = 'http://localhost:5002/api';
let currentStudent = null;
let currentQuestion = null;
let questionHistory = [];
let isAnswerRevealed = false;

// ============================================================================
// INITIALIZATION & SESSION MANAGEMENT
// ============================================================================

/**
 * Initialize the application on page load
 */
function initializeApp() {
    console.log('🚀 Initializing Adaptive Learning System...');
    console.log('🚀 API_BASE_URL:', API_BASE_URL);
    
    // Check if student is already logged in
    const savedStudentId = localStorage.getItem('studentId');
    const savedStudentName = localStorage.getItem('studentName');
    
    console.log('🚀 Saved session:', { savedStudentId, savedStudentName });
    
    if (savedStudentId && savedStudentName) {
        console.log('✅ Found existing session:', savedStudentName);
        currentStudent = {
            id: savedStudentId,
            name: savedStudentName,
            chapter: localStorage.getItem('chapter') || 'chapter_1'
        };
        console.log('✅ Loaded student:', currentStudent);
        
        console.log('🎓 Showing main UI for returning student...');
        showMainUI();
        
        console.log('📊 Loading progress...');
        loadProgress();
        
        console.log('📚 Loading categories...');
        loadCategories();
    } else {
        console.log('ℹ️ No existing session, showing auth panel');
        showAuthPanel();
    }
}

/**
 * Show authentication panel
 */
function showAuthPanel() {
    document.getElementById('authPanel').style.display = 'block';
    document.getElementById('mainHeader').style.display = 'none';
    document.getElementById('categorySection').style.display = 'none';
    document.getElementById('questionSection').style.display = 'none';
    document.getElementById('dashboardSection').style.display = 'none';
    document.getElementById('studentPanel').style.display = 'none';
}

/**
 * Show main learning UI
 */
function showMainUI() {
    console.log('🎓 Showing main learning UI');
    
    document.getElementById('authPanel').style.display = 'none';
    console.log('  ✅ Hidden authPanel');
    
    document.getElementById('mainHeader').style.display = 'block';
    console.log('  ✅ Showed mainHeader');
    
    document.getElementById('categorySection').style.display = 'block';
    console.log('  ✅ Showed categorySection');
    
    document.getElementById('questionSection').style.display = 'block';
    console.log('  ✅ Showed questionSection');
    
    document.getElementById('dashboardSection').style.display = 'block';
    console.log('  ✅ Showed dashboardSection');
    
    document.getElementById('studentPanel').style.display = 'flex';
    console.log('  ✅ Showed studentPanel');
    
    // Update student panel
    if (currentStudent) {
        const nameElement = document.getElementById('studentName');
        if (nameElement) {
            nameElement.textContent = currentStudent.name;
            console.log('  ✅ Updated student name:', currentStudent.name);
        } else {
            console.warn('  ⚠️ studentName element not found');
        }
    }
}

// ============================================================================
// STUDENT REGISTRATION & AUTHENTICATION
// ============================================================================

/**
 * Register a new student
 */
async function registerStudent() {
    const nameInput = document.getElementById('studentNameInput');
    const chapterSelect = document.getElementById('chapterSelect');
    
    const studentName = nameInput.value.trim();
    const selectedChapterName = chapterSelect.value;
    
    console.log('📝 Registration attempt:', { studentName, selectedChapterName });
    
    if (!studentName) {
        showAlert('❌ Please enter your name', 'error');
        return;
    }
    
    try {
        console.log('📝 Registering student:', studentName);
        
        const requestBody = {
            name: studentName,
            chapter: selectedChapterName
        };
        
        console.log('📝 Request body:', requestBody);
        
        const response = await fetch(`${API_BASE_URL}/student/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        console.log('📝 Registration response status:', response.status, response.ok);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }
        
        const data = await response.json();
        console.log('✅ Student registered successfully:', data);
        
        // Store student info in localStorage
        currentStudent = {
            id: data.student_id,
            name: data.name,
            chapter: selectedChapterName
        };
        
        console.log('💾 Stored student info:', currentStudent);
        
        localStorage.setItem('studentId', currentStudent.id);
        localStorage.setItem('studentName', currentStudent.name);
        localStorage.setItem('chapter', currentStudent.chapter);
        
        console.log('💾 Saved to localStorage');
        
        // Clear form and show main UI
        nameInput.value = '';
        console.log('🎓 Calling showMainUI()...');
        showMainUI();
        
        // Load initial data
        console.log('📊 Calling loadProgress()...');
        await loadProgress();
        
        console.log('📚 Calling loadCategories()...');
        await loadCategories();
        
        showAlert('🎉 Welcome to Adaptive Learning, ' + studentName + '!', 'success');
    } catch (error) {
        console.error('❌ Registration error:', error);
        showAlert('❌ ' + error.message, 'error');
    }
}

/**
 * Logout student
 */
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        console.log('👋 Logging out...');
        
        localStorage.removeItem('studentId');
        localStorage.removeItem('studentName');
        localStorage.removeItem('chapter');
        
        currentStudent = null;
        currentQuestion = null;
        questionHistory = [];
        
        showAuthPanel();
        showAlert('👋 You have been logged out', 'info');
    }
}

// ============================================================================
// CATEGORY & QUESTION MANAGEMENT
// ============================================================================

/**
 * Load available categories and populate the UI
 */
async function loadCategories() {
    try {
        console.log('📚 Loading categories from:', `${API_BASE_URL}/categories`);
        
        const response = await fetch(`${API_BASE_URL}/categories`);
        
        console.log('📚 Categories response status:', response.status, response.ok);
        
        if (!response.ok) {
            throw new Error(`Failed to load categories: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('📚 Categories data received:', data);
        
        const categories = data.categories || [];
        console.log('📚 Number of categories:', categories.length);
        
        // Populate category grid
        const categoryGrid = document.getElementById('categoryGrid');
        
        if (!categoryGrid) {
            console.error('❌ categoryGrid element not found in DOM');
            return;
        }
        
        categoryGrid.innerHTML = '';
        
        categories.forEach((category, index) => {
            console.log(`Creating category button ${index + 1}:`, category.name);
            
            const categoryBtn = document.createElement('button');
            categoryBtn.className = 'category-btn';
            categoryBtn.innerHTML = `
                <span class="category-icon">${category.icon}</span>
                <div class="category-name">${category.name}</div>
                <div class="category-desc">${category.description}</div>
            `;
            categoryBtn.onclick = () => selectCategory(category.id);
            categoryGrid.appendChild(categoryBtn);
        });
        
        console.log('✅ Categories loaded successfully:', categories.length, 'categories');
    } catch (error) {
        console.error('❌ Error loading categories:', error);
        showAlert('❌ Failed to load categories: ' + error.message, 'error');
    }
}

/**
 * Select a category and fetch an adaptive question
 */
async function selectCategory(categoryKey) {
    if (!currentStudent) {
        showAlert('❌ Please register first', 'error');
        return;
    }
    
    try {
        console.log('🎯 Selecting category:', categoryKey);
        isAnswerRevealed = false;
        
        const response = await fetch(`${API_BASE_URL}/question`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                studentId: currentStudent.id,
                chapter: categoryKey
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fetch question');
        }
        
        const data = await response.json();
        currentQuestion = data;
        
        console.log('✅ Question loaded:', data);
        
        // Display the question
        displayQuestion(data);
        
        // Clear previous answer state
        document.getElementById('resultDiv').innerHTML = '';
        document.getElementById('misconceptionAlert').style.display = 'none';
        
    } catch (error) {
        console.error('❌ Error fetching question:', error);
        showAlert('❌ ' + error.message, 'error');
    }
}

/**
 * Display question on the UI
 */
function displayQuestion(questionData) {
    // Store the correct answer index
    currentQuestion = {
        ...questionData,
        correct_answer_index: questionData.correctOptionIndex || questionData.correctIndex
    };
    
    // Display question text and metadata
    document.getElementById('questionText').innerHTML = `
        <div class="question-header">
            <h3>${questionData.question || questionData.topic}</h3>
            <div class="question-metadata">
                <span class="category-badge">${questionData.chapter || 'Question'}</span>
            </div>
        </div>
    `;
    
    // Display options
    const optionsDiv = document.getElementById('optionsDiv');
    optionsDiv.innerHTML = '';
    
    const options = questionData.options || [];
    options.forEach((option, index) => {
        const optionBtn = document.createElement('button');
        optionBtn.className = 'option-btn';
        optionBtn.innerHTML = `
            <span class="option-letter">${String.fromCharCode(65 + index)}.</span>
            <span class="option-text">${option}</span>
        `;
        optionBtn.onclick = () => selectAnswer(index);
        optionsDiv.appendChild(optionBtn);
    });
    
    console.log('✅ Question displayed');
}

/**
 * Select an answer
 */
async function selectAnswer(selectedIndex) {
    if (!currentQuestion || isAnswerRevealed) return;
    
    try {
        console.log('📤 Submitting answer:', selectedIndex);
        
        const questionId = currentQuestion.questionId || currentQuestion.id;
        const response = await fetch(`${API_BASE_URL}/check-answer/${questionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                selectedIndex: selectedIndex,
                studentId: currentStudent.id
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to check answer');
        }
        
        const data = await response.json();
        isAnswerRevealed = true;
        
        console.log('✅ Answer checked:', data);
        
        // Display result
        displayAnswerResult(data, selectedIndex);
        
        // Update progress
        await loadProgress();
        
    } catch (error) {
        console.error('❌ Error checking answer:', error);
        showAlert('❌ ' + error.message, 'error');
    }
}

/**
 * Display answer result
 */
function displayAnswerResult(result, selectedIndex) {
    const resultDiv = document.getElementById('resultDiv');
    const isCorrect = result.isCorrect;
    
    resultDiv.className = isCorrect ? 'result success' : 'result error';
    resultDiv.innerHTML = `
        <div class="result-content">
            <h4>${isCorrect ? '✅ Correct!' : '❌ Incorrect'}</h4>
            <p>${isCorrect ? 'Great job!' : 'The correct answer is: ' + (result.answer || '')}</p>
            ${result.solutionSteps && result.solutionSteps.length > 0 ? 
                `<p class="explanation"><strong>Solution:</strong><br>${result.solutionSteps.join('<br>')}</p>` : ''}
        </div>
    `;
    resultDiv.style.display = 'block';
    
    // Highlight options
    const optionBtns = document.querySelectorAll('.option-btn');
    optionBtns.forEach((btn, idx) => {
        if (idx === result.correctIndex) {
            btn.style.backgroundColor = '#4CAF50';
            btn.style.color = 'white';
        } else if (idx === selectedIndex && !isCorrect) {
            btn.style.backgroundColor = '#f44336';
            btn.style.color = 'white';
        }
    });
}

/**
 * Display misconception feedback
 */
function displayMisconceptionFeedback(result) {
    const alertDiv = document.getElementById('misconceptionAlert');
    const teachingPointsList = document.getElementById('teachingPointsList');
    
    alertDiv.style.display = 'block';
    
    // Display misconception text
    document.getElementById('misconceptionText').innerHTML = `
        <strong>💡 Learning Opportunity:</strong><br>
        <em>${result.misconception_details.misconception_type}</em>
    `;
    
    // Display teaching points
    teachingPointsList.innerHTML = '';
    if (result.misconception_details.teaching_points && 
        result.misconception_details.teaching_points.length > 0) {
        
        result.misconception_details.teaching_points.forEach(point => {
            const li = document.createElement('li');
            li.textContent = point;
            teachingPointsList.appendChild(li);
        });
    }
    
    // Display remediation strategy
    if (result.misconception_details.remediation_strategy) {
        const strategyDiv = document.createElement('div');
        strategyDiv.className = 'remediation-strategy';
        strategyDiv.innerHTML = `
            <strong>📚 Suggested Learning Path:</strong><br>
            ${result.misconception_details.remediation_strategy}
        `;
        alertDiv.appendChild(strategyDiv);
    }
    
    console.log('✅ Misconception feedback displayed');
}

/**
 * Get next adaptive question
 */
async function getNextQuestion() {
    if (!currentStudent) {
        showAlert('❌ Please register first', 'error');
        return;
    }
    
    try {
        console.log('➡️ Getting next adaptive question...');
        
        // Use the same chapter as previous question
        const chapter = currentQuestion.chapter;
        
        const response = await fetch(`${API_BASE_URL}/question`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                studentId: currentStudent.id,
                chapter: chapter
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fetch next question');
        }
        
        const data = await response.json();
        currentQuestion = data;
        isAnswerRevealed = false;
        
        console.log('✅ Next question loaded');
        
        // Reset UI and display new question
        document.getElementById('resultDiv').innerHTML = '';
        document.getElementById('misconceptionAlert').style.display = 'none';
        displayQuestion(data);
        
    } catch (error) {
        console.error('❌ Error fetching next question:', error);
        showAlert('❌ ' + error.message, 'error');
    }
}

// ============================================================================
// PROGRESS & ANALYTICS
// ============================================================================

/**
 * Load student progress
 */
async function loadProgress() {
    if (!currentStudent) return;
    
    try {
        console.log('📊 Loading progress...');
        
        const response = await fetch(`${API_BASE_URL}/student/${currentStudent.id}/progress`);
        
        if (!response.ok) {
            throw new Error('Failed to load progress');
        }
        
        const data = await response.json();
        
        console.log('✅ Progress loaded:', data);
        
        // Update progress bar
        const accuracy = data.accuracyRate * 100;
        const totalAttempts = data.attemptCount || 1;
        const correctAttempts = data.correctCount || 0;
        
        document.getElementById('progressFill').style.width = accuracy + '%';
        document.getElementById('progressText').textContent = 
            `${correctAttempts} correct out of ${totalAttempts} attempts`;
        
        // Update Bloom's level
        updateBloomLevel(data.currentBloomLevel);
        
        // Update student panel stats
        document.getElementById('accuracyRate').textContent = Math.round(accuracy) + '%';
        document.getElementById('bloomLevel').textContent = data.currentBloomLevel;
        document.getElementById('attemptsCount').textContent = totalAttempts;
        
        // Show misconceptions if any
        if (data.misconceptionsEncountered && data.misconceptionsEncountered.length > 0) {
            // Could display misconception list if needed
            console.log('Misconceptions:', data.misconceptionsEncountered);
        }
        
    } catch (error) {
        console.error('❌ Error loading progress:', error);
    }
}

/**
 * Update Bloom's level display
 */
function updateBloomLevel(level) {
    const descriptions = {
        'Remember': 'Recognizing and recalling facts and concepts',
        'Understand': 'Explaining ideas or concepts',
        'Apply': 'Using information in a new situation',
        'Analyze': 'Drawing connections among ideas',
        'Evaluate': 'Justifying a decision or choice',
        'Create': 'Producing new or original work'
    };
    
    document.getElementById('bloomLevelDisplay').textContent = level;
    document.getElementById('levelDescription').textContent = descriptions[level] || '';
}

/**
 * Display detected misconceptions
 */
function displayMisconceptions(misconceptions) {
    const card = document.getElementById('misconceptionsCard');
    const list = document.getElementById('misconceptionsList');
    
    card.style.display = 'block';
    list.innerHTML = '';
    
    misconceptions.forEach(misc => {
        const item = document.createElement('div');
        item.className = 'misconception-item';
        item.innerHTML = `
            <h4>${misc.misconception_type}</h4>
            <p>${misc.frequency_count} occurrence(s)</p>
        `;
        list.appendChild(item);
    });
    
    console.log('✅ Misconceptions displayed');
}

/**
 * Display recommendations
 */
function displayRecommendations(recommendations) {
    const card = document.getElementById('recommendationsCard');
    const list = document.getElementById('recommendationsList');
    
    card.style.display = 'block';
    list.innerHTML = '';
    
    recommendations.forEach(rec => {
        const item = document.createElement('div');
        item.className = 'recommendation-item';
        item.innerHTML = `
            <p><strong>📌 ${rec}</strong></p>
        `;
        list.appendChild(item);
    });
    
    console.log('✅ Recommendations displayed');
}

/**
 * Show detailed progress report
 */
function showDetailedReport() {
    if (!currentStudent) {
        showAlert('❌ Please register first', 'error');
        return;
    }
    
    const modal = document.getElementById('reportModal');
    modal.style.display = 'block';
    
    // Fetch and populate detailed data
    loadProgressStats();
}

/**
 * Load progress statistics for detailed report
 */
async function loadProgressStats() {
    if (!currentStudent) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/student/${currentStudent.id}/progress`);
        
        if (!response.ok) {
            throw new Error('Failed to load progress');
        }
        
        const data = await response.json();
        
        // Update report values
        document.getElementById('reportAttempts').textContent = data.total_attempts;
        document.getElementById('reportCorrect').textContent = data.correct_answers;
        document.getElementById('reportAccuracy').textContent = 
            Math.round(data.accuracy_percentage) + '%';
        document.getElementById('reportBloomLevel').textContent = data.current_bloom_level;
        
        // Show misconceptions section if any
        if (data.misconceptions && data.misconceptions.length > 0) {
            const section = document.getElementById('misconceptionsSection');
            section.style.display = 'block';
            
            const container = document.getElementById('reportMisconceptions');
            container.innerHTML = '';
            
            data.misconceptions.forEach(misc => {
                const div = document.createElement('div');
                div.className = 'report-misconception';
                div.innerHTML = `
                    <strong>${misc.misconception_type}</strong> (${misc.frequency_count} times)
                    <p>${misc.teaching_points ? misc.teaching_points.join(' • ') : ''}</p>
                `;
                container.appendChild(div);
            });
        }
        
        // Show recommendations section if any
        if (data.recommendations && data.recommendations.length > 0) {
            const section = document.getElementById('recommendationsSection');
            section.style.display = 'block';
            
            const list = document.getElementById('reportRecommendations');
            list.innerHTML = '';
            
            data.recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                list.appendChild(li);
            });
        }
        
    } catch (error) {
        console.error('❌ Error loading progress stats:', error);
    }
}

/**
 * Close progress report modal
 */
function closeReportModal() {
    document.getElementById('reportModal').style.display = 'none';
}

/**
 * Show misconception report
 */
function showMisconceptionReport() {
    showDetailedReport();
    // Scroll to misconceptions section in report
    setTimeout(() => {
        document.getElementById('misconceptionsSection').scrollIntoView();
    }, 100);
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Show alert/notification
 */
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    document.body.appendChild(alertDiv);
    
    // Remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
    
    console.log(`[${type.toUpperCase()}] ${message}`);
}

/**
 * Close modals when clicking outside
 */
window.onclick = function(event) {
    const reportModal = document.getElementById('reportModal');
    if (event.target === reportModal) {
        reportModal.style.display = 'none';
    }
}

/**
 * Initialize app when DOM is ready
 */
document.addEventListener('DOMContentLoaded', initializeApp);
