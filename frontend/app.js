/* ==========================================
   P Λ R Λ D I T I - AI Powered Government Scheme Recommender
   Frontend Application Logic
   ========================================== */

// --- Configuration & State ---
// Use relative path so it works everywhere (Local and Production)
const API_BASE_URL = '/api';
let currentUser = JSON.parse(localStorage.getItem('paraditi_user'));
let authToken = localStorage.getItem('paraditi_token');
let allUserDocuments = []; // Global store for documents

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    init();
});

function init() {
    // Check if on auth pages
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // Check if on dashboard
    if (window.location.pathname.endsWith('dashboard.html')) {
        if (!authToken) {
            window.location.href = 'login.html';
            return;
        }
        loadDashboard();

        // Setup dashboard event listeners
        const logoutLink = document.getElementById('logoutLink');
        if (logoutLink) logoutLink.addEventListener('click', logout);

        const profileLink = document.getElementById('profileLink');
        if (profileLink) {
            profileLink.addEventListener('click', (e) => {
                e.preventDefault();
                showProfileModal();
            });
        }

        // Fix: Explicitly bind the Update Profile button inside dashboard actions if it doesn't use onclick attribute
        const updateProfileBtn = document.querySelector('button[onclick="showProfileModal()"]');
        if (updateProfileBtn) {
            // It already has an onclick attribute, so no need to double-bind. 
            // However, let's make sure showProfileModal is globally accessible if needed.
        }

        const profileForm = document.getElementById('profileForm');
        if (profileForm) profileForm.addEventListener('submit', updateProfile);

        // PARADITI 3.0, 4.0 & 5.1 Demo Init
        loadLifeJourney();
        loadMobilityRoadmap();
        loadSocialCredit();
    }
}

// --- Authentication ---
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorMsg = document.getElementById('errorMessage');

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('paraditi_token', data.token);
            localStorage.setItem('paraditi_user', JSON.stringify(data.user));
            authToken = data.token;
            currentUser = data.user;
            window.location.href = 'dashboard.html';
        } else {
            errorMsg.textContent = data.error || 'Login failed';
            errorMsg.style.display = 'block';
        }
    } catch (err) {
        errorMsg.textContent = 'Network error. Please try again.';
        errorMsg.style.display = 'block';
        console.error(err);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    const errorMsg = document.getElementById('errorMessage');

    // Basic validation
    if (data.password.length < 8) {
        errorMsg.textContent = 'Password must be at least 8 characters';
        errorMsg.style.display = 'block';
        return;
    }

    // Convert numeric fields
    if (data.age) data.age = parseInt(data.age);
    if (data.income) data.income = parseFloat(data.income);

    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            body: formData // fetch automatically sets Content-Type to multipart/form-data
        });

        const resData = await response.json();

        if (response.ok) {
            localStorage.setItem('paraditi_token', resData.token);
            localStorage.setItem('paraditi_user', JSON.stringify(resData.user));
            window.location.href = 'dashboard.html';
        } else {
            errorMsg.textContent = resData.error || 'Registration failed';
            errorMsg.style.display = 'block';
        }
    } catch (err) {
        errorMsg.textContent = 'Network error. Please try again.';
        errorMsg.style.display = 'block';
        console.error(err);
    }
}

function logout(e) {
    if (e) e.preventDefault();
    localStorage.removeItem('paraditi_token');
    localStorage.removeItem('paraditi_user');
    window.location.href = 'index.html';
}

// --- Dashboard Logic ---
async function loadDashboard() {
    // Load User Profile to ensure fresh data
    try {
        const response = await fetch(`${API_BASE_URL}/profile`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            localStorage.setItem('paraditi_user', JSON.stringify(currentUser));

            const userNameEl = document.getElementById('userName');
            if (userNameEl) userNameEl.textContent = currentUser.name;

            // Load stats and schemes
            loadUserStats();
            loadDocumentLibrary(); // NEW: Load Document Dashboard
            loadRecommendedSchemes();
            loadLifeJourney();
            syncAgentUI();
        } else {
            logout(); // Token invalid
        }
    } catch (err) {
        console.error(err);
    }
}

async function loadUserStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/user-stats`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await response.json();

        if (response.ok) {
            // document.getElementById('viewedCount').textContent = data.viewed_count; // Handled by loadRecommendedSchemes
            document.getElementById('appliedCount').textContent = data.applied_count;
            document.getElementById('totalSchemes').textContent = data.total_schemes;

            // NEW: Universal Beneficiary Score
            const ubsEl = document.getElementById('ubsScore');
            if (ubsEl) {
                ubsEl.textContent = data.beneficiary_score || 0;
                // Animate color based on score
                const color = data.beneficiary_score > 70 ? '#00f2ff' : (data.beneficiary_score > 40 ? '#ff8c00' : '#f43f5e');
                ubsEl.style.color = color;
                ubsEl.style.textShadow = `0 0 15px ${color}88`;
            }
        }
    } catch (err) {
        console.error('Error loading stats:', err);
    }
}

async function loadLifeJourney() {
    const container = document.getElementById('journeyTimeline');
    if (!container) return;

    try {
        const response = await fetch(`${API_BASE_URL}/schemes/recommended`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await response.json();

        if (response.ok) {
            // Sort by age requirements if available, or just use recommended list
            // BACKEND: keys are 'schemes' and 'almost_eligible' (which are already flat objects)
            const schemes = (data.schemes || []).concat(data.almost_eligible || []);

            // Sort by min_age to create a timeline
            schemes.sort((a, b) => (a.min_age || 0) - (b.min_age || 0));

            if (schemes.length === 0) {
                container.innerHTML = '<div class="loading">Complete your profile to unlock your life journey roadmap.</div>';
                return;
            }

            container.innerHTML = schemes.map((s, index) => `
                <div class="journey-step">
                    <span class="step-age">${s.min_age ? 'Ages ' + s.min_age + '+' : 'Life Event ' + (index + 1)}</span>
                    <div class="step-title">${s.name}</div>
                    <div class="step-desc">${s.description ? s.description.substring(0, 80) : 'Welfare and support benefits'}...</div>
                    <a href="#" class="step-link" onclick="showSchemeDetails(${s.id}); return false;">Explore Milestone →</a>
                </div>
            `).join('');
        }
    } catch (err) {
        container.innerHTML = '<div class="loading">Failed to load roadmap.</div>';
    }
}

async function loadRecommendedSchemes() {
    const container = document.getElementById('schemesContainer');
    if (!container) return;

    container.innerHTML = '<div class="loading">Loading recommendations...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/schemes/recommended?limit=50`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await response.json();

        container.innerHTML = '';

        const hasSchemes = data.schemes && data.schemes.length > 0;
        const hasAlmost = data.almost_eligible && data.almost_eligible.length > 0;

        if (!hasSchemes && !hasAlmost) {
            container.innerHTML = '<div class="no-data">No schemes found matching your profile.</div>';
            return;
        }

        // Render Eligible
        if (hasSchemes) {
            const eligibleSection = document.createElement('div');

            // Personalization Feedback
            const profileSummary = [];
            if (currentUser.state) profileSummary.push(currentUser.state);
            if (currentUser.age) profileSummary.push(`${currentUser.age} yrs`);
            if (currentUser.gender) profileSummary.push(currentUser.gender);
            if (currentUser.category) profileSummary.push(currentUser.category);
            const summaryStr = profileSummary.length > 0 ? `Based on: ${profileSummary.join(' • ')}` : 'Complete your profile for better matches';

            eligibleSection.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1.5rem;">
                    <h3 style="margin:0; font-size: 1.5rem; color: #ffffff;">Top Recommendations</h3>
                    <span style="font-size: 0.85rem; color: #00f2ff; background: rgba(0, 242, 255, 0.1); border: 1px solid rgba(0, 242, 255, 0.2); padding: 6px 14px; border-radius: 99px;">${summaryStr}</span>
                </div>`;
            eligibleSection.innerHTML += `<div class="schemes-grid">${data.schemes.map(s => createSchemeCard(s)).join('')}</div>`;
            container.appendChild(eligibleSection);
        }

        // Render Almost Eligible
        if (hasAlmost) {
            const almostSection = document.createElement('div');
            almostSection.style.marginTop = '3rem';
            almostSection.innerHTML = '<h3 style="margin-bottom: 0.5rem; color: #ff00ff; text-shadow: 0 0 10px rgba(255, 0, 255, 0.3);">Almost Eligible</h3><p style="margin-bottom: 1.5rem; color: var(--text-secondary);">Unlock these by updating your profile details.</p>';
            almostSection.innerHTML += `<div class="schemes-grid">${data.almost_eligible.map(s => createSchemeCard(s, true)).join('')}</div>`;
            container.appendChild(almostSection);
        }

        // SYNC: Update the "Eligible Schemes" stat to match the cards shown
        const totalCount = (data.schemes ? data.schemes.length : 0) + (data.almost_eligible ? data.almost_eligible.length : 0);
        const countEl = document.getElementById('viewedCount');
        if (countEl) countEl.textContent = totalCount;

    } catch (err) {
        container.innerHTML = '<div class="error">Failed to load schemes.</div>';
        console.error(err);
    }
}

async function loadAllSchemes() {
    const container = document.getElementById('schemesContainer');
    if (!container) return;

    container.innerHTML = '<div class="loading">Loading all schemes...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/schemes/all`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await response.json();

        renderSchemes(data.schemes);
    } catch (err) {
        container.innerHTML = '<div class="error">Failed to load schemes.</div>';
        console.error(err);
    }
}

function renderSchemes(schemes) {
    const container = document.getElementById('schemesContainer');
    if (!container) return;

    if (schemes.length === 0) {
        container.innerHTML = '<div class="no-data">No schemes found matching your profile.</div>';
        return;
    }

    container.innerHTML = `<div class="schemes-grid">${schemes.map(s => createSchemeCard(s)).join('')}</div>`;
}

function createSchemeCard(scheme, isAlmost = false) {
    let footerContent = '';
    let headerBadge = '';

    if (isAlmost) {
        headerBadge = `<span class="badge" style="background: rgba(255, 0, 255, 0.1); color: #ff00ff; border: 1px solid rgba(255, 0, 255, 0.2); font-size: 0.8rem; padding: 0.35rem 0.75rem; border-radius: 6px;">${scheme.gap_reason}</span>`;

        let alternativeHtml = '';
        if (scheme.alternative) {
            alternativeHtml = `<div style="margin-bottom: 0.75rem; font-size: 0.85rem; color: #00f2ff; padding: 0.75rem; background: rgba(0, 242, 255, 0.05); border: 1px solid rgba(0, 242, 255, 0.1); border-radius: 8px;">
                <strong>💡 Quick Alternative:</strong> <a href="#" onclick="showSchemeDetails(${scheme.alternative.id}); return false;" style="color: #00f2ff; text-decoration: underline; font-weight: 700;">${scheme.alternative.name}</a>
            </div>`;
        }

        footerContent = `
            <div style="width: 100%;">
                ${alternativeHtml}
                <button class="btn btn-outline" onclick="showSchemeDetails(${scheme.id})" style="width: 100%;">View Requirements</button>
            </div>
        `;
    } else {
        headerBadge = scheme.similarity_score ? `<span class="match-score">${Math.round(scheme.similarity_score * 100)}% Match</span>` : '';
        footerContent = `
            <button class="btn btn-outline" onclick="showSchemeDetails(${scheme.id})">View Details</button>
            ${scheme.is_applied
                ? '<button class="btn btn-success" disabled>Applied ✅</button>'
                : `<button class="btn btn-primary" onclick="showSchemeDetails(${scheme.id})">Apply Now</button>`
            }
        `;
    }

    return `
        <div class="scheme-card" ${isAlmost ? 'style="border-left: 4px solid #f43f5e;"' : ''}>
            <div class="scheme-header" style="display: flex; justify-content: space-between; align-items: start; gap: 0.5rem;">
                <h3 style="margin: 0; font-size: 1.1rem;">${scheme.name}</h3>
                ${headerBadge}
            </div>
            <div class="scheme-body">
                <p><strong>Ministry:</strong> ${scheme.ministry}</p>
                <p>${scheme.description ? scheme.description.substring(0, 100) : ''}...</p>
                
                ${scheme.approval_confidence ? `
                <div class="confidence-badge" style="margin-top: 1rem; background: rgba(0, 242, 255, 0.05); padding: 10px; border-radius: 12px; border: 1px solid rgba(0, 242, 255, 0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem;">
                        <span style="opacity: 0.7;">🚀 Approval Confidence:</span>
                        <span style="font-weight: 800; color: ${scheme.approval_confidence > 80 ? '#00f2ff' : (scheme.approval_confidence > 50 ? '#ff8c00' : '#f43f5e')}">${scheme.approval_confidence}%</span>
                    </div>
                </div>` : ''}

                ${scheme.graduation_path && scheme.graduation_path.length > 0 ? `
                <div class="path-badge" style="margin-top: 0.5rem; background: rgba(121, 40, 202, 0.05); padding: 10px; border-radius: 12px; border: 1px solid rgba(121, 40, 202, 0.1);">
                    <div style="font-size: 0.75rem; color: #a1a1aa; margin-bottom: 4px;">🎯 Graduation Path:</div>
                    <div style="font-size: 0.85rem; color: #7928ca; font-weight: 700;">+ ₹${scheme.projected_salary_increase ? scheme.projected_salary_increase.toLocaleString() : '5,000'} Annual ROI</div>
                    <div style="font-size: 0.7rem; color: #71717a; margin-top: 4px;">Skills: ${scheme.skill_tags ? JSON.parse(scheme.skill_tags).join(', ') : 'Vocational'}</div>
                </div>` : ''}

                <div class="benefits-preview" style="margin-top: auto;">
                    <strong>Benefits:</strong> ${scheme.benefits ? scheme.benefits.substring(0, 50) : ''}...
                </div>
            </div>
            <div class="scheme-footer">
                ${footerContent}
            </div>
        </div>
    `;
}

async function showSchemeDetails(schemeId) {
    const modal = document.getElementById('schemeModal');
    const content = document.getElementById('schemeDetails');

    content.innerHTML = '<div class="loading">Loading details...</div>';
    modal.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/schemes/${schemeId}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await response.json();
        const scheme = data.scheme;

        content.innerHTML = `
            <h2>${scheme.name}</h2>
            <div class="scheme-meta">
                <span class="badge">${scheme.ministry}</span>
                <span class="badge">${scheme.category}</span>
                ${scheme.similarity_score ? `<span class="badge match-high">${Math.round(scheme.similarity_score * 100)}% Match</span>` : ''}
            </div>
            
            <div class="scheme-details-section">
                <h3>Description</h3>
                <p>${scheme.description}</p>
            </div>
            
            <div class="scheme-details-section">
                <h3>Benefits</h3>
                <p>${scheme.benefits}</p>
            </div>
            
            <div class="scheme-details-section">
                <h3>Eligibility</h3>
                <p>${scheme.eligibility_criteria}</p>
            </div>
            
            <div class="scheme-actions" style="margin-top: 2rem; display: flex; gap: 1rem; flex-wrap: wrap;">
                ${scheme.official_link ? `<a href="${scheme.official_link}" target="_blank" rel="noopener noreferrer" class="btn btn-outline">🌐 Official Website</a>` : ''}
                <a href="https://www.google.com/search?q=${encodeURIComponent(scheme.name + ' scheme official website')}" target="_blank" rel="noopener noreferrer" class="btn btn-outline">🔍 Search on Google</a>
                ${scheme.is_applied
                ? `<button class="btn btn-success" style="cursor: default">Applied ✅</button>
                       <button class="btn btn-danger" onclick="withdrawApplication(${scheme.id})" style="background-color: #dc3545; color: white; border: none;">Withdraw Application</button>`
                : `<button class="btn btn-primary" onclick="openApplyModal(${scheme.id}, '${scheme.name.replace(/'/g, "\\'")}')">One-Click Apply</button>`
            }
            </div>
        `;

        // Close button handler
        const closeBtn = modal.querySelector('.close');
        closeBtn.onclick = () => modal.style.display = 'none';

        // Click outside to close
        window.onclick = (event) => {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }

    } catch (err) {
        content.innerHTML = '<div class="error">Failed to load details.</div>';
        console.error(err);
    }
}

// --- Apply Modal Logic ---
let currentApplySchemeId = null;

function openApplyModal(schemeId, schemeName) {
    currentApplySchemeId = schemeId;
    document.getElementById('schemeModal').style.display = 'none';
    const modal = document.getElementById('applyModal');

    // Populate review data
    document.getElementById('applySchemeName').textContent = schemeName;
    document.getElementById('reviewName').textContent = currentUser.name;
    document.getElementById('reviewAge').textContent = currentUser.age;
    document.getElementById('reviewIncome').textContent = currentUser.income || 'N/A';

    // Reset views
    document.getElementById('applicationReviewContent').style.display = 'block';
    document.getElementById('applicationSuccess').style.display = 'none';

    modal.style.display = 'block';

    // Bind confirm button
    document.getElementById('confirmApplyBtn').onclick = submitApplication;
}

function closeApplyModal() {
    document.getElementById('applyModal').style.display = 'none';
    currentApplySchemeId = null;
}

async function submitApplication() {
    if (!currentApplySchemeId) return;

    const btn = document.getElementById('confirmApplyBtn');
    const originalText = btn.textContent;
    btn.textContent = 'Compressing Docs...';
    btn.disabled = true;

    try {
        // Simulate "Step 1: Processing" text change for effect
        await new Promise(r => setTimeout(r, 800));
        btn.textContent = 'Auto-filling Form...';

        const response = await fetch(`${API_BASE_URL}/schemes/${currentApplySchemeId}/one_click_apply`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('applicationReviewContent').style.display = 'none';
            document.getElementById('applicationSuccess').style.display = 'block';

            // Show package details in success screen if element exists
            const refEl = document.getElementById('successRefId');
            if (refEl) {
                refEl.innerHTML = `
                    <div style="text-align: left; background: rgba(0, 242, 255, 0.05); padding: 15px; border-radius: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; border: 1px solid rgba(0, 242, 255, 0.2);">
                        <strong style="color: #00f2ff;">APP ID:</strong> ${data.application_id || 'Submitted'}<br>
                        <strong style="color: #00f2ff;">RECEIPT HASH:</strong> ${data.receipt_signature ? data.receipt_signature.substring(0, 24) + '...' : 'N/A'}
                    </div>
                `;
            }

            // Refresh dashboard stats
            loadUserStats();
            loadRecommendedSchemes();
        } else {
            alert(data.error || 'Application failed. ensure you have uploaded documents in your profile.');
        }
    } catch (err) {
        alert('Network error during application');
        console.error(err);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

async function withdrawApplication(schemeId) {
    if (!confirm('Are you sure you want to withdraw your application?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/schemes/${schemeId}/withdraw`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        const data = await response.json();

        if (response.ok) {
            alert('Application withdrawn successfully');
            document.getElementById('schemeModal').style.display = 'none';

            // Refresh dashboard
            loadUserStats();
            loadRecommendedSchemes();
            renderLifeJourney(); // NEW: Load the welfare roadmap
        } else {
            alert(data.error || 'Withdrawal failed');
        }
    } catch (err) {
        console.error(err);
        alert('Network error during withdrawal');
    }
}

// --- Profile Management ---
function showProfileModal() {
    console.log("Opening profile modal, user:", currentUser);
    const modal = document.getElementById('profileModal');
    if (!modal) {
        console.error("Profile modal element not found!");
        return;
    }
    modal.style.display = 'block';

    if (!currentUser) {
        console.warn("Current user is null, fetching...");
        // Fallback or wait?
        return;
    }

    // Fill form
    document.getElementById('profileName').value = currentUser.name || '';
    document.getElementById('profileAge').value = currentUser.age || '';
    document.getElementById('profileGender').value = currentUser.gender || '';
    document.getElementById('profileState').value = currentUser.state || '';
    document.getElementById('profileIncome').value = currentUser.income || '';
    document.getElementById('profileCategory').value = currentUser.category || '';
    document.getElementById('profileOccupation').value = currentUser.occupation || '';
}

function closeProfileModal() {
    document.getElementById('profileModal').style.display = 'none';
}

async function updateProfile(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch(`${API_BASE_URL}/profile`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const resData = await response.json();
            currentUser = resData.user;
            localStorage.setItem('paraditi_user', JSON.stringify(currentUser));
            closeProfileModal();
            loadDashboard(); // Refresh UI
            alert('Profile updated successfully!');
        } else {
            alert('Failed to update profile');
        }
    } catch (err) {
        console.error(err);
        alert('Network error');
    }
}

// --- Document Upload ---
async function uploadDocument() {
    const fileInput = document.getElementById('docFile');
    const docType = document.getElementById('docType').value;

    if (!fileInput.files[0]) {
        alert('Please select a file');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('doc_type', docType);

    const btn = document.getElementById('uploadBtn');
    btn.textContent = 'Uploading...';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/upload-document`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('docStatus').style.display = 'flex';
            document.getElementById('uploadResult').style.display = 'block';

            // Show extracted data
            let html = '<ul style="list-style: none; padding: 0;">';
            for (const [key, value] of Object.entries(data.extracted_data)) {
                if (key !== '_meta') {
                    html += `<li><strong>${key}:</strong> ${value}</li>`;
                }
            }
            html += '</ul>';
            document.getElementById('extractedData').innerHTML = html;

        } else {
            alert(data.error || 'Upload failed');
        }
    } catch (err) {
        console.error(err);
        alert('Upload failed due to network error');
    } finally {
        btn.textContent = 'Upload & Analyze';
        btn.disabled = false;
    }
}

function enableReupload() {
    document.getElementById('docStatus').style.display = 'none';
    document.getElementById('docFile').value = '';
}

/* ==========================================
   PARADITI 3.0 DEMO FEATURES IMPLEMENTATION
   ========================================== */

// --- 1. Life Journey Predictor ---
function renderLifeJourney() {
    const timeline = document.getElementById('lifeJourneyTimeline');
    if (!timeline) return;

    // Simulate user age if not loaded yet
    const currentAge = currentUser ? (currentUser.age || 25) : 25;

    const milestones = [
        { age: currentAge, title: "Today", event: "Active Profile" },
        { age: 30, title: "Marriage", event: "Kanyadan / Shagun Schemes" },
        { age: 35, title: "Family & Housing", event: "PM Awas Yojana (Housing)" },
        { age: 45, title: "Children Education", event: "Post-Matric Scholarship" },
        { age: 60, title: "Retirement", event: "Atal Pension Yojana" }
    ];

    timeline.innerHTML = '';

    milestones.forEach((milestone, index) => {
        // Only show future milestones or current
        if (milestone.age >= currentAge) {
            const item = document.createElement('div');
            item.className = `timeline-item ${index === 0 ? 'active' : ''}`;
            item.innerHTML = `
                <div class="timeline-dot"></div>
                <div class="timeline-year">Age ${milestone.age}</div>
                <div class="timeline-event">${milestone.title}<br><small>${milestone.event}</small></div>
            `;
            timeline.appendChild(item);
        }
    });
}

// --- 2. Scan-to-Scheme (Photo Magic) ---
function triggerScanDemo() {
    document.getElementById('scanInput').click();
}

function processScan(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        const resultDiv = document.getElementById('scanResult');

        // Show loading
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div style="text-align:center">🔍 AI Analyzing Image... (Simulated)</div>';

        // Call Mock API
        const formData = new FormData();
        formData.append('image', file);

        // Note: In a real implementation we would send the file.
        // Here we just trigger the mock endpoint.
        fetch(`${API_BASE_URL}/scan-scheme`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({}) // Sending empty body as it's a mock
        })
            .then(response => response.json())
            .then(data => {
                const analysis = data.analysis;
                let schemesHtml = '';
                analysis.schemes.forEach(s => {
                    schemesHtml += `<li><strong>${s.name}</strong>: ${s.benefit}</li>`;
                });

                resultDiv.innerHTML = `
                <div style="text-align: center; margin-bottom: 10px;">
                    <span style="font-size: 3rem;">⚠️</span>
                </div>
                <h4>${data.message}</h4>
                <p>Confidence: ${analysis.confidence}</p>
                <div style="background: rgba(0,0,0,0.1); padding: 10px; border-radius: 4px; margin-top: 10px;">
                    <strong>Analysis:</strong>
                    <ul style="margin: 5px 0; padding-left: 20px;">
                        ${schemesHtml}
                    </ul>
                </div>
            `;
            })
            .catch(err => {
                console.error(err);
                resultDiv.innerHTML = '<div class="error">Analysis failed. Try again.</div>';
            });
    }
}

// --- 3. PARADITI 4.0: Aditi AI Experience Logic ---

function toggleAditi() {
    const panel = document.getElementById('aditiPanel');
    if (!panel) return;

    if (panel.style.display === 'flex') {
        minimizeAditi();
    } else {
        panel.style.display = 'flex';
        // Animate entrance
        panel.style.animation = 'panel-entry 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards';
        setTimeout(() => {
            const input = document.getElementById('aditiInput');
            if (input) input.focus();
        }, 100);
    }
}

function toggleAditi() {
    const panel = document.getElementById('aditiPanel');
    if (panel) {
        // Toggle logic: if hidden (or empty), show it. If shown, hide it.
        // Note: CSS might set it to display:none initially or via class.
        const currentDisplay = window.getComputedStyle(panel).display;

        if (currentDisplay === 'none') {
            panel.style.display = 'flex'; // Use flex as per CSS likely
            setTimeout(() => {
                const input = document.getElementById('aditiInput');
                if (input) input.focus();
            }, 100);
        } else {
            panel.style.display = 'none';
        }
    }
}

function minimizeAditi() {
    const panel = document.getElementById('aditiPanel');
    if (panel) {
        panel.style.display = 'none';
    }
}

function handleAditiKey(event) {
    if (event.key === 'Enter') {
        sendAditiMessage();
    }
}

async function sendAditiMessage() {
    const input = document.getElementById('aditiInput');
    const message = input.value.trim();
    if (!message) return;

    // Add User Message
    addMessage(message, 'user');
    input.value = '';

    // Show typing
    const typingId = showTypingIndicator();

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        removeTypingIndicator(typingId);

        if (response.ok) {
            const data = await response.json();
            // Render Main Response
            addMessage(data.response, 'bot', true);

            // Render Rich Cards if available
            if (data.rich_cards && data.rich_cards.length > 0) {
                renderRichCards(data.rich_cards);
            }
        } else {
            addMessage('I am having trouble connecting to the Ministry server. Please try again.', 'bot');
        }
    } catch (err) {
        console.error(err);
        removeTypingIndicator(typingId);
        addMessage('Network error. Please check your connection.', 'bot');
    }
}

function askAditi(query) {
    const input = document.getElementById('aditiInput');
    if (input) {
        input.value = query;
        sendAditiMessage();
    }
}

function addMessage(text, type, isHtml = false) {
    const container = document.getElementById('aditiMessages');
    if (!container) return;

    const msgWrapper = document.createElement('div');
    msgWrapper.className = `chat-message ${type}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (isHtml) {
        // Convert markdown-style bolding to HTML
        let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formattedText = formattedText.replace(/\n/g, '<br>');
        contentDiv.innerHTML = formattedText;
    } else {
        contentDiv.textContent = text;
    }

    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = 'Just now';

    msgWrapper.appendChild(contentDiv);
    msgWrapper.appendChild(timeDiv);

    container.appendChild(msgWrapper);
    container.scrollTop = container.scrollHeight;
}

function renderRichCards(cards) {
    const container = document.getElementById('aditiMessages');
    // ... same as before but using addMessage ...
    cards.forEach(card => {
        const cardHtml = `
            <div class="rich-card">
                <h4>${card.title}</h4>
                <p>${card.subtitle || 'Government Scheme'}</p>
                <a href="#" onclick="showSchemeDetails(${card.id}); return false;">${card.link_text || 'View Details'} →</a>
            </div>
        `;
        addMessage(cardHtml, 'bot', true);
    });
}

function showTypingIndicator() {
    const container = document.getElementById('aditiMessages');
    const id = 'typing-' + Date.now();
    const wrapper = document.createElement('div');
    wrapper.className = 'chat-message bot';
    wrapper.id = id;
    wrapper.innerHTML = `
        <div class="message-content" style="padding: 0.5rem 1rem;">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
    `;
    container.appendChild(wrapper);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Make functions globally available for inline onclick handlers
window.showProfileModal = showProfileModal;
window.closeProfileModal = closeProfileModal;
window.loadRecommendedSchemes = loadRecommendedSchemes;
window.loadAllSchemes = loadAllSchemes;
window.syncFromApiSetu = syncFromApiSetu;
window.uploadDocument = uploadDocument;
window.enableReupload = enableReupload;
window.applyExtractedData = applyExtractedData;
window.showSchemeDetails = showSchemeDetails;
window.withdrawApplication = withdrawApplication;
window.openApplyModal = openApplyModal;
window.closeApplyModal = closeApplyModal;
window.submitApplication = submitApplication;

// Chat functions mapping
window.toggleChat = toggleAditi;
window.toggleAditi = toggleAditi;
window.minimizeAditi = minimizeAditi;
window.handleChatKey = handleAditiKey;
window.handleAditiKey = handleAditiKey;
window.sendChatMessage = sendAditiMessage;
window.sendAditiMessage = sendAditiMessage;
window.askAditi = askAditi;

// Placeholder function for sync button
async function syncFromApiSetu() {
    const btn = document.getElementById('syncApisetuBtn');
    if (btn) {
        btn.textContent = 'Syncing...';
        btn.disabled = true;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/schemes/sync`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await response.json();

        if (response.ok) {
            alert(`Sync Successful! Added ${data.added} new schemes and updated ${data.updated} existing ones.`);
            loadRecommendedSchemes();
            loadUserStats(); // Reload stats to show new total
        } else {
            alert(data.error || 'Sync failed.');
        }
    } catch (err) {
        console.error(err);
        alert('Network error during sync.');
    } finally {
        if (btn) {
            btn.textContent = 'Sync from API Setu';
            btn.disabled = false;
        }
    }
}
window.syncFromApiSetu = syncFromApiSetu;

function applyExtractedData() {
    const extractedEl = document.getElementById('extractedData');
    if (!extractedEl) return;

    // The data is rendered as a list in uploadDocument
    // We can try to parse it or just use the global state if we saved it
    // For simplicity, we'll re-fetch the profile as it should have been updated by the backend during upload
    loadDashboard();
    document.getElementById('uploadResult').style.display = 'none';
    alert("Profile auto-filled from verified documents!");
    showProfileModal();
}
window.applyExtractedData = applyExtractedData;

/* ==========================================
   SAHAJ 5.0: INTELLIGENT DOCUMENT DASHBOARD
   ========================================== */


async function loadDocumentLibrary() {
    const grid = document.getElementById('documentLibrary');
    if (!grid) return;

    // Show loading state
    grid.innerHTML = '<div class="loading">Loading Intelligent Document Library...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/documents`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await response.json();

        if (response.ok) {
            allUserDocuments = data.documents;

            // 1. Update Overview Stats
            document.getElementById('docTotalCount').textContent = data.stats.total;
            document.getElementById('docVerifiedCount').textContent = data.stats.verified;
            document.getElementById('docExpiringCount').textContent = data.stats.expiring;
            document.getElementById('docMissingCount').textContent = data.stats.missing;

            // 2. Update Missing Docs Alert
            const missingAlert = document.getElementById('missingDocsAlert');
            const missingListText = document.getElementById('missingDocsList');
            if (data.stats.missing_list && data.stats.missing_list.length > 0) {
                missingAlert.style.display = 'flex';
                missingListText.innerHTML = `Please upload: <strong>${data.stats.missing_list.join(', ')}</strong>`;
            } else {
                missingAlert.style.display = 'none';
            }

            // 3. Render Cards (Default: All)
            renderDocCards(allUserDocuments);
        } else {
            console.error(data.error);
            grid.innerHTML = '<div class="error">Failed to load documents.</div>';
        }
    } catch (err) {
        console.error("Doc Library Error:", err);
        // Differentiate between JSON parse error (server returned HTML 500) and Network Error
        let msg = 'Network error loading library.';
        if (err.message && err.message.includes('JSON')) {
            msg = 'Server Error (Invalid JSON Response). Check server logs.';
        }
        grid.innerHTML = `<div class="error">${msg} <br><small>${err.message}</small></div>`;
    }
}

function renderDocCards(docs) {
    const grid = document.getElementById('documentLibrary');
    grid.innerHTML = '';

    if (docs.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 3rem; background: #f8fafc; border-radius: 12px; border: 2px dashed #e2e8f0;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📂</div>
                <h3 style="color: #64748b;">No Documents Found</h3>
                <p style="color: #94a3b8; margin-bottom: 1.5rem;">Upload your documents to unlock schemes.</p>
                <button class="btn btn-primary" onclick="showUploadModal()">+ Upload First Document</button>
            </div>
        `;
        return;
    }

    docs.forEach(doc => {
        const card = document.createElement('div');
        card.className = 'doc-card';
        card.style.cssText = `
            background: white; border-radius: 12px; padding: 1.25rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0; transition: all 0.2s; position: relative;
        `;

        // Status Colors
        let statusColor = '#94a3b8'; // Pending (Gray)
        let statusIcon = '🔄';
        let statusText = 'Processing';

        if (doc.is_verified) {
            statusColor = '#059669'; // Verified (Green)
            statusIcon = '✅';
            statusText = 'Verified';
        }
        if (doc.expiry_date && new Date(doc.expiry_date) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)) {
            statusColor = '#d97706'; // Expiring (Orange)
            statusIcon = '⚠️';
            statusText = 'Expiring Soon';
        }

        // Size Calculation
        const sizeKb = Math.round(doc.file_size / 1024);
        const originalKb = doc.original_size ? Math.round(doc.original_size / 1024) : sizeKb;
        const savedPercent = originalKb > sizeKb ? Math.round((1 - sizeKb / originalKb) * 100) : 0;

        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                <div style="background: ${statusColor}15; color: ${statusColor}; padding: 0.25rem 0.6rem; border-radius: 99px; font-size: 0.75rem; font-weight: 700; display: inline-flex; align-items: center; gap: 0.25rem;">
                    ${statusIcon} ${statusText}
                </div>
                <!-- Options Menu (Simplified) -->
                <button onclick="deleteDocument(${doc.id})" style="background: none; border: none; cursor: pointer; color: #ef4444; font-size: 1.1rem;" title="Delete">🗑️</button>
            </div>
            
            <div style="display: flex; gap: 1rem; align-items: center; margin-bottom: 1rem;">
                <div style="width: 50px; height: 50px; background: #eff6ff; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">
                    📄
                </div>
                <div>
                    <h4 style="margin: 0; color: #1e293b; font-size: 1rem;">${doc.document_type}</h4>
                    <span style="font-size: 0.8rem; color: #64748b;">${new Date(doc.created_at).toLocaleDateString()}</span>
                </div>
            </div>
            
            <div style="background: #f8fafc; padding: 0.75rem; border-radius: 8px; font-size: 0.85rem; color: #475569; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span>Optimized Size:</span>
                    <span style="font-weight: 600;">${sizeKb} KB</span>
                </div>
                ${savedPercent > 0 ? `
                <div style="display: flex; justify-content: space-between; color: #059669;">
                    <span>Compression:</span>
                    <span style="font-weight: 700;">-${savedPercent}%</span>
                </div>` : ''}
            </div>
            
            <div style="display: flex; gap: 0.5rem;">
                <button class="btn btn-sm btn-outline" style="flex: 1;" onclick="viewDocument(${doc.id})">👁️ View</button>
                <button class="btn btn-sm btn-outline" style="flex: 1;" onclick="alert('Feature coming soon: Replace document')">✏️ Edit</button>
            </div>
        `;
        grid.appendChild(card);
    });
}

function filterDocs(category) {
    // Update active tab
    const tabs = document.getElementById('docCategoryTabs').children;
    for (let btn of tabs) {
        if (btn.textContent === category || (category === 'all' && btn.textContent === 'All')) {
            btn.classList.add('active');
            btn.style.background = 'var(--primary-color)';
            btn.style.color = 'white';
        } else {
            btn.classList.remove('active');
            btn.style.background = 'transparent';
            btn.style.color = 'var(--primary-color)';
        }
    }

    if (category === 'all') {
        renderDocCards(allUserDocuments);
    } else {
        const filtered = allUserDocuments.filter(d => d.category === category);
        renderDocCards(filtered);
    }
}

function searchDocs(query) {
    const q = query.toLowerCase();
    const filtered = allUserDocuments.filter(d =>
        d.document_type.toLowerCase().includes(q) ||
        d.filename.toLowerCase().includes(q) ||
        (d.category && d.category.toLowerCase().includes(q))
    );
    renderDocCards(filtered);
}

// --- Upload Logic ---
function showUploadModal() {
    document.getElementById('uploadModal').style.display = 'block';
    updateDocTypes();
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
    // Reset form
    document.getElementById('uploadDocForm').reset();
    document.getElementById('uploadProgress').style.display = 'none';
}

function updateDocTypes() {
    const category = document.getElementById('uploadCategory').value;
    const typeSelect = document.getElementById('uploadDocType');
    typeSelect.innerHTML = '';

    let options = [];
    if (category === 'Identity') options = ['Aadhaar Card', 'PAN Card', 'Voter ID', 'Driving License'];
    else if (category === 'Income') options = ['Income Certificate', 'Salary Slip', 'ITR'];
    else if (category === 'Address') options = ['Electricity Bill', 'Water Bill', 'Rent Agreement', 'Passport'];
    else if (category === 'Education') options = ['10th Marksheet', '12th Marksheet', 'Degree Certificate'];
    else if (category === 'Bank') options = ['Bank Passbook', 'Cancelled Cheque'];
    else options = ['Other Document'];

    options.forEach(opt => {
        const el = document.createElement('option');
        el.value = opt;
        el.textContent = opt;
        typeSelect.appendChild(el);
    });
}

async function handleUploadSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const btn = document.getElementById('startUploadBtn');
    const progressDiv = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('uploadProgressBar');
    const statusText = document.getElementById('uploadStatusText');

    btn.disabled = true;
    progressDiv.style.display = 'block';

    try {
        // Simulate Compression Step
        statusText.textContent = "AI Agent: Compressing & Optimizing Image...";
        progressBar.style.width = "40%";
        await new Promise(r => setTimeout(r, 800));

        statusText.textContent = "AI Agent: Extracting Data via OCR...";
        progressBar.style.width = "70%";
        await new Promise(r => setTimeout(r, 800));

        statusText.textContent = "Uploading to Secure Vault...";
        progressBar.style.width = "90%";

        const response = await fetch(`${API_BASE_URL}/upload-document`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            progressBar.style.width = "100%";
            statusText.textContent = "Complete!";

            // Refresh Dashboard
            await loadDocumentLibrary();
            closeUploadModal();
            loadUserStats(); // Update stats

        } else {
            alert(data.error || 'Upload failed');
            progressDiv.style.display = 'none';
        }
    } catch (err) {
        console.error(err);
        alert('Network error');
        progressDiv.style.display = 'none';
    } finally {
        btn.disabled = false;
    }
}

async function deleteDocument(id) {
    if (!confirm("Are you sure? This document might be used in active applications.")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/documents/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (response.ok) {
            loadDocumentLibrary(); // Refresh
            loadUserStats();
        } else {
            alert("Failed to delete document");
        }
    } catch (e) {
        console.error(e);
    }
}

async function viewDocument(id) {
    try {
        // Show status
        const btn = document.activeElement;
        const originalText = btn ? btn.innerText : 'View';
        if (btn) btn.innerText = 'Decrypting...';

        const token = localStorage.getItem('paraditi_token');
        if (!token) {
            throw new Error("Authentication token missing. Please login again.");
        }

        const response = await fetch(`${API_BASE_URL}/documents/${id}/view`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (btn) btn.innerText = originalText;

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Failed to verify ownership');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        // Open securely
        const win = window.open(url, '_blank');
        if (!win) {
            alert('Document Decrypted! Please allow popups to view it.');
            // Fallback link
            window.location.href = url;
        }
    } catch (err) {
        console.error(err);
        alert('Security Audit: ' + err.message);
    }
}

// --- 4. Bharat-First: Voice & Mobility Logic ---

async function startVoiceDiscovery() {
    const micBtn = document.getElementById('aditiMicBtn');
    const input = document.getElementById('aditiInput');

    if (micBtn.classList.contains('listening')) {
        micBtn.classList.remove('listening');
        micBtn.textContent = '🎙️';
        return;
    }

    micBtn.classList.add('listening');
    micBtn.textContent = '🔴';
    input.placeholder = "Listening to your dialect...";

    // Simulated Voice-to-Text for demo
    // In production, this would use Web Speech API or custom STT
    setTimeout(async () => {
        micBtn.classList.remove('listening');
        micBtn.textContent = '🎙️';

        const transcripts = [
            "humra laiki ke padhai khatir paisa chai", // Bhojpuri
            "beti ki padhai ke liye bajiifa chahiye", // Hindi
            "kheti ke liye madad chahiye" // General
        ];
        const randomTranscript = transcripts[Math.floor(Math.random() * transcripts.length)];
        input.value = randomTranscript;

        // Call Backend Dialect Mapper
        try {
            const response = await fetch(`${API_BASE_URL}/dialect/query`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ transcript: randomTranscript })
            });
            const data = await response.json();

            if (response.ok) {
                input.placeholder = "Type or speak in your dialect...";
                addMessage(data.greeting, 'bot');
                addMessage(`Mapped Intent: **${data.analysis.mapped_intent.replace(/_/g, ' ')}**`, 'bot');

                // Trigger recommendation search based on intent
                askAditi(`Find ${data.analysis.mapped_intent.replace(/_/g, ' ')} schemes`);
            }
        } catch (e) {
            console.error(e);
        }
    }, 2000);
}

async function loadMobilityRoadmap() {
    const roiEl = document.getElementById('projectedROI');
    const percEl = document.getElementById('roiPercentage');
    const pathEl = document.getElementById('pathSequence');

    if (!roiEl) return;

    try {
        const response = await fetch(`${API_BASE_URL}/mobility/roadmap`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await response.json();

        if (response.ok && data.current_path.length > 0) {
            const path = data.current_path[0];
            const impact = data.economic_impact;

            roiEl.textContent = `₹${Math.round(impact.projected_annual_growth).toLocaleString()}`;
            percEl.textContent = `${impact.roi_percentage} Income Increase`;

            pathEl.innerHTML = `
                <div style="font-size: 1.5rem;">➡️</div>
                <div style="flex: 1;">
                    <strong style="color: var(--secondary-color); font-size: 0.9rem;">NEXT LOGICAL STEP:</strong>
                    <div style="font-size: 1.1rem; font-weight: 700; margin: 0.2rem 0;">${path.next_step.replace(/_/g, ' ')}</div>
                    <div style="font-size: 0.8rem; opacity: 0.7;">Goal: ${path.goal}</div>
                </div>
            `;
        }
    } catch (e) {
        console.error("Mobility Error:", e);
    }
}

// --- 5. Phase 3: Social Operating System Features ---

async function loadSocialCredit() {
    const scoreEl = document.getElementById('socialCreditScore');
    const tierEl = document.getElementById('riskTier');
    const limitEl = document.getElementById('lendingLimit');

    if (!scoreEl) return;

    scoreEl.textContent = '...';

    try {
        const response = await fetch(`${API_BASE_URL}/credit/assess`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await response.json();

        if (response.ok) {
            scoreEl.textContent = data.social_credit_score;
            tierEl.textContent = data.risk_tier;
            tierEl.className = `badge ${data.risk_tier === 'PRIME' ? 'badge-success' : 'badge-warning'}`;
            limitEl.textContent = `₹${data.estimated_micro_loan_limit.toLocaleString()}`;
        }
    } catch (e) {
        console.error("Credit Error:", e);
    }
}

let currentAgentId = null;

function syncAgentUI() {
    const statusEl = document.getElementById('agentStatus');
    const joinBtn = document.getElementById('joinAgentBtn');
    const workBtn = document.getElementById('workAgentBtn');
    const leaveBtn = document.getElementById('leaveAgentBtn');

    if (!statusEl || !currentUser) return;

    if (currentUser.agent_id || currentAgentId) {
        const id = currentUser.agent_id || currentAgentId;
        statusEl.innerHTML = `<span class="badge badge-success">Status: Agent (${id})</span>`;
        if (joinBtn) joinBtn.style.display = 'none';
        if (workBtn) workBtn.style.display = 'block';
        if (leaveBtn) leaveBtn.style.display = 'block';
    } else {
        statusEl.innerHTML = `<span class="badge">Status: Standard User</span>`;
        if (joinBtn) joinBtn.style.display = 'block';
        if (workBtn) workBtn.style.display = 'none';
        if (leaveBtn) leaveBtn.style.display = 'none';
    }
}

async function registerAsAgent() {
    if (!confirm("Are you sure? You will be responsible for assisting citizens in your region.")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/agent/register`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ region: currentUser.state || 'BIHAR' })
        });
        const data = await response.json();

        if (response.ok) {
            currentAgentId = data.agent_id;
            currentUser.agent_id = data.agent_id; // Sync local state
            localStorage.setItem('paraditi_user', JSON.stringify(currentUser));

            alert(`Registration Successful! Your Agent ID is ${data.agent_id}.`);
            syncAgentUI();
        }
    } catch (e) {
        console.error("Agent Error:", e);
    }
}

async function leaveAgentProgram() {
    if (!confirm("Are you sure you want to resign from the Agent Network?")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/agent/resign`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ agent_id: currentAgentId || currentUser.agent_id })
        });
        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            currentAgentId = null;
            delete currentUser.agent_id;
            localStorage.setItem('paraditi_user', JSON.stringify(currentUser));
            syncAgentUI();
        }
    } catch (e) {
        console.error("Resignation Error:", e);
    }
}

async function scheduleArbitrage(appId) {
    // This would be triggered by 'Apply' button if servers are busy
    try {
        const response = await fetch(`${API_BASE_URL}/arbitrage/schedule/${appId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ portal_id: 'api_setu' })
        });
        const data = await response.json();

        if (data.action === "QUEUE_FOR_ARBITRAGE") {
            alert(`Claim Q Active: Government Servers are busy. Submission scheduled for window: ${data.scheduled_window}`);
        }
    } catch (e) {
        console.error(e);
    }
}

// Global Exports
window.startVoiceDiscovery = startVoiceDiscovery;
window.loadMobilityRoadmap = loadMobilityRoadmap;
window.renderLifeJourney = renderLifeJourney;
window.loadSocialCredit = loadSocialCredit;
window.registerAsAgent = registerAsAgent;
window.leaveAgentProgram = leaveAgentProgram;
window.loadDocumentLibrary = loadDocumentLibrary;
window.filterDocs = filterDocs;
window.searchDocs = searchDocs;
window.showUploadModal = showUploadModal;
window.closeUploadModal = closeUploadModal;
window.updateDocTypes = updateDocTypes;
window.handleUploadSubmit = handleUploadSubmit;
window.deleteDocument = deleteDocument;
window.viewDocument = viewDocument;
window.showProfileModal = showProfileModal;
window.closeProfileModal = closeProfileModal;
window.loadRecommendedSchemes = loadRecommendedSchemes;
window.loadAllSchemes = loadAllSchemes;
window.syncFromApiSetu = syncFromApiSetu;
window.uploadDocument = uploadDocument;
window.enableReupload = enableReupload;
window.applyExtractedData = applyExtractedData;
window.showSchemeDetails = showSchemeDetails;
window.withdrawApplication = withdrawApplication;
window.openApplyModal = openApplyModal;
window.closeApplyModal = closeApplyModal;
window.submitApplication = submitApplication;
window.toggleChat = toggleChat;
window.handleChatKey = handleChatKey;
window.sendChatMessage = sendChatMessage;
window.toggleAditi = toggleAditi;
window.minimizeAditi = minimizeAditi;
window.handleAditiKey = handleAditiKey;
window.sendAditiMessage = sendAditiMessage;
