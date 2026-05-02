module.exports = {
  apps: [
    {
      name: 'costos-backend',
      cwd: '/var/www/costos/backend',
      script: 'venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 3001',
      exec_mode: 'fork',
      interpreter: 'none',
      env: {
        PORT: 3001
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '256M',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: '/var/log/costos/backend-error.log',
      out_file: '/var/log/costos/backend-out.log'
    }
  ]
}
