# 🚀 AWS Deployment Guide - Event Scheduler

This guide will help you deploy your Event Scheduler application to AWS using DynamoDB for data storage.

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Python 3.8+** installed
4. **Git** for version control

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   Flask API     │    │   AWS Services  │
│   (Port 8501)   │◄──►│   (Port 5000)   │◄──►│   DynamoDB      │
└─────────────────┘    └─────────────────┘    │   + S3          │
                                              └─────────────────┘
```

## 🔧 Step 1: AWS Setup

### 1.1 Create IAM User
```bash
# Create IAM user with programmatic access
# Attach policies: AmazonDynamoDBFullAccess, AmazonS3FullAccess
# Save Access Key ID and Secret Access Key
```

### 1.2 Configure AWS CLI
```bash
aws configure
# Enter your Access Key ID, Secret Access Key, and region
```

### 1.3 Create DynamoDB Table
```bash
# The table will be created automatically when you run the app
# Or create manually:
aws dynamodb create-table \
    --table-name events \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

## 🚀 Step 2: EC2 Deployment

### 2.1 Launch EC2 Instance
```bash
# Launch Amazon Linux 2 instance
# Instance type: t2.micro (free tier) or t2.small
# Security Group: Allow ports 22 (SSH), 5000 (Flask), 8501 (Streamlit)
```

### 2.2 Connect to EC2
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

### 2.3 Install Dependencies
```bash
# Update system
sudo yum update -y

# Install Python and Git
sudo yum install python3 python3-pip git -y

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
```

### 2.4 Clone and Setup Application
```bash
# Clone your repository
git clone <your-repo-url>
cd event-scheduler-backend

# Install Python dependencies
pip3 install -r requirements.txt
cd streamlit-ui
pip3 install -r requirements.txt
cd ..
```

### 2.5 Configure Environment
```bash
# Edit .env file with your AWS credentials
nano .env

# Add your AWS credentials:
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1
DYNAMODB_TABLE_NAME=events
```

### 2.6 Migrate Data (if needed)
```bash
# Run migration script to move data from JSON to DynamoDB
python3 migrate_to_dynamodb.py
```

### 2.7 Run Application
```bash
# Terminal 1: Run Flask API
python3 run.py

# Terminal 2: Run Streamlit UI
cd streamlit-ui
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

## 🐳 Step 3: Docker Deployment (Alternative)

### 3.1 Create Dockerfile for Flask API
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]
```

### 3.2 Create Dockerfile for Streamlit UI
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY streamlit-ui/requirements.txt .
RUN pip install -r requirements.txt

COPY streamlit-ui/ .

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

### 3.3 Build and Run with Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
    depends_on:
      - dynamodb-local

  ui:
    build: ./streamlit-ui
    ports:
      - "8501:8501"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
    depends_on:
      - api
```

## 📊 Step 4: Monitoring and Scaling

### 4.1 CloudWatch Monitoring
```bash
# Set up CloudWatch alarms for:
# - DynamoDB read/write capacity
# - EC2 CPU utilization
# - Application errors
```

### 4.2 Auto Scaling
```bash
# Create Auto Scaling Group for EC2 instances
# Set up Application Load Balancer
# Configure health checks
```

## 🔒 Step 5: Security Best Practices

### 5.1 IAM Roles
```bash
# Use IAM roles instead of access keys for EC2
# Create custom policies with minimal permissions
```

### 5.2 Security Groups
```bash
# Restrict access to specific IP ranges
# Use VPC for network isolation
```

### 5.3 Secrets Management
```bash
# Use AWS Secrets Manager for sensitive data
# Rotate credentials regularly
```

## 💰 Cost Optimization

### 6.1 DynamoDB Optimization
```bash
# Use on-demand billing for unpredictable workloads
# Use provisioned capacity for predictable workloads
# Implement TTL for old events
```

### 6.2 EC2 Optimization
```bash
# Use Spot Instances for non-critical workloads
# Right-size instances based on usage
# Use Reserved Instances for predictable workloads
```

## 🚨 Troubleshooting

### Common Issues:

1. **DynamoDB Connection Error**
   ```bash
   # Check AWS credentials
   aws sts get-caller-identity
   
   # Check table exists
   aws dynamodb describe-table --table-name events
   ```

2. **EC2 Security Group Issues**
   ```bash
   # Check security group rules
   # Ensure ports 5000 and 8501 are open
   ```

3. **Environment Variables**
   ```bash
   # Verify .env file is loaded
   # Check AWS region configuration
   ```

## 📈 Performance Tuning

### 7.1 DynamoDB Performance
```bash
# Use Global Secondary Indexes for complex queries
# Implement pagination for large datasets
# Use batch operations for bulk operations
```

### 7.2 Application Performance
```bash
# Use connection pooling
# Implement caching with Redis
# Optimize database queries
```

## 🔄 Backup and Recovery

### 8.1 Data Backup
```bash
# Enable DynamoDB point-in-time recovery
# Set up automated backups
# Export data to S3 regularly
```

### 8.2 Disaster Recovery
```bash
# Use multi-region deployment
# Implement failover mechanisms
# Test recovery procedures
```

## 📞 Support

For issues and questions:
- Check AWS documentation
- Review application logs
- Monitor CloudWatch metrics
- Contact AWS support if needed

---

**Happy Deploying! 🎉** 