"use client";

import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Pagination,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
} from "@mui/material";
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Search as SearchIcon,
  ShoppingCart as OrderIcon,
  LocalShipping as ShippingIcon,
  Payment as PaymentIcon,
} from "@mui/icons-material";
import { useState } from "react";
import { motion } from "framer-motion";
import {
  useAllOrders,
  useOrder,
  useUpdateOrder,
} from "../../../hooks/useOrdersQuery";
import { useAuth } from "../../../providers/AuthProvider";
import { useWebSocket } from "../../../hooks/useWebSocket";
import { OrderUpdate } from "../../../services/ordersApi";

const ORDER_STATUSES = [
  "pending",
  "confirmed",
  "processing",
  "shipped",
  "delivered",
  "cancelled",
  "refunded",
];

const PAYMENT_STATUSES = [
  "pending",
  "paid",
  "partially_paid",
  "failed",
  "refunded",
  "partially_refunded",
];

export default function OrdersPage() {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [searchTerm, setSearchTerm] = useState("");
  const [openDialog, setOpenDialog] = useState(false);
  const [viewingOrder, setViewingOrder] = useState<any>(null);
  const [editingOrder, setEditingOrder] = useState<any>(null);
  const [formData, setFormData] = useState<OrderUpdate>({
    status: "",
    payment_status: "",
    internal_notes: "",
  });

  const { user } = useAuth();
  const isAdmin = user?.roles?.includes("admin");

  // Queries
  const { data: orders = [], isLoading } = useAllOrders(
    (page - 1) * pageSize,
    pageSize
  );
  const { data: orderDetails } = useOrder(viewingOrder?.id, isAdmin);
  const updateOrderMutation = useUpdateOrder(isAdmin);

  // WebSocket for real-time updates
  const { isConnected } = useWebSocket({
    endpoint: "/ws/orders",
    onMessage: (data: any) => {
      console.log("Order update received:", data);
    },
  });

  const handleViewOrder = (order: any) => {
    setViewingOrder(order);
    setOpenDialog(true);
  };

  const handleEditOrder = (order: any) => {
    setEditingOrder(order);
    setFormData({
      status: order.status,
      payment_status: order.payment_status,
      internal_notes: order.internal_notes || "",
    });
  };

  const handleSaveOrder = async () => {
    if (editingOrder) {
      await updateOrderMutation.mutateAsync({
        orderId: editingOrder.id,
        orderData: formData,
      });
      setEditingOrder(null);
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setViewingOrder(null);
    setEditingOrder(null);
  };

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
      case "refunded":
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
      case "partially_paid":
        return "info";
      case "failed":
        return "error";
      case "refunded":
      case "partially_refunded":
        return "secondary";
      default:
        return "default";
    }
  };

  const filteredOrders = orders.filter(
    (order) =>
      order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.status.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.payment_status.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(filteredOrders.length / pageSize);

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Box display="flex" alignItems="center">
          <OrderIcon sx={{ mr: 1, fontSize: 32 }} />
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            Orders Management
          </Typography>
          {isConnected && (
            <Chip label="Live" color="success" size="small" sx={{ ml: 2 }} />
          )}
        </Box>
      </Box>

      <Box mb={3}>
        <TextField
          fullWidth
          placeholder="Search orders..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <SearchIcon sx={{ mr: 1, color: "text.secondary" }} />
            ),
          }}
        />
      </Box>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Order Number</TableCell>
                <TableCell>Customer</TableCell>
                <TableCell>Total</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Payment</TableCell>
                <TableCell>Items</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredOrders.map((order) => (
                <motion.tr
                  key={order.id}
                  component={TableRow}
                  hover
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.2 }}
                >
                  <TableCell>
                    <Typography
                      variant="body2"
                      fontFamily="monospace"
                      fontWeight="medium"
                    >
                      {order.order_number}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {order.user?.first_name || order.user?.last_name
                        ? `${order.user.first_name || ""} ${
                            order.user.last_name || ""
                          }`.trim()
                        : order.user?.email || "Guest"}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      ${order.total_amount.toFixed(2)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={order.status}
                      color={getStatusColor(order.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={order.payment_status}
                      color={getPaymentStatusColor(order.payment_status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {order.order_items?.length || 0} items
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {new Date(order.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleViewOrder(order)}
                    >
                      <ViewIcon />
                    </IconButton>
                    {isAdmin && (
                      <IconButton
                        size="small"
                        onClick={() => handleEditOrder(order)}
                      >
                        <EditIcon />
                      </IconButton>
                    )}
                  </TableCell>
                </motion.tr>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Box display="flex" justifyContent="center" mt={3}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, value) => setPage(value)}
            color="primary"
          />
        </Box>
      </motion.div>

      {/* Order Details Dialog */}
      <Dialog
        open={openDialog && viewingOrder && !editingOrder}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
          >
            <Typography variant="h6">
              Order {orderDetails?.order_number}
            </Typography>
            {isAdmin && (
              <Button
                variant="outlined"
                size="small"
                startIcon={<EditIcon />}
                onClick={() => handleEditOrder(orderDetails)}
              >
                Edit
              </Button>
            )}
          </Box>
        </DialogTitle>
        <DialogContent>
          {orderDetails && (
            <Box>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        <PaymentIcon sx={{ mr: 1, verticalAlign: "middle" }} />
                        Order Summary
                      </Typography>
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography>Subtotal:</Typography>
                        <Typography>
                          ${orderDetails.subtotal.toFixed(2)}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography>Tax:</Typography>
                        <Typography>
                          ${orderDetails.tax_amount.toFixed(2)}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography>Shipping:</Typography>
                        <Typography>
                          ${orderDetails.shipping_amount.toFixed(2)}
                        </Typography>
                      </Box>
                      <Divider sx={{ my: 1 }} />
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="h6">Total:</Typography>
                        <Typography variant="h6">
                          ${orderDetails.total_amount.toFixed(2)}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        <ShippingIcon sx={{ mr: 1, verticalAlign: "middle" }} />
                        Shipping Address
                      </Typography>
                      <Typography variant="body2">
                        {orderDetails.shipping_first_name}{" "}
                        {orderDetails.shipping_last_name}
                      </Typography>
                      {orderDetails.shipping_company && (
                        <Typography variant="body2">
                          {orderDetails.shipping_company}
                        </Typography>
                      )}
                      <Typography variant="body2">
                        {orderDetails.shipping_address_line1}
                      </Typography>
                      {orderDetails.shipping_address_line2 && (
                        <Typography variant="body2">
                          {orderDetails.shipping_address_line2}
                        </Typography>
                      )}
                      <Typography variant="body2">
                        {orderDetails.shipping_city},{" "}
                        {orderDetails.shipping_state}{" "}
                        {orderDetails.shipping_postal_code}
                      </Typography>
                      <Typography variant="body2">
                        {orderDetails.shipping_country}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    Order Items
                  </Typography>
                  <TableContainer component={Paper}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Product</TableCell>
                          <TableCell>SKU</TableCell>
                          <TableCell align="right">Quantity</TableCell>
                          <TableCell align="right">Unit Price</TableCell>
                          <TableCell align="right">Total</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {orderDetails.order_items?.map((item: any) => (
                          <TableRow key={item.id}>
                            <TableCell>{item.product_name}</TableCell>
                            <TableCell>{item.product_sku}</TableCell>
                            <TableCell align="right">{item.quantity}</TableCell>
                            <TableCell align="right">
                              ${item.unit_price.toFixed(2)}
                            </TableCell>
                            <TableCell align="right">
                              ${item.total_price.toFixed(2)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Order Dialog */}
      <Dialog
        open={!!editingOrder}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Order Status</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Order Status</InputLabel>
              <Select
                value={formData.status}
                onChange={(e) =>
                  setFormData({ ...formData, status: e.target.value })
                }
              >
                {ORDER_STATUSES.map((status) => (
                  <MenuItem key={status} value={status}>
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth margin="normal">
              <InputLabel>Payment Status</InputLabel>
              <Select
                value={formData.payment_status}
                onChange={(e) =>
                  setFormData({ ...formData, payment_status: e.target.value })
                }
              >
                {PAYMENT_STATUSES.map((status) => (
                  <MenuItem key={status} value={status}>
                    {status.charAt(0).toUpperCase() +
                      status.slice(1).replace("_", " ")}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              margin="normal"
              label="Internal Notes"
              multiline
              rows={3}
              value={formData.internal_notes}
              onChange={(e) =>
                setFormData({ ...formData, internal_notes: e.target.value })
              }
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSaveOrder}
            variant="contained"
            disabled={updateOrderMutation.isPending}
          >
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
