# Frontend Components: Component Catalog

> **Complete catalog of React components with usage examples**

## Component Organization

```
components/
├── ui/           # Base UI components (25 components)
├── layout/       # Layout components (3 components)
├── forms/        # Form components (3 components)
├── auth/         # Auth components (2 components)
└── analytics/    # Analytics components (1 component)
```

## Base UI Components (`components/ui/`)

### Button

**File**: `src/components/ui/Button.tsx`

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

// Usage
<Button variant="primary" size="md" onClick={handleClick}>
  Submit
</Button>
```

### Input

```typescript
interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number';
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
}

// Usage
<Input
  type="email"
  placeholder="Enter email"
  value={email}
  onChange={setEmail}
  error={errors.email}
/>
```

### Modal

```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

// Usage
<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Confirm Action"
  size="md"
>
  <p>Are you sure?</p>
  <Button onClick={handleConfirm}>Confirm</Button>
</Modal>
```

---

## Layout Components (`components/layout/`)

### Header

**File**: `src/components/layout/Header.tsx`

```typescript
export const Header: React.FC = () => {
  const { user, logout } = useAppStore();
  
  return (
    <header className="bg-white shadow">
      <nav className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Logo />
          <Navigation />
          <UserMenu user={user} onLogout={logout} />
        </div>
      </nav>
    </header>
  );
};
```

### Sidebar

```typescript
export const Sidebar: React.FC = () => {
  const location = useLocation();
  
  const menuItems = [
    { path: '/', label: 'Dashboard', icon: HomeIcon },
    { path: '/applications', label: 'Applications', icon: BriefcaseIcon },
    { path: '/resumes', label: 'Resumes', icon: DocumentIcon },
  ];
  
  return (
    <aside className="w-64 bg-gray-100 min-h-screen">
      {menuItems.map(item => (
        <NavLink
          key={item.path}
          to={item.path}
          className={location.pathname === item.path ? 'active' : ''}
        >
          <item.icon />
          {item.label}
        </NavLink>
      ))}
    </aside>
  );
};
```

---

## Form Components (`components/forms/`)

### ApplicationForm

**File**: `src/components/forms/ApplicationForm.tsx`

```typescript
interface ApplicationFormProps {
  initialData?: Application;
  onSubmit: (data: ApplicationCreate) => Promise<void>;
  onCancel: () => void;
}

export const ApplicationForm: React.FC<ApplicationFormProps> = ({
  initialData,
  onSubmit,
  onCancel
}) => {
  const { register, handleSubmit, formState: { errors } } = useForm<ApplicationCreate>({
    defaultValues: initialData
  });
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input
        {...register('company_name', { required: 'Company name is required' })}
        placeholder="Company Name"
        error={errors.company_name?.message}
      />
      
      <Input
        {...register('position_title', { required: 'Position is required' })}
        placeholder="Position Title"
        error={errors.position_title?.message}
      />
      
      <Select
        {...register('status')}
        options={[
          { value: 'draft', label: 'Draft' },
          { value: 'submitted', label: 'Submitted' }
        ]}
      />
      
      <div className="flex gap-2">
        <Button type="submit" variant="primary">Save</Button>
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
};
```

---

## State Management Patterns

### Using Zustand Store

```typescript
import { useAppStore } from '@/stores/appStore';

export const UserProfile: React.FC = () => {
  const { user, setUser, logout } = useAppStore();
  
  const handleUpdate = async (data: UserUpdate) => {
    const updated = await api.updateUser(data);
    setUser(updated);
  };
  
  return (
    <div>
      <h1>Welcome, {user?.full_name}</h1>
      <Button onClick={logout}>Logout</Button>
    </div>
  );
};
```

### Using React Query

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const ApplicationsList: React.FC = () => {
  const queryClient = useQueryClient();
  
  // Fetch data
  const { data, isLoading, error } = useQuery({
    queryKey: ['applications'],
    queryFn: () => api.getApplications()
  });
  
  // Mutation
  const createMutation = useMutation({
    mutationFn: (data: ApplicationCreate) => api.createApplication(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    }
  });
  
  if (isLoading) return <Loading />;
  if (error) return <Error message={error.message} />;
  
  return (
    <div>
      {data?.map(app => (
        <ApplicationCard key={app.id} application={app} />
      ))}
    </div>
  );
};
```

---

## Custom Hooks

### useAuth

**File**: `src/hooks/useAuth.ts`

```typescript
export const useAuth = () => {
  const { user, setUser, logout: storeLogout } = useAppStore();
  const navigate = useNavigate();
  
  const login = async (email: string, password: string) => {
    const response = await api.login(email, password);
    localStorage.setItem('token', response.access_token);
    const userData = await api.getCurrentUser();
    setUser(userData);
    navigate('/dashboard');
  };
  
  const logout = () => {
    localStorage.removeItem('token');
    storeLogout();
    navigate('/login');
  };
  
  const isAuthenticated = !!user;
  
  return { user, login, logout, isAuthenticated };
};

// Usage
const { user, login, logout, isAuthenticated } = useAuth();
```

---

## Component Testing

### Testing with Vitest

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click Me</Button>);
    expect(screen.getByText('Click Me')).toBeInTheDocument();
  });
  
  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click</Button>);
    
    fireEvent.click(screen.getByText('Click'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
  
  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click</Button>);
    expect(screen.getByText('Click')).toBeDisabled();
  });
});
```

---

**Last Updated**: 2026-01-20  
**Framework**: React 19 + TypeScript  
**For complete component list, see**: [08-codebase-map.md](./08-codebase-map.md)
