# Practice Arena Admin UI

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Setup

1. **Install dependencies**:
```bash
npm install
```

2. **Start development server**:
```bash
npm run dev
```

3. **Open in browser**:
Navigate to `http://localhost:3001`

## 📋 TypeScript Errors Before Installation

**This is normal!** You will see TypeScript errors before running `npm install`:

```
Cannot find module 'react' or its corresponding type declarations.
Cannot find module '@tanstack/react-query' or its corresponding type declarations.
Cannot find type definition file for 'vite/client'.
```

**These errors will resolve automatically** after installing dependencies.

## 🔧 Environment Configuration

The app uses Vite environment variables:

- `import.meta.env.PROD` - Production mode
- `import.meta.env.DEV` - Development mode  
- `import.meta.env.VITE_API_URL` - Custom API URL (optional)

## 📦 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## 🌐 API Configuration

The app automatically connects to:
- Development: `http://localhost:8000/api`
- Production: `/api` (same domain)

Override with `VITE_API_URL` environment variable.

## 🎯 Features

- ✅ Template management (CRUD)
- ✅ Advanced search and filtering
- ✅ Visual template editor with live preview
- ✅ Review and approval workflow
- ✅ Coverage analytics dashboard
- ✅ Responsive design (mobile + desktop)
- ✅ TypeScript support
- ✅ Accessibility features

## 📱 Development

The admin UI runs on port 3001 and proxies API requests to the backend on port 8000.

Make sure the backend API server is running when using the admin UI.

## 🔍 Troubleshooting

### TypeScript errors after npm install
```bash
# Restart TypeScript server in your IDE
# VS Code: Cmd+Shift+P -> "TypeScript: Restart TS Server"
```

### API connection issues
```bash
# Ensure backend is running on port 8000
# Check vite.config.ts proxy configuration
```

### Build issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```
