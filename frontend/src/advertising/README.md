# ViralAI Advertising Platform Frontend

A professional, production-ready React TypeScript application for managing viral advertising campaigns with real-time analytics, trending topic detection, and AI-powered content creation.

## Features

### 🎯 Core Features
- **Dashboard**: Real-time metrics overview with interactive charts
- **Campaign Management**: Create, edit, pause, resume, and analyze advertising campaigns
- **Analytics**: Comprehensive performance tracking with customizable timeframes
- **Trending Topics**: AI-powered viral opportunity detection and content suggestions
- **Real-time Updates**: WebSocket integration for live data updates
- **Responsive Design**: Mobile-first design that works on all devices

### 🚀 Technical Features
- **TypeScript**: Full type safety and better developer experience
- **Material-UI**: Modern, accessible UI components
- **Redux Toolkit**: Efficient state management with RTK Query
- **Real-time WebSocket**: Live updates for campaigns and trending topics
- **Chart Visualizations**: Interactive charts using Recharts
- **Form Validation**: Robust form handling with Formik and Yup
- **Authentication**: JWT-based authentication with auto-refresh
- **Error Handling**: Comprehensive error boundaries and user feedback
- **Responsive Layout**: Adaptive design for desktop, tablet, and mobile

## Project Structure

```
src/advertising/
├── components/          # Reusable UI components
│   └── Layout.tsx      # Main application layout
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication context
├── hooks/              # Custom React hooks
│   └── useWebSocket.ts # WebSocket management hook
├── pages/              # Main application pages
│   ├── Dashboard.tsx   # Analytics dashboard
│   ├── Campaigns.tsx   # Campaign list and management
│   ├── CreateCampaign.tsx # Campaign creation wizard
│   ├── Analytics.tsx   # Advanced analytics page
│   └── Trending.tsx    # Trending topics and viral opportunities
├── services/           # API and external services
│   └── api.ts         # API client with all endpoints
├── store/              # Redux store configuration
│   └── store.ts       # Store setup with slices
├── types/              # TypeScript type definitions
│   └── index.ts       # All interface definitions
└── utils/              # Utility functions
    ├── constants.ts    # Application constants
    └── formatters.ts   # Data formatting utilities
```

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Running ViralAI backend at `http://localhost:8000`

### Installation

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Environment Configuration**:
   Create a `.env` file in the frontend directory:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   VITE_WS_URL=ws://localhost:8000
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

4. **Access the application**:
   Open http://localhost:5173 in your browser

## Key Components

### Layout (`components/Layout.tsx`)
- **Navigation**: Sidebar with all main sections
- **Header**: User menu, notifications, theme toggle
- **Real-time Updates**: WebSocket integration for live notifications
- **Responsive**: Collapsible sidebar for mobile devices

### Dashboard (`pages/Dashboard.tsx`)
- **Metrics Cards**: Key performance indicators with trend indicators
- **Interactive Charts**: Performance trends and platform distribution
- **Campaign Overview**: Quick access to active campaigns
- **Recent Activity**: Timeline of recent actions and updates

### Campaign Management (`pages/Campaigns.tsx`)
- **Data Table**: Sortable, filterable campaign list
- **Bulk Actions**: Multi-select operations
- **Status Management**: Play/pause campaigns inline
- **Advanced Filters**: Filter by status, platform, date range, budget

### Campaign Creation (`pages/CreateCampaign.tsx`)
- **Multi-step Wizard**: Guided campaign creation process
- **Form Validation**: Real-time validation with helpful error messages
- **Target Audience**: Advanced demographic and interest targeting
- **Platform Selection**: Multi-platform campaign setup
- **Content Integration**: Video selection and call-to-action setup

### Analytics (`pages/Analytics.tsx`)
- **Customizable Timeframes**: 7d, 30d, 90d, or custom date ranges
- **Multiple Chart Types**: Line, area, bar, pie, and radar charts
- **Campaign Comparison**: Side-by-side performance analysis
- **Demographics**: Age, gender, and location breakdowns
- **Export Functionality**: Download reports in various formats

### Trending Topics (`pages/Trending.tsx`)
- **Viral Opportunities**: AI-detected trending topics with scores
- **Content Suggestions**: AI-generated content ideas
- **Competition Analysis**: Difficulty and opportunity assessment
- **Bookmark System**: Save interesting topics for later
- **Quick Campaign Creation**: One-click campaign creation from trends

## State Management

The application uses Redux Toolkit with the following slices:

- **Auth**: User authentication and profile management
- **Dashboard**: Dashboard metrics and overview data
- **Campaigns**: Campaign list, filters, and CRUD operations
- **Trending**: Trending topics and viral opportunities
- **Videos**: Video library and generation status
- **Notifications**: Real-time notifications and alerts
- **UI**: Theme, sidebar state, and global UI settings

## API Integration

### Endpoints
- **Authentication**: `/auth/*` - Login, register, token refresh
- **Campaigns**: `/campaigns/*` - CRUD operations, analytics
- **Analytics**: `/analytics/*` - Performance data and comparisons
- **Trending**: `/trending/*` - Viral topics and opportunities
- **Videos**: `/videos/*` - Upload, generation, and library management

### Error Handling
- Automatic token refresh on 401 errors
- User-friendly error messages
- Retry logic for failed requests
- Loading states and skeleton screens

## Real-time Features

### WebSocket Integration
- **Campaign Updates**: Live status changes and performance updates
- **Trending Topics**: New viral opportunities as they're detected
- **Notifications**: System alerts and important updates
- **Analytics**: Real-time metric updates

### Event Types
- `campaign_update` - Campaign status or performance changes
- `trending_update` - New trending topics detected
- `metrics_update` - Dashboard metric updates
- `notification` - System notifications and alerts

## Styling and Theming

### Material-UI Integration
- Consistent design system across all components
- Light and dark theme support
- Responsive breakpoints
- Accessibility compliance (WCAG 2.1)

### Custom Styling
- Theme-aware color palette
- Consistent spacing and typography
- Interactive elements with hover states
- Loading and error states

## Performance Optimizations

### Code Splitting
- Lazy-loaded routes and components
- Dynamic imports for large dependencies
- Chunk optimization for better caching

### Data Management
- Efficient state updates with Redux Toolkit
- Memoized selectors to prevent unnecessary re-renders
- Virtualized lists for large datasets
- Debounced search and filtering

### Network Optimization
- Request deduplication
- Intelligent caching strategies
- Compressed API responses
- WebSocket connection management

## Development Workflow

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript checks
```

### Code Quality
- TypeScript strict mode enabled
- ESLint with React and TypeScript rules
- Prettier for consistent formatting
- Pre-commit hooks for code quality

## Testing (Future Enhancement)

### Planned Testing Strategy
- **Unit Tests**: Component testing with React Testing Library
- **Integration Tests**: API integration and user workflows
- **E2E Tests**: Full user journey testing with Playwright
- **Performance Tests**: Bundle size and runtime performance monitoring

## Deployment

### Build Process
```bash
npm run build
```

### Environment Variables
```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com
VITE_ENVIRONMENT=production
```

### Static File Hosting
The built application can be deployed to:
- Vercel
- Netlify  
- AWS S3 + CloudFront
- Any static file hosting service

## Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile**: iOS Safari 14+, Chrome Mobile 90+
- **ES6+ Support**: Required for modern JavaScript features

## Accessibility

- **WCAG 2.1 AA Compliance**: Meets accessibility standards
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: ARIA labels and semantic markup
- **Color Contrast**: Meets minimum contrast ratios
- **Focus Management**: Clear focus indicators

## Security

### Frontend Security Measures
- **XSS Prevention**: Content sanitization and CSP headers
- **CSRF Protection**: Token-based authentication
- **Secure Storage**: JWT tokens in httpOnly cookies (when possible)
- **Input Validation**: Client and server-side validation
- **Dependency Security**: Regular security audits

## Contributing

### Development Guidelines
1. Follow TypeScript strict mode requirements
2. Use Material-UI components when possible
3. Implement proper error boundaries
4. Add loading states for async operations
5. Include proper TypeScript types for all props and functions
6. Follow the established folder structure
7. Add comprehensive error handling

### Code Style
- Use functional components with hooks
- Prefer TypeScript interfaces over types
- Use const assertions for immutable data
- Follow React best practices for performance
- Use meaningful variable and function names

## Troubleshooting

### Common Issues

1. **API Connection Issues**:
   - Verify backend is running on port 8000
   - Check CORS configuration
   - Confirm environment variables

2. **WebSocket Connection Failures**:
   - Check WebSocket URL configuration
   - Verify authentication token
   - Check network/firewall settings

3. **Build Issues**:
   - Clear node_modules and reinstall
   - Check TypeScript errors
   - Verify all imports are correct

4. **Performance Issues**:
   - Check for memory leaks in components
   - Verify proper cleanup of event listeners
   - Monitor bundle size and optimize if needed

## Future Enhancements

### Planned Features
- **A/B Testing**: Campaign variant testing
- **Automated Bidding**: AI-powered bid optimization
- **Advanced Templates**: Pre-built campaign templates
- **Multi-language Support**: Internationalization
- **Advanced Reporting**: Custom report builder
- **Mobile App**: React Native companion app

### Technical Improvements
- **PWA Support**: Service worker and offline capabilities
- **Advanced Caching**: More sophisticated caching strategies
- **Performance Monitoring**: Real user monitoring integration
- **Error Tracking**: Sentry or similar error tracking
- **Analytics**: User behavior tracking and insights

## Support

For technical support or questions about the advertising platform:
1. Check the troubleshooting section above
2. Review the API documentation
3. Check the backend logs for errors
4. Verify your environment configuration

---

**Built with ❤️ using React, TypeScript, and Material-UI**