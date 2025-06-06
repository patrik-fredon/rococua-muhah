# Dashboard CRUD Implementation

This dashboard provides complete CRUD (Create, Read, Update, Delete) functionality for managing users, roles, products, and orders in the e-commerce system.

## Features

### 🔐 Authentication & Authorization

- JWT-based authentication
- Role-based access control (RBAC)
- Admin-only features for user and role management
- Secure API communication with automatic token refresh

### 👥 User Management

- View all users with pagination and search
- Create new users with email verification
- Update user profiles and status
- Toggle user active/inactive status
- Real-time user status updates via WebSocket

### 🛡️ Role Management (Admin Only)

- Create custom roles with permissions
- Update role information and status
- Delete non-system roles (admin/user roles protected)
- Role assignment to users

### 📦 Product Management

- Complete product catalog management
- Inventory tracking and stock status
- Product pricing and cost management
- Category and brand organization
- Featured product management
- SEO metadata support

### 🛒 Order Management

- View all orders with detailed information
- Order status tracking (pending → confirmed → processing → shipped → delivered)
- Payment status management
- Customer and shipping information
- Order item details with product information
- Admin order editing capabilities

## Technology Stack

### Frontend

- **Next.js 14** - React framework with App Router
- **Material-UI (MUI)** - Component library for consistent design
- **React Query (TanStack Query)** - Data fetching and caching
- **TypeScript** - Type safety
- **Framer Motion** - Smooth animations
- **React Hot Toast** - Toast notifications

### Backend Integration

- **FastAPI** - Python backend API
- **WebSocket** - Real-time updates
- **JWT Authentication** - Secure token-based auth
- **PostgreSQL** - Database via SQLAlchemy

## Project Structure

```
dashboard/
├── app/
│   ├── dashboard/
│   │   ├── layout.tsx          # Dashboard layout with navigation
│   │   ├── page.tsx            # Dashboard home page
│   │   ├── users/page.tsx      # User management
│   │   ├── roles/page.tsx      # Role management
│   │   ├── products/page.tsx   # Product management
│   │   └── orders/page.tsx     # Order management
│   ├── login/page.tsx          # Login page
│   └── layout.tsx              # Root layout
├── components/
│   └── RealTimeOrderStatus.tsx # Real-time order updates
├── hooks/
│   ├── useUsersQuery.ts        # User data hooks
│   ├── useRolesQuery.ts        # Role data hooks
│   ├── useProductsQuery.ts     # Product data hooks
│   ├── useOrdersQuery.ts       # Order data hooks
│   └── useWebSocket.ts         # WebSocket connection
├── providers/
│   ├── AppProviders.tsx        # Global providers setup
│   └── AuthProvider.tsx        # Authentication context
└── services/
    ├── authApi.ts              # Authentication API
    ├── usersApi.ts             # User API calls
    ├── rolesApi.ts             # Role API calls
    ├── productsApi.ts          # Product API calls
    └── ordersApi.ts            # Order API calls
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd dashboard
npm install
```

### Required packages:

```json
{
  "@mui/material": "^5.14.0",
  "@mui/icons-material": "^5.14.0",
  "@emotion/react": "^11.11.0",
  "@emotion/styled": "^11.11.0",
  "@tanstack/react-query": "^5.0.0",
  "@tanstack/react-query-devtools": "^5.0.0",
  "react-hot-toast": "^2.4.0",
  "framer-motion": "^10.16.0",
  "axios": "^1.5.0",
  "js-cookie": "^3.0.5",
  "@types/js-cookie": "^3.0.0"
}
```

### 2. Environment Configuration

Create `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 3. Backend Setup

Ensure your FastAPI backend is running with:

- User management endpoints (`/api/v1/users/*`)
- Role management endpoints (`/api/v1/roles/*`)
- Product management endpoints (`/api/v1/products/*`)
- Order management endpoints (`/api/v1/orders/*`)
- WebSocket endpoints (`/ws/*`)

### 4. Run Development Server

```bash
npm run dev
```

Visit `http://localhost:3000` to access the dashboard.

## API Integration

### Authentication

All API calls automatically include JWT tokens from cookies. The `apiClient` handles:

- Token attachment to requests
- Automatic logout on 401 responses
- Error handling and user feedback

### Data Fetching Strategy

- **React Query** for caching and synchronization
- **Optimistic updates** for better UX
- **Background refetching** to keep data fresh
- **Error boundaries** for graceful error handling

### Real-time Updates

WebSocket connections provide live updates for:

- User status changes
- Order status updates
- Product inventory changes
- New order notifications

## Usage Guide

### User Management

1. Navigate to "Users" in the sidebar
2. View user list with search and pagination
3. Click "Add User" to create new users
4. Click edit icon to modify user details
5. Toggle switches to activate/deactivate users

### Role Management (Admin Only)

1. Navigate to "Roles" in the sidebar
2. View existing roles and their permissions
3. Click "Add Role" to create custom roles
4. Edit role names, descriptions, and status
5. Delete custom roles (system roles protected)

### Product Management

1. Navigate to "Products" in the sidebar
2. View product catalog with inventory status
3. Click "Add Product" for new products
4. Edit product details, pricing, and inventory
5. Manage product categories and features

### Order Management

1. Navigate to "Orders" in the sidebar
2. View all orders with status and payment info
3. Click view icon to see order details
4. Click edit icon to update order status
5. Track order progression through fulfillment

## Key Features

### 🔄 Real-time Updates

- Live connection status indicator
- Automatic data refresh on changes
- WebSocket-based notifications

### 📱 Responsive Design

- Mobile-friendly interface
- Adaptive navigation
- Touch-friendly controls

### 🎨 Modern UI/UX

- Material Design components
- Smooth animations
- Intuitive workflows
- Consistent styling

### 🛡️ Security

- Role-based access control
- JWT token management
- Protected admin features
- Secure API communication

### ⚡ Performance

- Efficient data caching
- Optimistic updates
- Lazy loading
- Minimal re-renders

## Development Tips

### Adding New Features

1. Create API service in `services/`
2. Add React Query hooks in `hooks/`
3. Build UI components with MUI
4. Integrate real-time updates if needed

### Customizing Themes

Modify `providers/AppProviders.tsx` to customize:

- Color schemes
- Typography
- Component styles
- Breakpoints

### Error Handling

The system includes comprehensive error handling:

- API error responses
- Network failures
- Validation errors
- User-friendly messages

### Testing

- Mock API responses for development
- Use React Query DevTools for debugging
- Test WebSocket connections
- Verify role-based access

This implementation provides a solid foundation for managing an e-commerce platform with modern web technologies and best practices.
