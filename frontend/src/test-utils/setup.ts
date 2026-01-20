import { vi } from 'vitest';

export type SetupTestEnvironmentOptions = {
  matchMediaMatches?: boolean;
};

export function createStorageMock(): Storage {
  return {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
    key: vi.fn(),
    length: 0
  };
}

export function setupTestEnvironment(options: SetupTestEnvironmentOptions = {}): void {
  const { matchMediaMatches = false } = options;

  global.IntersectionObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn()
  }));

  global.ResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn()
  }));

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

  Object.defineProperty(global, 'localStorage', {
    value: createStorageMock(),
    writable: true
  });

  Object.defineProperty(global, 'sessionStorage', {
    value: createStorageMock(),
    writable: true
  });
}

setupTestEnvironment();
