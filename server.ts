/**
 * Production Web & API Gateway Server
 * Serves React SPA & Proxies /api requests to Flask Python Backend
 */
import express from 'express';
import path from 'path';
import http from 'http';
import { spawn, ChildProcess } from 'child_process';
import { createServer as createViteServer } from 'vite';

const PORT = 3000;
const FLASK_PORT = 5000;
let flaskProcess: ChildProcess | null = null;

function startFlaskBackend(): void {
  const pythonPath = 'python3';
  const backendScript = path.join(process.cwd(), 'backend', 'run.py');

  console.log(`[Flask Backend] Spawning Python server on port ${FLASK_PORT}...`);
  flaskProcess = spawn(pythonPath, [backendScript], {
    env: {
      ...process.env,
      BACKEND_PORT: String(FLASK_PORT),
      PYTHONUNBUFFERED: '1',
    },
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  flaskProcess.stdout?.on('data', (data) => {
    console.log(`[Flask stdout] ${data.toString().trim()}`);
  });

  flaskProcess.stderr?.on('data', (data) => {
    console.error(`[Flask stderr] ${data.toString().trim()}`);
  });

  flaskProcess.on('exit', (code, signal) => {
    console.warn(`[Flask Backend] Process exited with code ${code}, signal ${signal}`);
  });
}

async function startServer() {
  // Start Python Flask Auth backend
  startFlaskBackend();

  const app = express();

  // Proxy /api/* requests directly to Flask
  app.use('/api', (req, res) => {
    const targetPath = `/api${req.url.startsWith('/') ? req.url : `/${req.url}`}`;
    
    const options: http.RequestOptions = {
      hostname: '127.0.0.1',
      port: FLASK_PORT,
      path: targetPath,
      method: req.method,
      headers: {
        ...req.headers,
        host: `127.0.0.1:${FLASK_PORT}`,
      },
    };

    const proxyReq = http.request(options, (proxyRes) => {
      res.writeHead(proxyRes.statusCode || 500, proxyRes.headers);
      proxyRes.pipe(res, { end: true });
    });

    proxyReq.on('error', (err) => {
      console.error('[Proxy Error]', err.message);
      if (!res.headersSent) {
        res.status(502).json({
          success: false,
          error: {
            code: 'BACKEND_UNAVAILABLE',
            message: 'Unable to connect to Shamba. Please try again.',
          },
        });
      }
    });

    req.pipe(proxyReq, { end: true });
  });

  // Vite development middleware vs Static Production bundle
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  const server = app.listen(PORT, '0.0.0.0', () => {
    console.log(`[Shamba Web Server] Running on http://0.0.0.0:${PORT}`);
  });

  // Graceful cleanup
  const cleanup = () => {
    if (flaskProcess) {
      console.log('[Flask Backend] Terminating background process...');
      flaskProcess.kill('SIGTERM');
    }
    server.close(() => {
      process.exit(0);
    });
  };

  process.on('SIGINT', cleanup);
  process.on('SIGTERM', cleanup);
}

startServer().catch((err) => {
  console.error('Failed to start Shamba server:', err);
  process.exit(1);
});
