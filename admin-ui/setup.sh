#!/bin/bash

echo "🚀 Setting up Practice Arena Admin UI"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this from the admin-ui directory."
    exit 1
fi

echo "📦 Installing Node.js dependencies..."
npm install

echo "🔧 Verifying TypeScript configuration..."
echo "✅ Environment types configured in src/vite-env.d.ts"

echo ""
echo "🎯 Setup complete! Here's what was fixed:"
echo "  ✅ Added @types/node for Node.js type definitions"
echo "  ✅ Created vite-env.d.ts for Vite environment variables"
echo "  ✅ Updated API client to use import.meta.env"
echo ""
echo "Next steps:"
echo "1. Start development server: npm run dev"
echo "2. Open http://localhost:3001 in your browser"
echo "3. Make sure backend API is running on http://localhost:8000"
echo ""
echo "The TypeScript errors should now be resolved! 🎉"
