/**
 * CRUD Generator Utility
 *
 * This utility provides a streamlined way to create new CRUD operations
 * for any entity in the dashboard. It generates the necessary API service,
 * React Query hooks, and provides templates for UI components.
 */

import { createCrudService, CrudApiService } from "../services/baseApi";
import { createCrudHooks } from "../hooks/useGenericQuery";

/**
 * Entity configuration interface
 */
export interface EntityConfig<T, TCreate = Partial<T>, TUpdate = Partial<T>> {
  name: string;
  endpoint: string;
  displayName?: string;
  pluralName?: string;
}

/**
 * Generated CRUD operations result
 */
export interface GeneratedCrud<T, TCreate = Partial<T>, TUpdate = Partial<T>> {
  service: CrudApiService<T, TCreate, TUpdate>;
  hooks: ReturnType<typeof createCrudHooks<T, TCreate, TUpdate>>;
  config: EntityConfig<T, TCreate, TUpdate>;
}

/**
 * Generate complete CRUD operations for an entity
 */
export function generateEntityCrud<
  T,
  TCreate = Partial<T>,
  TUpdate = Partial<T>
>(
  config: EntityConfig<T, TCreate, TUpdate>
): GeneratedCrud<T, TCreate, TUpdate> {
  // Create API service
  const service = createCrudService<T, TCreate, TUpdate>(config.endpoint);

  // Create React Query hooks
  const hooks = createCrudHooks<T, TCreate, TUpdate>(
    config.displayName || config.name,
    service
  );

  return {
    service,
    hooks,
    config: {
      ...config,
      displayName: config.displayName || config.name,
      pluralName: config.pluralName || `${config.name}s`,
    },
  };
}

/**
 * Generate API service file content
 */
export function generateApiServiceCode(
  entityName: string,
  endpoint: string
): string {
  const capitalizedName =
    entityName.charAt(0).toUpperCase() + entityName.slice(1);
  const pluralName = `${entityName}s`;

  return `import { createCrudService } from "./baseApi";

// Define your ${capitalizedName} interfaces here
export interface ${capitalizedName} {
  id: string;
  // Add your entity properties here
  created_at: string;
  updated_at: string;
}

export interface ${capitalizedName}Create {
  // Add your creation properties here
}

export interface ${capitalizedName}Update {
  // Add your update properties here (all optional)
}

// Create ${entityName} CRUD service using the generic base
const ${entityName}Service = createCrudService<${capitalizedName}, ${capitalizedName}Create, ${capitalizedName}Update>("${endpoint}");

export const ${pluralName}Api = {
  // Get all ${pluralName}
  get${capitalizedName}s: async (
    skip: number = 0,
    limit: number = 100
  ): Promise<${capitalizedName}[]> => {
    return ${entityName}Service.getAll({ skip, limit });
  },

  // Get ${entityName} by ID
  get${capitalizedName}: async (${entityName}Id: string): Promise<${capitalizedName}> => {
    return ${entityName}Service.getById(${entityName}Id);
  },

  // Create new ${entityName}
  create${capitalizedName}: async (${entityName}Data: ${capitalizedName}Create): Promise<${capitalizedName}> => {
    return ${entityName}Service.create(${entityName}Data);
  },

  // Update ${entityName}
  update${capitalizedName}: async (
    ${entityName}Id: string,
    ${entityName}Data: ${capitalizedName}Update
  ): Promise<${capitalizedName}> => {
    return ${entityName}Service.update(${entityName}Id, ${entityName}Data);
  },

  // Delete ${entityName}
  delete${capitalizedName}: async (${entityName}Id: string): Promise<void> => {
    return ${entityName}Service.delete(${entityName}Id);
  },

  // Add any entity-specific methods here
  // Example:
  // getActive${capitalizedName}s: async (skip: number = 0, limit: number = 100): Promise<${capitalizedName}[]> => {
  //   return ${entityName}Service.search({ is_active: true }, { skip, limit });
  // },
};

// Export the service for direct access if needed
export { ${entityName}Service };
`;
}

/**
 * Generate React Query hooks file content
 */
export function generateHooksCode(entityName: string): string {
  const capitalizedName =
    entityName.charAt(0).toUpperCase() + entityName.slice(1);
  const pluralName = `${entityName}s`;

  return `import { createCrudHooks } from "./useGenericQuery";
import {
  ${entityName}Service,
  ${capitalizedName},
  ${capitalizedName}Create,
  ${capitalizedName}Update,
} from "../services/${pluralName}Api";

// Create ${entityName} CRUD hooks using the generic factory
const ${entityName}Hooks = createCrudHooks<${capitalizedName}, ${capitalizedName}Create, ${capitalizedName}Update>(
  "${capitalizedName}",
  ${entityName}Service
);

// Export all hooks with ${entityName}-specific names
export const use${capitalizedName}s = ${entityName}Hooks.useGetAll;
export const use${capitalizedName} = ${entityName}Hooks.useGetById;
export const useCreate${capitalizedName} = ${entityName}Hooks.useCreate;
export const useUpdate${capitalizedName} = ${entityName}Hooks.useUpdate;
export const useDelete${capitalizedName} = ${entityName}Hooks.useDelete;

// Export additional hooks
export const use${capitalizedName}Search = ${entityName}Hooks.useSearch;
export const use${capitalizedName}Count = ${entityName}Hooks.useCount;
export const useInvalidate${capitalizedName}s = ${entityName}Hooks.useInvalidateAll;
export const useInvalidate${capitalizedName}Lists = ${entityName}Hooks.useInvalidateLists;
export const usePrefetch${capitalizedName} = ${entityName}Hooks.usePrefetchDetail;

// Export query keys for external use
export const ${entityName}Keys = ${entityName}Hooks.queryKeys;

// Add any entity-specific hooks here
// Example:
// export function useActive${capitalizedName}s(skip: number = 0, limit: number = 100) {
//   return ${entityName}Hooks.useSearch({ is_active: true }, { skip, limit });
// }
`;
}

/**
 * Generate dashboard page component template
 */
export function generatePageComponentCode(entityName: string): string {
  const capitalizedName =
    entityName.charAt(0).toUpperCase() + entityName.slice(1);
  const pluralName = `${entityName}s`;

  return `"use client";

import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Chip,
  Tooltip,
  CircularProgress,
} from "@mui/material";
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import {
  use${capitalizedName}s,
  useCreate${capitalizedName},
  useUpdate${capitalizedName},
  useDelete${capitalizedName},
} from "@/hooks/use${capitalizedName}Query";
import { ${capitalizedName}, ${capitalizedName}Create, ${capitalizedName}Update } from "@/services/${pluralName}Api";

const ${capitalizedName}ManagementPage: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState<${capitalizedName} | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  // Queries and mutations
  const { data: ${pluralName} = [], isLoading, error } = use${capitalizedName}s();
  const createMutation = useCreate${capitalizedName}();
  const updateMutation = useUpdate${capitalizedName}();
  const deleteMutation = useDelete${capitalizedName}();

  const handleCreate = () => {
    setEditingItem(null);
    setOpenDialog(true);
  };

  const handleEdit = (item: ${capitalizedName}) => {
    setEditingItem(item);
    setOpenDialog(true);
  };

  const handleDelete = (id: string) => {
    setDeleteConfirmId(id);
  };

  const confirmDelete = () => {
    if (deleteConfirmId) {
      deleteMutation.mutate(deleteConfirmId);
      setDeleteConfirmId(null);
    }
  };

  const handleSubmit = (data: ${capitalizedName}Create | ${capitalizedName}Update) => {
    if (editingItem) {
      updateMutation.mutate(
        { id: editingItem.id, data: data as ${capitalizedName}Update },
        {
          onSuccess: () => {
            setOpenDialog(false);
            setEditingItem(null);
          },
        }
      );
    } else {
      createMutation.mutate(data as ${capitalizedName}Create, {
        onSuccess: () => {
          setOpenDialog(false);
        },
      });
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Typography color="error">Error loading ${pluralName}: {error.message}</Typography>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            ${capitalizedName} Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
            sx={{ borderRadius: 2 }}
          >
            Add ${capitalizedName}
          </Button>
        </Box>

        <Card>
          <CardContent>
            <TableContainer component={Paper} elevation={0}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    {/* Add your table headers here */}
                    <TableCell>Created At</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {${pluralName}.map((item) => (
                    <TableRow key={item.id} hover>
                      <TableCell>{item.id}</TableCell>
                      {/* Add your table cells here */}
                      <TableCell>
                        {new Date(item.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Tooltip title="View">
                          <IconButton size="small" onClick={() => handleEdit(item)}>
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit">
                          <IconButton size="small" onClick={() => handleEdit(item)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            onClick={() => handleDelete(item.id)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>

        {/* Form Dialog */}
        <${capitalizedName}FormDialog
          open={openDialog}
          onClose={() => setOpenDialog(false)}
          onSubmit={handleSubmit}
          editingItem={editingItem}
          isLoading={createMutation.isPending || updateMutation.isPending}
        />

        {/* Delete Confirmation Dialog */}
        <Dialog open={!!deleteConfirmId} onClose={() => setDeleteConfirmId(null)}>
          <DialogTitle>Confirm Delete</DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to delete this ${entityName}? This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteConfirmId(null)}>Cancel</Button>
            <Button
              onClick={confirmDelete}
              color="error"
              variant="contained"
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? <CircularProgress size={20} /> : "Delete"}
            </Button>
          </DialogActions>
        </Dialog>
      </motion.div>
    </Box>
  );
};

// Form Dialog Component
interface ${capitalizedName}FormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: ${capitalizedName}Create | ${capitalizedName}Update) => void;
  editingItem: ${capitalizedName} | null;
  isLoading: boolean;
}

const ${capitalizedName}FormDialog: React.FC<${capitalizedName}FormDialogProps> = ({
  open,
  onClose,
  onSubmit,
  editingItem,
  isLoading,
}) => {
  const [formData, setFormData] = useState<Partial<${capitalizedName}>>({});

  React.useEffect(() => {
    if (editingItem) {
      setFormData(editingItem);
    } else {
      setFormData({});
    }
  }, [editingItem, open]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          {editingItem ? \`Edit \${editingItem.id}\` : "Create New ${capitalizedName}"}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {/* Add your form fields here */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Example Field"
                value={formData.exampleField || ""}
                onChange={(e) =>
                  setFormData({ ...formData, exampleField: e.target.value })
                }
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={20} /> : (editingItem ? "Update" : "Create")}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default ${capitalizedName}ManagementPage;
`;
}

/**
 * Instructions for adding a new entity
 */
export function getAddEntityInstructions(entityName: string): string {
  const capitalizedName =
    entityName.charAt(0).toUpperCase() + entityName.slice(1);
  const pluralName = `${entityName}s`;

  return `
# Adding ${capitalizedName} Entity to Dashboard

## Backend Setup

1. **Create the model** (\`app/models/${entityName}.py\`):
   - Define SQLAlchemy model with relationships
   - Add to \`app/models/__init__.py\`

2. **Create schemas** (\`app/schemas/${entityName}.py\`):
   - Define Pydantic models for Create, Read, Update
   - Add to \`app/schemas/__init__.py\`

3. **Create service** (\`app/services/${entityName}_service.py\`):
   - Extend CRUDBase class
   - Add entity-specific business logic
   - Add to \`app/services/__init__.py\`

4. **Create API routes** (\`app/api/${entityName}.py\`):
   - Use the service layer
   - Add proper authentication and permissions
   - Add to \`app/api/__init__.py\`

5. **Run database migration**:
   \`\`\`bash
   alembic revision --autogenerate -m "Add ${entityName} model"
   alembic upgrade head
   \`\`\`

## Frontend Setup

1. **Create API service** (\`dashboard/services/${pluralName}Api.ts\`):
   Use the generated code from \`generateApiServiceCode\`

2. **Create React Query hooks** (\`dashboard/hooks/use${capitalizedName}Query.ts\`):
   Use the generated code from \`generateHooksCode\`

3. **Create dashboard page** (\`dashboard/app/dashboard/${pluralName}/page.tsx\`):
   Use the generated code from \`generatePageComponentCode\`

4. **Update navigation** (\`dashboard/app/dashboard/layout.tsx\`):
   Add new menu item for ${pluralName}

5. **Add route to sidebar navigation**

## Example Usage

\`\`\`typescript
// Generate all CRUD operations
const ${entityName}Crud = generateEntityCrud<${capitalizedName}, ${capitalizedName}Create, ${capitalizedName}Update>({
  name: "${entityName}",
  endpoint: "/api/v1/${pluralName}",
  displayName: "${capitalizedName}",
  pluralName: "${capitalizedName}s"
});

// Use the generated hooks
const { data: ${pluralName} } = ${entityName}Crud.hooks.useGetAll();
const createMutation = ${entityName}Crud.hooks.useCreate();
\`\`\`

This pattern ensures consistency, maintainability, and follows DRY principles.
`;
}
