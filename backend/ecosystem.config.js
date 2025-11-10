module.exports = {
  apps: [{
    name: 'eduvideo-backend',
    script: 'main.py',
    interpreter: 'python3',
    args: '3003',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '2G',
    env: {
      PYTHONUNBUFFERED: '1',
      PORT: '3003',
      ENVIRONMENT: 'production'
    },
    error_file: 'logs/err.log',
    out_file: 'logs/out.log',
    log_file: 'logs/combined.log',
    time: true
  }]
}
