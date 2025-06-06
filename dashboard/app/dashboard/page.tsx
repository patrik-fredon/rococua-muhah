"use client";

import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
} from "@mui/material";
import {
  People as PeopleIcon,
  Inventory as InventoryIcon,
  ShoppingCart as OrdersIcon,
  TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

interface DashboardStats {
  totalUsers: number;
  totalProducts: number;
  totalOrders: number;
  revenue: number;
}

interface RecentActivity {
  id: string;
  type: "user" | "product" | "order";
  description: string;
  timestamp: string;
}

const StatCard = ({
  title,
  value,
  icon: Icon,
  color,
}: {
  title: string;
  value: string | number;
  icon: any;
  color: string;
}) => (
  <motion.div whileHover={{ scale: 1.02 }} transition={{ duration: 0.2 }}>
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="h2" sx={{ fontWeight: 600 }}>
              {value}
            </Typography>
          </Box>
          <Box
            sx={{
              backgroundColor: color,
              borderRadius: "50%",
              p: 2,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Icon sx={{ color: "white", fontSize: 32 }} />
          </Box>
        </Box>
      </CardContent>
    </Card>
  </motion.div>
);

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 0,
    totalProducts: 0,
    totalOrders: 0,
    revenue: 0,
  });
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);

  useEffect(() => {
    // Simulate loading dashboard data
    const loadDashboardData = async () => {
      // In a real app, these would be API calls
      setStats({
        totalUsers: 1234,
        totalProducts: 567,
        totalOrders: 890,
        revenue: 45678.9,
      });

      setRecentActivity([
        {
          id: "1",
          type: "user",
          description: "New user registration: john.doe@example.com",
          timestamp: "2 minutes ago",
        },
        {
          id: "2",
          type: "order",
          description: "Order #12345 completed",
          timestamp: "5 minutes ago",
        },
        {
          id: "3",
          type: "product",
          description: 'Product "Gaming Laptop" updated',
          timestamp: "10 minutes ago",
        },
        {
          id: "4",
          type: "user",
          description: "User profile updated: jane.smith@example.com",
          timestamp: "15 minutes ago",
        },
      ]);
    };

    loadDashboardData();
  }, []);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case "user":
        return <PeopleIcon />;
      case "product":
        return <InventoryIcon />;
      case "order":
        return <OrdersIcon />;
      default:
        return <TrendingUpIcon />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case "user":
        return "primary";
      case "product":
        return "secondary";
      case "order":
        return "success";
      default:
        return "default";
    }
  };

  return (
    <Box>
      <Typography
        variant="h4"
        component="h1"
        gutterBottom
        sx={{ fontWeight: 600 }}
      >
        Dashboard Overview
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Users"
            value={stats.totalUsers.toLocaleString()}
            icon={PeopleIcon}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Products"
            value={stats.totalProducts.toLocaleString()}
            icon={InventoryIcon}
            color="#dc004e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Orders"
            value={stats.totalOrders.toLocaleString()}
            icon={OrdersIcon}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Revenue"
            value={`$${stats.revenue.toLocaleString()}`}
            icon={TrendingUpIcon}
            color="#ed6c02"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Analytics Chart
            </Typography>
            <Box
              display="flex"
              alignItems="center"
              justifyContent="center"
              height="300px"
              sx={{ backgroundColor: "#f5f5f5", borderRadius: 1 }}
            >
              <Typography color="text.secondary">
                Chart placeholder - integrate with your preferred charting
                library
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <List sx={{ maxHeight: 300, overflow: "auto" }}>
              {recentActivity.map((activity) => (
                <ListItem key={activity.id} sx={{ px: 0 }}>
                  <Box sx={{ mr: 2 }}>{getActivityIcon(activity.type)}</Box>
                  <ListItemText
                    primary={activity.description}
                    secondary={activity.timestamp}
                  />
                  <Chip
                    label={activity.type}
                    color={getActivityColor(activity.type) as any}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
