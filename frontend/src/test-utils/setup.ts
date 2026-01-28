import { vi } from 'vitest';

export type SetupTestEnvironmentOptions = {
  matchMediaMatches?: boolean;
};

export function createStorageMock(): Storage {
  const store: Record<string, string> = {};
  
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      Object.keys(store).forEach(key => delete store[key]);
    }),
    key: vi.fn((index: number) => Object.keys(store)[index] || null),
    get length() {
      return Object.keys(store).length;
    }
  };
}

// Constructible IntersectionObserver mock for Headless UI and RTL compatibility
class MockIntersectionObserver implements IntersectionObserver {
  readonly root: Element | Document | null = null;
  readonly rootMargin: string = '';
  readonly thresholds: ReadonlyArray<number> = [];
  
  constructor(_callback: IntersectionObserverCallback, _options?: IntersectionObserverInit) {
    // Constructor accepts callback and options as per spec
  }
  
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
  takeRecords = vi.fn((): IntersectionObserverEntry[] => []);
}

// Constructible ResizeObserver mock
class MockResizeObserver implements ResizeObserver {
  constructor(_callback: ResizeObserverCallback) {
    // Constructor accepts callback as per spec
  }
  
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}

export function setupTestEnvironment(options: SetupTestEnvironmentOptions = {}): void {
  const { matchMediaMatches = false } = options;

  // Use globalThis for cross-environment compatibility (not Node-specific 'global')
  globalThis.IntersectionObserver = MockIntersectionObserver as unknown as typeof IntersectionObserver;
  globalThis.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;

  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: matchMediaMatches,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn()
    }))
  });

  Object.defineProperty(globalThis, 'localStorage', {
    value: createStorageMock(),
    writable: true
  });

  Object.defineProperty(globalThis, 'sessionStorage', {
    value: createStorageMock(),
    writable: true
  });
}

setupTestEnvironment();
