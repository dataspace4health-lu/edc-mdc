Object.defineProperty(window, "location", {
  value: {
    pathname: "/",
    search: "",
    hash: "",
    href: "http://localhost:3000/",
  },
  writable: true,
});

// Mock console methods if needed
global.console = {
  ...console,
  // Suppress console.log in tests
  // log: vi.fn(),
  // warn: vi.fn(),
  // error: vi.fn(),
};
