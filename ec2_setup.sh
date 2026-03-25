#!/bin/bash
# deployment/aws/ec2_setup.sh
# Bootstrap script for Ubuntu 24.04 EC2 instance

set -e

echo "=== AI Hiring Agent System - EC2 Bootstrap ==="

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io docker-compose-v2 git nginx certbot python3-certbot-nginx

# Enable Docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Clone repo (update with your repo URL)
git clone https://github.com/YOUR_ORG/ai-hiring-system.git /home/ubuntu/app
cd /home/ubuntu/app

# Copy env file
cp .env.example .env
echo "⚠️  Edit /home/ubuntu/app/.env with real credentials before running!"

# Pull and start
sudo docker compose -f deployment/docker-compose.yml up -d --build

# Setup nginx reverse proxy
sudo tee /etc/nginx/sites-available/hiring-api > /dev/null <<'EOF'
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 20M;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/hiring-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# SSL (replace with your domain)
# sudo certbot --nginx -d api.your-domain.com

echo "=== Setup complete. API running at http://localhost:8000 ==="
