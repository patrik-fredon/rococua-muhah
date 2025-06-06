# Admin Dashboard

A modular, secure, and animated admin dashboard UI that integrates seamlessly with the FastAPI backend via API endpoints.

## Features

- 🔐 **Secure Authentication**: JWT-based authentication with cookie storage
- 📱 **Responsive Design**: Mobile-first design with Material-UI components
- ⚡ **Real-time Updates**: WebSocket integration for live data updates
- 🎨 **Smooth Animations**: Framer Motion for fluid user interactions
- 🔄 **State Management**: React Query for server state and caching
- 🏗️ **Modular Architecture**: Feature-based organization for scalability
- 🎯 **Type Safety**: Full TypeScript support

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **UI Library**: Material-UI (MUI) v5
- **Animation**: Framer Motion
- **State Management**: React Query (TanStack Query)
- **Authentication**: JWT with httpOnly cookies
- **Real-time**: WebSocket API
- **Styling**: Material-UI theming + CSS-in-JS
- **Type Safety**: TypeScript

## Project Structure

```
dashboard/
├── app/                    # Next.js App Router pages
│   ├── dashboard/          # Protected dashboard routes
│   │   ├── users/         # User management
│   │   ├── products/      # Product management
│   │   └── orders/        # Order management
│   ├── login/             # Authentication
│   └── layout.tsx         # Root layout
├── components/            # Reusable UI components
├── features/              # Feature modules
│   ├── users/            # User-related components and logic
│   ├── products/         # Product-related components and logic
│   └── orders/           # Order-related components and logic
├── hooks/                 # Custom React hooks
│   └── useWebSocket.ts   # WebSocket hook for real-time updates
├── providers/             # Context providers
│   ├── AppProviders.tsx  # Main app providers wrapper
│   └── AuthProvider.tsx  # Authentication context
├── services/              # API clients and external services
│   └── authApi.ts        # Authentication API client
├── store/                 # State management (if using Redux/Zustand)
├── styles/                # Global styles and themes
└── utils/                 # Utility functions
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- FastAPI backend running on `http://localhost:8000`

### Installation

1. **Install dependencies**:

   ```bash
   npm install
   ```

2. **Set up environment variables**:

   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` with your configuration:

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_WS_URL=ws://localhost:8000
   ```

3. **Run the development server**:

   ```bash
   npm run dev
   ```

4. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

### Development Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript type checking
```

## Authentication Flow

1. **Login**: User enters credentials on `/login`
2. **Token Storage**: JWT stored in httpOnly cookie for security
3. **Protected Routes**: Dashboard routes check authentication status
4. **Auto-logout**: Automatic logout on token expiration (401 responses)

## API Integration

### REST API

The dashboard integrates with the FastAPI backend through:

- **Authentication**: `/api/v1/auth/*` endpoints
- **Users**: `/api/v1/users/*` endpoints
- **Products**: `/api/v1/products/*` endpoints
- **Orders**: `/api/v1/orders/*` endpoints
- **Roles**: `/api/v1/roles/*` endpoints

### WebSocket Integration

Real-time updates are handled via WebSocket connections:

- **Products**: `/api/v1/ws/products` - Product and inventory updates
- **Orders**: `/api/v1/ws/orders/{order_id}` - Order status updates

Usage example:

```typescript
import { useWebSocket } from "@/hooks/useWebSocket";

function ProductsPage() {
  const { isConnected, lastMessage } = useWebSocket("/products", {
    onMessage: (data) => {
      console.log("Product update:", data);
      // Update local state or invalidate React Query cache
    },
  });

  // Component implementation...
}
```

## Key Components

### Authentication Provider

```typescript
import { useAuth } from "@/providers/AuthProvider";

function MyComponent() {
  const { user, login, logout, isAuthenticated } = useAuth();
  // Use authentication state...
}
```

### WebSocket Hook

```typescript
import { useWebSocket } from "@/hooks/useWebSocket";

function RealTimeComponent() {
  const { isConnected, sendMessage } = useWebSocket("/products");
  // Handle real-time updates...
}
```

## Customization

### Theming

Customize the Material-UI theme in `providers/AppProviders.tsx`:

```typescript
const theme = createTheme({
  palette: {
    primary: { main: "#1976d2" },
    secondary: { main: "#dc004e" },
  },
  // Add your custom theme configuration
});
```

### Adding New Features

1. Create feature directory in `features/`
2. Add API client in `services/`
3. Create pages in `app/dashboard/`
4. Add navigation item in `app/dashboard/layout.tsx`

## Security Features

- **httpOnly Cookies**: JWT tokens stored securely
- **CSRF Protection**: SameSite cookie configuration
- **Auto-logout**: Automatic token cleanup on expiration
- **Route Protection**: Authentication guards on protected routes

## Performance Optimizations

- **Code Splitting**: Automatic route-based code splitting
- **React Query Caching**: Intelligent server state caching
- **Lazy Loading**: Components loaded on demand
- **Image Optimization**: Next.js automatic image optimization

## Deployment

### Vercel (Recommended)

1. Push code to GitHub repository
2. Import project in Vercel dashboard
3. Set environment variables in Vercel
4. Deploy automatically on push

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables

Required environment variables for production:

```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_WS_URL=wss://your-api-domain.com
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License.
