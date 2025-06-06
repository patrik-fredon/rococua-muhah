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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  FormControlLabel,
  Switch,
  Pagination,
} from "@mui/material";
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Person as PersonIcon,
} from "@mui/icons-material";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  useUsers,
  useCreateUser,
  useUpdateUser,
  useUpdateUserStatus,
} from "../../../hooks/useUsersQuery";
import { useRoles } from "../../../hooks/useRolesQuery";
import { useWebSocket } from "../../../hooks/useWebSocket";
import { UserCreate, UserUpdate } from "../../../services/usersApi";

export default function UsersPage() {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [searchTerm, setSearchTerm] = useState("");
  const [openDialog, setOpenDialog] = useState(false);
  const [editingUser, setEditingUser] = useState<any>(null);
  const [formData, setFormData] = useState<UserCreate & { password?: string }>({
    email: "",
    username: "",
    password: "",
    first_name: "",
    last_name: "",
    phone: "",
    address: "",
    is_active: true,
    is_verified: false,
  });

  // Queries
  const {
    data: users = [],
    isLoading,
    error,
  } = useUsers((page - 1) * pageSize, pageSize);
  const { data: roles = [] } = useRoles();
  const createUserMutation = useCreateUser();
  const updateUserMutation = useUpdateUser();
  const updateStatusMutation = useUpdateUserStatus();

  // WebSocket for real-time updates
  const { isConnected } = useWebSocket({
    endpoint: "/ws/users",
    onMessage: (data) => {
      console.log("User update received:", data);
      // Refetch users data when updates are received
    },
  });

  const handleOpenDialog = (user?: any) => {
    if (user) {
      setEditingUser(user);
      setFormData({
        email: user.email,
        username: user.username,
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        phone: user.phone || "",
        address: user.address || "",
        is_active: user.is_active,
        is_verified: user.is_verified,
      });
    } else {
      setEditingUser(null);
      setFormData({
        email: "",
        username: "",
        password: "",
        first_name: "",
        last_name: "",
        phone: "",
        address: "",
        is_active: true,
        is_verified: false,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingUser(null);
  };

  const handleSaveUser = async () => {
    if (editingUser) {
      // Update user
      const { password, ...updateData } = formData;
      await updateUserMutation.mutateAsync({
        userId: editingUser.id,
        userData: updateData as UserUpdate,
      });
    } else {
      // Create new user
      await createUserMutation.mutateAsync(formData as UserCreate);
    }
    handleCloseDialog();
  };

  const handleToggleUserStatus = async (
    userId: string,
    currentStatus: boolean
  ) => {
    await updateStatusMutation.mutateAsync({
      userId,
      statusData: { is_active: !currentStatus },
    });
  };

  const filteredUsers = users.filter(
    (user) =>
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      `${user.first_name || ""} ${user.last_name || ""}`
        .toLowerCase()
        .includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(filteredUsers.length / pageSize);

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
          <PersonIcon sx={{ mr: 1, fontSize: 32 }} />
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            Users Management
          </Typography>
          {isConnected && (
            <Chip label="Live" color="success" size="small" sx={{ ml: 2 }} />
          )}
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add User
        </Button>
      </Box>

      <Box mb={3}>
        <TextField
          fullWidth
          placeholder="Search users..."
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
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Username</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Verified</TableCell>
                <TableCell>Roles</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredUsers.map((user) => (
                <motion.tr
                  key={user.id}
                  component={TableRow}
                  hover
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.2 }}
                >
                  <TableCell>
                    {user.first_name || user.last_name
                      ? `${user.first_name || ""} ${
                          user.last_name || ""
                        }`.trim()
                      : "-"}
                  </TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.username}</TableCell>
                  <TableCell>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={user.is_active}
                          onChange={() =>
                            handleToggleUserStatus(user.id, user.is_active)
                          }
                          size="small"
                        />
                      }
                      label={user.is_active ? "Active" : "Inactive"}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={user.is_verified ? "Verified" : "Pending"}
                      color={user.is_verified ? "success" : "warning"}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {user.roles?.map((role) => (
                      <Chip
                        key={role.id}
                        label={role.display_name}
                        size="small"
                        sx={{ mr: 0.5 }}
                      />
                    ))}
                  </TableCell>
                  <TableCell>
                    {new Date(user.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(user)}
                    >
                      <EditIcon />
                    </IconButton>
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

      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>{editingUser ? "Edit User" : "Add New User"}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              margin="normal"
              label="Email"
              type="email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              required
            />
            <TextField
              fullWidth
              margin="normal"
              label="Username"
              value={formData.username}
              onChange={(e) =>
                setFormData({ ...formData, username: e.target.value })
              }
              required
            />
            {!editingUser && (
              <TextField
                fullWidth
                margin="normal"
                label="Password"
                type="password"
                value={formData.password || ""}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                required
              />
            )}
            <TextField
              fullWidth
              margin="normal"
              label="First Name"
              value={formData.first_name}
              onChange={(e) =>
                setFormData({ ...formData, first_name: e.target.value })
              }
            />
            <TextField
              fullWidth
              margin="normal"
              label="Last Name"
              value={formData.last_name}
              onChange={(e) =>
                setFormData({ ...formData, last_name: e.target.value })
              }
            />
            <TextField
              fullWidth
              margin="normal"
              label="Phone"
              value={formData.phone}
              onChange={(e) =>
                setFormData({ ...formData, phone: e.target.value })
              }
            />
            <TextField
              fullWidth
              margin="normal"
              label="Address"
              multiline
              rows={2}
              value={formData.address}
              onChange={(e) =>
                setFormData({ ...formData, address: e.target.value })
              }
            />
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_active}
                  onChange={(e) =>
                    setFormData({ ...formData, is_active: e.target.checked })
                  }
                />
              }
              label="Active"
              sx={{ mt: 2 }}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_verified}
                  onChange={(e) =>
                    setFormData({ ...formData, is_verified: e.target.checked })
                  }
                />
              }
              label="Verified"
              sx={{ mt: 1 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSaveUser}
            variant="contained"
            disabled={
              createUserMutation.isPending || updateUserMutation.isPending
            }
          >
            {editingUser ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
