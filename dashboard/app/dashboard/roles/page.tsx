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
  FormControlLabel,
  Switch,
  Pagination,
} from "@mui/material";
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Security as SecurityIcon,
} from "@mui/icons-material";
import { useState } from "react";
import { motion } from "framer-motion";
import {
  useRoles,
  useCreateRole,
  useUpdateRole,
  useDeleteRole,
} from "../../../hooks/useRolesQuery";
import { useWebSocket } from "../../../hooks/useWebSocket";
import { RoleCreate, RoleUpdate } from "../../../services/rolesApi";

export default function RolesPage() {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [searchTerm, setSearchTerm] = useState("");
  const [openDialog, setOpenDialog] = useState(false);
  const [editingRole, setEditingRole] = useState<any>(null);
  const [formData, setFormData] = useState<RoleCreate>({
    name: "",
    display_name: "",
    description: "",
    is_active: true,
  });

  // Queries
  const { data: roles = [], isLoading } = useRoles(
    (page - 1) * pageSize,
    pageSize
  );
  const createRoleMutation = useCreateRole();
  const updateRoleMutation = useUpdateRole();
  const deleteRoleMutation = useDeleteRole();

  // WebSocket for real-time updates
  const { isConnected } = useWebSocket({
    endpoint: "/ws/roles",
    onMessage: (data: any) => {
      console.log("Role update received:", data);
    },
  });

  const handleOpenDialog = (role?: any) => {
    if (role) {
      setEditingRole(role);
      setFormData({
        name: role.name,
        display_name: role.display_name,
        description: role.description || "",
        is_active: role.is_active,
      });
    } else {
      setEditingRole(null);
      setFormData({
        name: "",
        display_name: "",
        description: "",
        is_active: true,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingRole(null);
  };

  const handleSaveRole = async () => {
    if (editingRole) {
      await updateRoleMutation.mutateAsync({
        roleId: editingRole.id,
        roleData: formData as RoleUpdate,
      });
    } else {
      await createRoleMutation.mutateAsync(formData);
    }
    handleCloseDialog();
  };

  const handleDeleteRole = async (roleId: string) => {
    if (window.confirm("Are you sure you want to delete this role?")) {
      await deleteRoleMutation.mutateAsync(roleId);
    }
  };

  const filteredRoles = roles.filter(
    (role) =>
      role.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      role.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (role.description &&
        role.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const totalPages = Math.ceil(filteredRoles.length / pageSize);

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
          <SecurityIcon sx={{ mr: 1, fontSize: 32 }} />
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            Roles Management
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
          Add Role
        </Button>
      </Box>

      <Box mb={3}>
        <TextField
          fullWidth
          placeholder="Search roles..."
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
                <TableCell>Display Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredRoles.map((role) => (
                <motion.tr
                  key={role.id}
                  component={TableRow}
                  hover
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.2 }}
                >
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace">
                      {role.name}
                    </Typography>
                  </TableCell>
                  <TableCell>{role.display_name}</TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {role.description || "-"}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={role.is_active ? "Active" : "Inactive"}
                      color={role.is_active ? "success" : "error"}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {new Date(role.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(role)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteRole(role.id)}
                      color="error"
                      disabled={role.name === "admin" || role.name === "user"}
                    >
                      <DeleteIcon />
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
        <DialogTitle>{editingRole ? "Edit Role" : "Add New Role"}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              margin="normal"
              label="Role Name"
              placeholder="e.g., moderator"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value.toLowerCase() })
              }
              helperText="Lowercase letters, numbers, hyphens, and underscores only"
              required
            />
            <TextField
              fullWidth
              margin="normal"
              label="Display Name"
              placeholder="e.g., Moderator"
              value={formData.display_name}
              onChange={(e) =>
                setFormData({ ...formData, display_name: e.target.value })
              }
              required
            />
            <TextField
              fullWidth
              margin="normal"
              label="Description"
              placeholder="Role description and purpose"
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
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
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSaveRole}
            variant="contained"
            disabled={
              createRoleMutation.isPending || updateRoleMutation.isPending
            }
          >
            {editingRole ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
