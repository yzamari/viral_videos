# Viral AI Video Generator - Frontend

A modern React TypeScript application for creating viral videos with AI agents. This frontend provides a comprehensive interface for video generation with real-time monitoring, script editing, overlay management, and subtitle editing.

## Features

- **🎬 Video Configuration**: Complete form with all CLI flags from main.py
- **📊 Real-time Progress**: Live monitoring of AI agent activities and generation progress
- **💬 AI Discussions**: Real-time display of AI agent conversations and strategies
- **🎥 Video Clips**: Display and playback of generated video clips with user selection
- **🎵 Audio Management**: Audio segments display with playback controls
- **📝 Script Editor**: Interactive script editing with segment management
- **🎨 Overlay Editor**: Visual overlay text editing with drag-and-drop positioning
- **📖 Subtitle Editor**: Comprehensive subtitle editing with SRT import/export
- **🎬 Final Video**: Video player with download functionality

## Tech Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** for UI components
- **Tailwind CSS** for styling
- **Socket.IO** for real-time WebSocket communication
- **Axios** for HTTP API requests
- **Vite** for build tooling

## Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Build for production**:
   ```bash
   npm run build
   ```

## Configuration

The frontend expects the Python backend to be running on `http://localhost:8000`. You can modify the API base URL in `src/services/api.ts`.

## License

This project is part of the Viral AI Video Generator system.