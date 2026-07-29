import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  timeout: 30000,
  retries: 1,
  use: {
    baseURL: 'http://192.168.1.22:8088',
    headless: true,
    viewport: { width: 1440, height: 900 },
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
  webServer: {
    command: '../.venvlnx/bin/python ../src/serve.py --port 8088 --no-auth',
    url: 'http://192.168.1.22:8088',
    reuseExistingServer: true,
    cwd: '..',
    timeout: 15000,
  },
});
