# Frontend Deployment Guide

Complete guide for setting up and deploying the Vitalis frontend.

## Overview

The frontend is a React 18 application built with Vite. It communicates with the
FastAPI backend through a REST API and is designed to sit in the `frontend/` folder
alongside the existing `backend/` folder.

## Project Structure

```
frontend/
  index.html              Entry point HTML
  vite.config.js          Vite + dev proxy configuration
  package.json            Dependencies and scripts
  .env.example            Template for environment variables
  src/
    main.jsx              React DOM entry point
    App.jsx               Root component with auth routing
    index.css             Global CSS variables and base styles
    pages/
      LoginPage.jsx       Patient login screen
      ChatPage.jsx        Main chat dashboard
    components/
      Sidebar.jsx         Left navigation panel
      TopBar.jsx          Header bar
      MessageBubble.jsx   Chat message renderer
      ChatInput.jsx       Compose bar with image and voice support
    hooks/
      useAuth.js          Authentication state hook
      useChat.js          Chat message state and API calls
    services/
      api.js              All backend API calls
```

## Prerequisites

- Node.js 18 or higher
- npm 9 or higher
- The backend running at `http://localhost:8000`

Verify Node.js:
```
node --version
npm --version
```

## Installation

Navigate to the `frontend` folder and install dependencies:

```bash
cd frontend
npm install
```

## Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

In development mode you do not need to change anything — Vite proxies all
`/api` requests to `http://localhost:8000/api` automatically.

For a production build, uncomment and set `VITE_API_BASE_URL` in `.env`:

```
VITE_API_BASE_URL=https://your-domain.com/api
```

Then update `src/services/api.js` to use it:

```js
const BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";
```

## Running in Development

Make sure the backend is running first, then:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

Hot Module Replacement is enabled by default, so any saved file change is
reflected immediately in the browser.

## Building for Production

```bash
npm run build
```

This creates an optimised bundle in the `dist/` folder. Serve it with any
static file host (Nginx, Apache, Netlify, Vercel, etc.).

Preview the production build locally:

```bash
npm run preview
```

## Serving with Nginx (Production)

Example minimal Nginx config:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend/dist;
    index index.html;

    # Route all requests to index.html for client-side routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API calls to the FastAPI backend
    location /api/ {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 15M;
    }
}
```

## Login Credentials

The backend accepts Patient IDs in this exact format:

```
FirstName###_LastName###_<uuid>
```

Example from the test suite:

```
Adam631_Cronin387_aff8f143-2375-416f-901d-b0e4c73e3e58
```

## Features

### Login screen
- Enter a Patient ID and click Secure Login.
- The token is stored in `sessionStorage` — it is cleared when the tab is closed.

### Chat dashboard
- Type a message and press Enter or click the send button.
- Attach an image by clicking the photo icon; optionally add a text description.
- Record a voice message with the microphone button (browser microphone permission required).
- Click New Consultation in the sidebar to clear the current chat.
- Click Sign Out to log out.

### Quick prompts
- The welcome screen shows four starter prompts. Click any to send it immediately.

## Browser Support

Any modern browser supporting ES2020+, CSS backdrop-filter, and the MediaRecorder
API is supported: Chrome 88+, Edge 88+, Firefox 87+, Safari 15.4+.

## Troubleshooting

### Login fails with "Invalid patient ID format"
The Patient ID must exactly match the pattern `Name###_Name###_uuid`. Check for
extra spaces or a truncated UUID.

### API requests fail with CORS errors
Verify that `CORS_ORIGINS` in the backend `.env` includes `http://localhost:3000`
and that the backend is actually running.

### Image or audio upload is rejected
Check that the backend `MAX_FILE_SIZE_MB` setting is large enough and that the
file type is in the allowed list (images: jpg, jpeg, png, webp, gif; audio: wav,
mp3, m4a, ogg).

### Voice recording button does nothing
The browser needs microphone permission. Click the lock icon in the address bar
and allow microphone access, then try again.