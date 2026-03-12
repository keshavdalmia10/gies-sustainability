import { createReadStream, existsSync, statSync } from 'node:fs'
import http from 'node:http'
import { extname, join, normalize } from 'node:path'
import { Readable } from 'node:stream'
import { fileURLToPath } from 'node:url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))
const distDir = join(__dirname, 'dist')
const host = '127.0.0.1'
const port = 3000
const apiOrigin = 'http://127.0.0.1:8000'

const contentTypes = {
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.map': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.txt': 'text/plain; charset=utf-8',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
}

function resolveStaticPath(urlPath) {
  const safePath = normalize(urlPath).replace(/^(\.\.[/\\])+/, '')
  const relativePath = safePath === '/' ? '/index.html' : safePath
  const absolutePath = join(distDir, relativePath)
  if (existsSync(absolutePath) && statSync(absolutePath).isFile()) {
    return absolutePath
  }
  return join(distDir, 'index.html')
}

function setCorsHeaders(res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,DELETE,OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')
}

async function proxyApi(req, res) {
  const targetUrl = new URL(req.url, apiOrigin)
  const headers = { ...req.headers, host: targetUrl.host }

  try {
    const upstream = await fetch(targetUrl, {
      method: req.method,
      headers,
      body: req.method === 'GET' || req.method === 'HEAD' ? undefined : Readable.toWeb(req),
      duplex: req.method === 'GET' || req.method === 'HEAD' ? undefined : 'half',
    })

    res.writeHead(upstream.status, Object.fromEntries(upstream.headers.entries()))
    if (!upstream.body || req.method === 'HEAD') {
      res.end()
      return
    }

    Readable.fromWeb(upstream.body).pipe(res)
  } catch (error) {
    res.writeHead(502, { 'Content-Type': 'application/json; charset=utf-8' })
    res.end(JSON.stringify({ error: 'Proxy request failed', detail: String(error) }))
  }
}

async function serveStatic(req, res) {
  const filePath = resolveStaticPath(req.url)
  const extension = extname(filePath)
  const contentType = contentTypes[extension] || 'application/octet-stream'

  res.writeHead(200, { 'Content-Type': contentType })
  if (req.method === 'HEAD') {
    res.end()
    return
  }

  createReadStream(filePath).pipe(res)
}

const server = http.createServer(async (req, res) => {
  if (!req.url || !req.method) {
    res.writeHead(400)
    res.end('Bad Request')
    return
  }

  if (req.method === 'OPTIONS') {
    setCorsHeaders(res)
    res.writeHead(204)
    res.end()
    return
  }

  if (req.url.startsWith('/api/')) {
    setCorsHeaders(res)
    await proxyApi(req, res)
    return
  }

  await serveStatic(req, res)
})

server.listen(port, host, async () => {
  const indexExists = existsSync(join(distDir, 'index.html'))
  if (!indexExists) {
    const message = 'Missing frontend/dist/index.html. Build the frontend before using serve-dist.mjs.'
    console.error(message)
    process.exitCode = 1
    server.close()
    return
  }

  console.log(`Frontend available at http://${host}:${port}`)
})
