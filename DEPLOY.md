# Deploy Commands

## Frontend (Vercel)

```bash
cd frontend
npm run build
npx vercel --prod
```

Follow prompts, then add env vars in Vercel dashboard:
- `VITE_API_URL` = your backend URL (e.g., `https://yourdomain.com`)
- `VITE_WS_URL` = your backend URL with wss (e.g., `wss://yourdomain.com`)

---

## Backend (Digital Ocean)

### On your server:

```bash
# Navigate to backend directory
cd /path/to/educational-influencer/backend

# Create .env file (add your OpenAI key)
nano .env

# Install dependencies if needed
pip3 install -r requirements.txt

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
```

### Nginx config:

Add to your nginx config (update `yourdomain.com` and paths):

```nginx
upstream eduvideo_backend {
    server 127.0.0.1:3003;
}

# Add these locations to your existing server block
location /api/ {
    proxy_pass http://eduvideo_backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
    proxy_read_timeout 300s;
}

location /ws/ {
    proxy_pass http://eduvideo_backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 7d;
}

location /output/ {
    alias /full/path/to/backend/output/;
    expires 1h;
}

location /health {
    proxy_pass http://eduvideo_backend;
}
```

Then:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

Done.
