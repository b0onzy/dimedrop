"""
Custom theme for DimeDrop Gradio app.
Professional dark theme with orange accents and modern UI patterns.
"""

import gradio as gr

# Custom CSS
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary-color: #F97316;
    --primary-hover: #EA580C;
    --secondary-color: #1E40AF;
    --background-dark: #0F0F0F;
    --background-card: #1A1A1A;
    --background-sidebar: #141414;
    --text-primary: #FFFFFF;
    --text-secondary: #E5E7EB;
    --text-muted: #9CA3AF;
    --border-color: #374151;
    --border-hover: #F97316;
    --success-color: #10B981;
    --warning-color: #F59E0B;
    --error-color: #EF4444;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    --radius-sm: 6px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;
}

* {
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--background-dark);
    color: var(--text-primary);
    line-height: 1.6;
}

.gradio-container {
    background: var(--background-dark) !important;
    font-family: 'Inter', sans-serif;
    max-width: none !important;
    padding: 0 !important;
}

/* Sidebar Styling */
.sidebar {
    background: var(--background-sidebar) !important;
    border-right: 1px solid var(--border-color) !important;
    width: 280px !important;
    min-height: 100vh;
    padding: 24px 20px !important;
    box-shadow: var(--shadow-xl);
    position: fixed;
    left: 0;
    top: 0;
    z-index: 100;
}

.sidebar .brand-section {
    text-align: center;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border-color);
}

.sidebar .brand-logo {
    font-size: 24px;
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: 4px;
    letter-spacing: -0.02em;
}

.sidebar .brand-tagline {
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Navigation Buttons */
.sidebar .nav-button {
    width: 100% !important;
    margin-bottom: 8px !important;
    padding: 12px 16px !important;
    background: transparent !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-secondary) !important;
    text-align: left !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    cursor: pointer !important;
}

.sidebar .nav-button:hover {
    background: rgba(249, 115, 22, 0.1) !important;
    color: var(--primary-color) !important;
    transform: translateX(4px);
}

.sidebar .nav-button.active {
    background: var(--primary-color) !important;
    color: white !important;
    box-shadow: var(--shadow-md);
}

/* User Status Section */
.user-status-card {
    background: var(--background-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-lg) !important;
    padding: 16px !important;
    margin-bottom: 24px !important;
}

.user-status-card .status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--error-color);
}

.status-dot.logged-in {
    background: var(--success-color);
}

.status-text {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Quick Stats */
.quick-stats {
    background: var(--background-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-lg) !important;
    padding: 16px !important;
}

.stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.stat-item:last-child {
    margin-bottom: 0;
}

.stat-label {
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.stat-value {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
}

/* Main Content Area */
.main-content {
    margin-left: 280px !important;
    padding: 32px !important;
    background: var(--background-dark) !important;
    min-height: 100vh;
}

/* Hero Section */
.hero-section {
    background: linear-gradient(135deg, #F97316 0%, #EA580C 50%, #DC2626 100%);
    border-radius: var(--radius-xl);
    padding: 48px 32px;
    margin-bottom: 32px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.hero-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="basketball" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="8" fill="rgba(255,255,255,0.1)"/><circle cx="10" cy="10" r="3" fill="rgba(255,255,255,0.2)"/></pattern></defs><rect width="100" height="100" fill="url(%23basketball)"/></svg>');
    opacity: 0.1;
}

.hero-content {
    position: relative;
    z-index: 1;
}

.hero-title {
    font-size: 48px;
    font-weight: 700;
    color: white;
    margin-bottom: 16px;
    letter-spacing: -0.02em;
    line-height: 1.1;
}

.hero-subtitle {
    font-size: 20px;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 24px;
    font-weight: 400;
}

.hero-stats {
    display: flex;
    justify-content: center;
    gap: 32px;
    margin-top: 32px;
}

.hero-stat {
    text-align: center;
}

.hero-stat-value {
    font-size: 32px;
    font-weight: 700;
    color: white;
    display: block;
}

.hero-stat-label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.8);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 500;
}

/* Feature Cards */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
}

.feature-card {
    background: var(--background-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-lg) !important;
    padding: 24px !important;
    transition: all 0.3s ease !important;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--primary-color);
    transform: scaleX(0);
    transition: transform 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-4px) !important;
    box-shadow: var(--shadow-xl) !important;
    border-color: var(--primary-color) !important;
}

.feature-card:hover::before {
    transform: scaleX(1);
}

.feature-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    font-size: 24px;
    color: white;
}

.feature-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
}

.feature-description {
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.5;
}

/* Component Cards */
.component-card {
    background: var(--background-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-lg) !important;
    padding: 24px !important;
    margin-bottom: 24px !important;
    box-shadow: var(--shadow-md);
}

.component-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
}

.component-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 12px;
}

.component-icon {
    width: 32px;
    height: 32px;
    background: var(--primary-color);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 16px;
}

/* Button Styles */
.btn-primary {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    border-radius: var(--radius-md) !important;
    transition: all 0.2s ease !important;
    box-shadow: var(--shadow-md);
}

.btn-primary:hover {
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-lg) !important;
}

.btn-secondary {
    background: var(--background-card) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
    font-weight: 500 !important;
    padding: 12px 24px !important;
    border-radius: var(--radius-md) !important;
    transition: all 0.2s ease !important;
}

.btn-secondary:hover {
    border-color: var(--primary-color) !important;
    color: var(--primary-color) !important;
}

/* Form Elements */
.gradio-textbox, .gradio-dropdown, .gradio-radio, .gradio-checkbox {
    background: var(--background-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
}

.gradio-textbox:focus, .gradio-dropdown:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1) !important;
}

/* Loading States */
.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 2px solid var(--border-color);
    border-radius: 50%;
    border-top-color: var(--primary-color);
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 1024px) {
    .sidebar {
        width: 240px !important;
    }
    .main-content {
        margin-left: 240px !important;
    }
}

@media (max-width: 768px) {
    .sidebar {
        width: 100% !important;
        position: relative !important;
        border-right: none !important;
        border-bottom: 1px solid var(--border-color) !important;
        padding: 16px !important;
    }

    .main-content {
        margin-left: 0 !important;
        padding: 16px !important;
    }

    .hero-section {
        padding: 32px 16px !important;
    }

    .hero-title {
        font-size: 32px !important;
    }

    .hero-stats {
        flex-direction: column;
        gap: 16px;
    }

    .feature-grid {
        grid-template-columns: 1fr;
        gap: 16px;
    }
}

@media (max-width: 480px) {
    .hero-section {
        padding: 24px 12px !important;
    }

    .hero-title {
        font-size: 28px !important;
    }

    .component-card {
        padding: 16px !important;
    }
}
"""

# Custom theme object
dime_drop_theme = gr.Theme()
