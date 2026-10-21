import { defineConfig } from '@playwright/test'

const E2E_DB = 'postgresql://erp:erp@localhost:54329/erp_e2e'
const BACKEND = `cd ../backend && DATABASE_URL=${E2E_DB} PYTHONPATH=src`

export default defineConfig({
  testDir: './e2e',
  workers: 1,
  fullyParallel: false,
  timeout: 30_000,
  use: { baseURL: 'http://127.0.0.1:5180', trace: 'retain-on-failure' },
  webServer: [
    {
      command: `${BACKEND} uv run python -m siam_bean_erp.reset_db && ${BACKEND} uv run uvicorn siam_bean_erp.app:create_app --factory --port 8010`,
      url: 'http://127.0.0.1:8010/api/health',
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: 'API_TARGET=http://127.0.0.1:8010 ../node_modules/.bin/vite --host 127.0.0.1 --port 5180 --strictPort',
      url: 'http://127.0.0.1:5180',
      reuseExistingServer: false,
      timeout: 60_000,
    },
  ],
})
