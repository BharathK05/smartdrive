# SmartDrive infrastructure: everything in one file.
# Creates a VPC with one public subnet, a private S3 bucket (files + JSON data),
# an IAM role, and one EC2 web server. Jenkins runs `terraform apply` on every push.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws    = { source = "hashicorp/aws", version = "~> 6.0" }
    random = { source = "hashicorp/random", version = "~> 3.6" }
    tls    = { source = "hashicorp/tls", version = "~> 4.0" }
  }
}

variable "region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "my_ip" {
  description = "CIDR allowed to SSH into the server (Jenkins passes in its own public IP, e.g. 1.2.3.4/32)"
  type        = string
}

provider "aws" {
  region = var.region
  default_tags {
    tags = { Project = "smartdrive" }
  }
}

# ---------- Network: VPC with one public subnet ----------

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags                 = { Name = "smartdrive-vpc" }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "smartdrive-igw" }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true
  tags                    = { Name = "smartdrive-public" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = { Name = "smartdrive-public-rt" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Free S3 gateway endpoint: traffic from the server to S3 stays inside the AWS network.
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.public.id]
  tags              = { Name = "smartdrive-s3-endpoint" }
}

resource "aws_security_group" "web" {
  name        = "smartdrive-web"
  description = "HTTP from anywhere, SSH only from Jenkins"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "Website"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH for Jenkins deploys"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---------- Storage: one private S3 bucket ----------

resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "files" {
  bucket        = "smartdrive-files-${random_id.suffix.hex}"
  force_destroy = true # lets `terraform destroy` remove the bucket even if it still has files
}

resource "aws_s3_bucket_public_access_block" "files" {
  bucket                  = aws_s3_bucket.files.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ---------- Permissions: what the web server may do ----------

resource "aws_iam_role" "web" {
  name = "smartdrive-web-role"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "ec2.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy" "web" {
  name = "smartdrive-web-policy"
  role = aws_iam_role.web.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Allow", Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"], Resource = "${aws_s3_bucket.files.arn}/*" },
      { Effect = "Allow", Action = "s3:ListBucket", Resource = aws_s3_bucket.files.arn },
      { Effect = "Allow", Action = ["rekognition:DetectLabels", "comprehend:DetectKeyPhrases"], Resource = "*" },
    ]
  })
}

resource "aws_iam_instance_profile" "web" {
  name = "smartdrive-web-profile"
  role = aws_iam_role.web.name
}

# ---------- Web server ----------

resource "tls_private_key" "deploy" {
  algorithm = "ED25519"
}

resource "aws_key_pair" "deploy" {
  key_name   = "smartdrive-deploy"
  public_key = tls_private_key.deploy.public_key_openssh
}

resource "random_password" "flask_secret" {
  length  = 32
  special = false
}

data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

resource "aws_instance" "web" {
  ami                    = data.aws_ssm_parameter.al2023.value
  instance_type          = "t3.micro" # free-tier eligible
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.web.id]
  iam_instance_profile   = aws_iam_instance_profile.web.name
  key_name               = aws_key_pair.deploy.key_name

  # Runs once at first boot: install Python and Nginx, and register the app as a service.
  # Nginx (port 80) forwards requests to Gunicorn (127.0.0.1:8000), which runs the Flask app.
  # Jenkins copies the app code in afterwards.
  user_data_replace_on_change = true # this script only runs at first boot, so changing it rebuilds the server
  user_data                   = <<-EOF
    #!/bin/bash
    set -e
    dnf install -y python3.11 python3.11-pip nginx
    mkdir -p /opt/smartdrive
    chown ec2-user:ec2-user /opt/smartdrive

    cat > /etc/smartdrive.env <<ENV
    S3_BUCKET=${aws_s3_bucket.files.bucket}
    AWS_REGION=${var.region}
    SECRET_KEY=${random_password.flask_secret.result}
    ENV
    chmod 600 /etc/smartdrive.env

    cat > /etc/systemd/system/smartdrive.service <<UNIT
    [Unit]
    Description=SmartDrive web app
    After=network-online.target

    [Service]
    User=ec2-user
    WorkingDirectory=/opt/smartdrive
    EnvironmentFile=/etc/smartdrive.env
    ExecStart=/opt/smartdrive/venv/bin/gunicorn --workers 1 --threads 4 --bind 127.0.0.1:8000 app:app
    Restart=always

    [Install]
    WantedBy=multi-user.target
    UNIT
    systemctl daemon-reload

    # Nginx: the public web server. Serves CSS/JS itself and passes everything else to Gunicorn.
    cat > /etc/nginx/nginx.conf <<'NGINX'
    user nginx;
    worker_processes auto;
    error_log /var/log/nginx/error.log notice;
    pid /run/nginx.pid;

    events {
        worker_connections 1024;
    }

    http {
        include /etc/nginx/mime.types;
        default_type application/octet-stream;
        types_hash_max_size 4096;
        access_log /var/log/nginx/access.log;
        sendfile on;
        server_tokens off;
        client_max_body_size 11m; # the app allows uploads up to 10 MB

        server {
            listen 80 default_server;
            server_name _;

            location /static/ {
                alias /opt/smartdrive/static/;
                add_header Cache-Control "no-cache"; # browsers re-check after each deploy
            }

            location / {
                proxy_pass http://127.0.0.1:8000;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_read_timeout 60s; # AI tagging can take a few seconds
            }
        }
    }
    NGINX
    systemctl enable --now nginx
  EOF

  lifecycle {
    ignore_changes = [ami] # don't rebuild the server every time Amazon publishes a new AMI
  }

  tags = { Name = "smartdrive-web" }
}

# ---------- Outputs (Jenkins reads these) ----------

output "app_ip" {
  value = aws_instance.web.public_ip
}

output "app_url" {
  value = "http://${aws_instance.web.public_ip}"
}

output "bucket_name" {
  value = aws_s3_bucket.files.bucket
}

output "ssh_private_key" {
  value     = tls_private_key.deploy.private_key_openssh
  sensitive = true
}
