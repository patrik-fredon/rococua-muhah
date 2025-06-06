"use client";

import {
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  CircularProgress,
  Alert,
} from "@mui/material";
import { motion, AnimatePresence } from "framer-motion";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useState, useEffect } from "react";
import toast from "react-hot-toast";

interface OrderStatus {
  order_id: string;
  status: string;
  payment_status: string;
  last_updated: string;
}

interface RealTimeOrderStatusProps {
  orderId: string;
}

export function RealTimeOrderStatus({ orderId }: RealTimeOrderStatusProps) {
  const [orderStatus, setOrderStatus] = useState<OrderStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const { isConnected, lastMessage } = useWebSocket(`/orders/${orderId}`, {
    onMessage: (data) => {
      console.log("Order update received:", data);

      if (data.type === "connection_established") {
        setOrderStatus({
          order_id: data.data.order_id,
          status: data.data.current_status,
          payment_status: data.data.payment_status,
          last_updated: new Date().toISOString(),
        });
        setIsLoading(false);
      } else if (data.type === "order_status_changed") {
        setOrderStatus((prev) =>
          prev
            ? {
                ...prev,
                status: data.data.new_status,
                last_updated: new Date().toISOString(),
              }
            : null
        );
        toast.success(`Order status updated to: ${data.data.new_status}`);
      } else if (data.type === "payment_status_changed") {
        setOrderStatus((prev) =>
          prev
            ? {
                ...prev,
                payment_status: data.data.new_status,
                last_updated: new Date().toISOString(),
              }
            : null
        );
        toast.success(`Payment status updated to: ${data.data.new_status}`);
      }
    },
    onConnect: () => {
      console.log(`Connected to order ${orderId} updates`);
    },
    onDisconnect: () => {
      console.log(`Disconnected from order ${orderId} updates`);
    },
    onError: (error) => {
      console.error("WebSocket error:", error);
      setIsLoading(false);
    },
  });

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "pending":
        return "warning";
      case "confirmed":
        return "info";
      case "processing":
        return "primary";
      case "shipped":
        return "secondary";
      case "delivered":
        return "success";
      case "cancelled":
        return "error";
      default:
        return "default";
    }
  };

  const getPaymentStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "pending":
        return "warning";
      case "paid":
        return "success";
      case "failed":
        return "error";
      case "refunded":
        return "info";
      default:
        return "default";
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="center" p={2}>
            <CircularProgress size={24} sx={{ mr: 2 }} />
            <Typography>Connecting to real-time updates...</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!isConnected) {
    return (
      <Card>
        <CardContent>
          <Alert severity="warning">
            Unable to connect to real-time updates. Status information may not
            be current.
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!orderStatus) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">
            Unable to load order status information.
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={orderStatus.last_updated}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.3 }}
      >
        <Card>
          <CardContent>
            <Box
              display="flex"
              alignItems="center"
              justifyContent="between"
              mb={2}
            >
              <Typography variant="h6" component="h3">
                Order Status
              </Typography>
              <Box display="flex" alignItems="center">
                <Box
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    backgroundColor: isConnected
                      ? "success.main"
                      : "error.main",
                    mr: 1,
                  }}
                />
                <Typography variant="caption" color="text.secondary">
                  {isConnected ? "Live" : "Disconnected"}
                </Typography>
              </Box>
            </Box>

            <Box display="flex" flexDirection="column" gap={2}>
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Order Status
                </Typography>
                <motion.div layout transition={{ duration: 0.2 }}>
                  <Chip
                    label={orderStatus.status}
                    color={getStatusColor(orderStatus.status) as any}
                    variant="filled"
                  />
                </motion.div>
              </Box>

              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Payment Status
                </Typography>
                <motion.div layout transition={{ duration: 0.2 }}>
                  <Chip
                    label={orderStatus.payment_status}
                    color={
                      getPaymentStatusColor(orderStatus.payment_status) as any
                    }
                    variant="outlined"
                  />
                </motion.div>
              </Box>

              <Box>
                <Typography variant="caption" color="text.secondary">
                  Last updated:{" "}
                  {new Date(orderStatus.last_updated).toLocaleString()}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </motion.div>
    </AnimatePresence>
  );
}
