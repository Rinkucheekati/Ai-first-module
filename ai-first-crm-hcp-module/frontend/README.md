# AI First CRM HCP Module - Frontend

A modern React-based frontend for an AI-first CRM system focused on Healthcare Professional (HCP) management.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Redux Toolkit** - State management
- **React Router** - Client-side routing
- **Material UI (MUI)** - Component library
- **Google Inter Font** - Typography

## Features

### Pages

1. **Login Page** - Secure authentication with gradient design
2. **Dashboard** - Overview with statistics cards and recent activity
3. **HCP List** - Searchable table of Healthcare Professionals with filtering
4. **Log Interaction** - Two-tab interface:
   - **Tab 1: Structured Form** - Traditional form-based interaction logging
   - **Tab 2: Conversational AI Chat** - AI-powered chat interface for natural interaction logging
5. **Interaction History** - Comprehensive history with AI summaries and insights

### Components

- **Navigation Sidebar** - Responsive sidebar with navigation menu
- **Top Navbar** - Header with user menu and logout functionality

### State Management

- **Auth Slice** - Authentication state (user, token, login/logout)
- **HCP Slice** - HCP data management
- **Interaction Slice** - Interaction data management

## Installation

1. Navigate to the frontend directory:
```bash
cd ai-first-crm-hcp-module/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will open at [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML template with Google Fonts
├── src/
│   ├── components/
│   │   ├── common/         # Shared components
│   │   └── layout/         # Layout components (Sidebar, Navbar)
│   ├── pages/              # Page components
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── HCPList.tsx
│   │   ├── LogInteraction.tsx
│   │   └── InteractionHistory.tsx
│   ├── store/
│   │   ├── store.ts        # Redux store configuration
│   │   └── slices/         # Redux slices
│   │       ├── authSlice.ts
│   │       ├── hcpSlice.ts
│   │       └── interactionSlice.ts
│   ├── utils/
│   │   └── theme.ts        # Material UI theme
│   ├── App.tsx             # Main app component with routing
│   └── index.tsx           # Entry point
├── package.json
├── tsconfig.json
└── .gitignore
```

## Usage

### Login

- Enter any email and password to login (demo mode)
- After login, you'll be redirected to the Dashboard

### Navigation

- Use the sidebar to navigate between pages
- On mobile devices, use the hamburger menu in the navbar

### HCP List

- Search HCPs by name, specialty, organization, or city
- View HCP details by clicking the eye icon
- Add new HCPs using the "Add HCP" button

### Log Interaction

**Structured Form Tab:**
- Select HCP from dropdown
- Choose interaction type (call, email, meeting, visit)
- Enter date, duration, notes, and outcome
- Set follow-up requirements if needed

**Conversational AI Chat Tab:**
- Chat naturally with AI to log interactions
- AI guides you through the process
- Use quick tags for common information

### Interaction History

- View all logged interactions
- Filter by search terms
- View detailed interaction information including AI summaries and insights
- AI provides automated summaries and actionable insights for each interaction

## Responsive Design

The application is fully responsive and works on:
- Desktop (sidebar always visible)
- Tablet (sidebar collapsible)
- Mobile (hamburger menu for navigation)

## Theme

The application uses:
- **Inter Font** - Google Font for modern typography
- **Material UI Theme** - Custom theme with consistent colors and styling
- **Primary Color**: Blue (#1976d2)
- **Secondary Color**: Purple (#9c27b0)

## Notes

- TypeScript errors will appear until dependencies are installed
- Run `npm install` to resolve all import errors
- The application uses mock data for demonstration purposes
- Backend integration will require API service implementation
