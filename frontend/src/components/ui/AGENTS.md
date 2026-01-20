# UI Components Agent Guide (`frontend/src/components/ui/`)

**OVERVIEW**: Reusable, atomic UI component library built with React, TypeScript, and Tailwind CSS.

## STRUCTURE
- **Basic**: `Button`, `Input`, `Badge`, `Spinner`, `Breadcrumb`
- **Feedback**: `Alert`, `Notification`, `Progress`, `Tooltip`
- **Layout**: `Card`, `Modal`, `Pagination`
- **Complex**: `Search`, `Select`, `Chart`, `ThemeToggle`

## WHERE TO LOOK
| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `Button.tsx` | Primary actions | `variant`, `size`, `loading`, `icon` |
| `Card.tsx` | Content grouping | `header`, `footer`, `className` |
| `Notification.tsx` | System alerts | `type`, `message`, `duration` |
| `Modal.tsx` | Overlays | `isOpen`, `onClose`, `title` |
| `Search.tsx` | Data filtering | `onSearch`, `suggestions`, `debounce` |
| `Chart.tsx` | Data visualization | `type`, `data`, `options` |

## CONVENTIONS
- **TypeScript**: Define props using interfaces named `[ComponentName]Props`.
- **Atomic Design**: Keep components pure and presentation-focused; avoid business logic.
- **Styling**: Use standard Tailwind classes. Avoid adding `clsx` or `tailwind-merge`.
- **Performance**: Wrap components in `React.memo` and use `useMemo`/`useCallback` for expensive operations.
- **Accessibility**: Use ARIA attributes and Headless UI for interactive elements (Modal, Select).

## ANTI-PATTERNS
- **Prop Drilling**: Do not pass data through these components; use `children` or specialized props.
- **Inline Styles**: Avoid `style` props unless calculating dynamic values that Tailwind cannot handle.
- **External UI Kits**: Stick to the internal implementation to maintain design consistency.

## NOTES
- **Icons**: Exclusively use `heroicons/24/outline` for consistency.
- **Theme**: Responsive to light/dark modes via `ThemeToggle` and Tailwind `dark:` classes.
- **Testing**: Unit tests are located in the `__tests__` subdirectory.
