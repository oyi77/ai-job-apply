/**
 * Global teardown for E2E tests
 * Runs once after all tests
 */

async function globalTeardown() {
  console.log('🧹 Cleaning up E2E test environment...');
  // Add any cleanup logic here if needed
  console.log('✅ E2E test environment cleaned up');
}

export default globalTeardown;
