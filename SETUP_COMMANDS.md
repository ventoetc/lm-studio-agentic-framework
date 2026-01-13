# GitHub Repository Setup Commands

## Step 1: Install Git (if not installed)
# Download and install from: https://git-scm.com/download/win

## Step 2: Configure Git (run these commands)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

## Step 3: Initialize Repository
cd "C:\Users\charl\OneDrive\Documents\development\llm chat"
git init

## Step 4: Create .gitignore
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Streamlit
.streamlit/

# Chat history (optional - exclude if sensitive)
# chats/

# OS
.DS_Store
Thumbs.db
EOF

## Step 5: Add all files (baseline)
git add .
git commit -m "Baseline: working LM Studio Streamlit chat app"

## Step 6: Create GitHub repository
# Go to: https://github.com/new
# Name: lm-studio-agentic-framework
# Description: Local agentic execution framework for LM Studio
# Public: Yes
# Initialize: No (we have existing code)

## Step 7: Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/lm-studio-agentic-framework.git
git branch -M main
git push -u origin main

## Step 8: Verify setup
git status
git log --oneline