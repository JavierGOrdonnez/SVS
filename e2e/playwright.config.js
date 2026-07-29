import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  timeout: 30000,
  retries: 1,
  use: {
    baseURL: 'http://127.0.0.1:8088',
    headless: true,
    viewport: { width: 1440, height: 900 },
    launchOptions: {
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_PATH || undefined,
    },
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
  webServer: {
    command: 'python3 src/serve.py --port 8088 --no-auth',
    url: 'http://127.0.0.1:8088',
    reuseExistingServer: true,
    cwd: '..',
    timeout: 15000,
  },
});
