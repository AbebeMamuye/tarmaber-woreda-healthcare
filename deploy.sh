#!/bin/bash

# Healthcare Performance Management System Deployment Script

echo "🚀 Starting Deployment Process..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - Healthcare Performance Management System"
    echo "✅ Git repository initialized"
else
    echo "📦 Git repository already exists"
fi

# Check if remote origin exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "🔗 Please add GitHub remote origin:"
    echo "git remote add origin https://github.com/yourusername/healthcare-performance.git"
    echo "Then run: git push -u origin main"
    exit 1
fi

echo "📋 Deployment Options:"
echo "1. Streamlit Cloud (Recommended - Free)"
echo "2. Railway (Free tier available)"
echo "3. Heroku (Free tier available)"
echo "4. VPS/Cloud Server (Paid)"

read -p "Choose deployment option (1-4): " choice

case $choice in
    1)
        echo "🌐 Deploying to Streamlit Cloud..."
        echo "1. Push your code to GitHub:"
        echo "   git push origin main"
        echo "2. Go to https://share.streamlit.io"
        echo "3. Connect your GitHub account"
        echo "4. Select your repository"
        echo "5. Set main file to 'app.py'"
        echo "6. Click 'Deploy'"
        ;;
    2)
        echo "🚂 Deploying to Railway..."
        echo "1. Install Railway CLI: npm install -g @railway/cli"
        echo "2. Login: railway login"
        echo "3. Initialize: railway init"
        echo "4. Deploy: railway up"
        ;;
    3)
        echo "🔥 Deploying to Heroku..."
        echo "1. Install Heroku CLI"
        echo "2. Login: heroku login"
        echo "3. Create app: heroku create your-app-name"
        echo "4. Deploy: git push heroku main"
        ;;
    4)
        echo "🖥️  VPS Deployment Instructions:"
        echo "1. Copy files to server"
        echo "2. Install Python and pip"
        echo "3. Run: pip install -r requirements.txt"
        echo "4. Run: streamlit run app.py --server.port 8501"
        echo "5. Configure nginx reverse proxy (optional)"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo "✅ Deployment instructions provided!"
echo "📚 Check README.md for detailed deployment guide"
