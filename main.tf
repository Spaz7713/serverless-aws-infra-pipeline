"""
OpenTofu config for serverless audit infrastructure.
Deployes API Gateway, Lambda, IAM, and CloudWatch logging.
"""

terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "OpenTofu"
    }
  }
}

# Lambda execution role
resource "aws_iam_role" "lambda_audit_role" {
  name_prefix = "lambda-audit-role-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Least privilege IAM policy for audit access
resource "aws_iam_role_policy" "lambda_audit_policy" {
  name_prefix = "lambda-audit-policy-"
  role        = aws_iam_role.lambda_audit_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "CloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/*"
      },
      {
        Sid    = "IAMAudit"
        Effect = "Allow"
        Action = [
          "iam:ListUsers",
          "iam:ListUserPolicies",
          "iam:GetUserPolicy"
        ]
        Resource = "*"
      },
      {
        Sid    = "S3Audit"
        Effect = "Allow"
        Action = [
          "s3:ListAllMyBuckets",
          "s3:GetBucketEncryption",
          "s3:GetPublicAccessBlock"
        ]
        Resource = "*"
      },
      {
        Sid    = "EC2Audit"
        Effect = "Allow"
        Action = [
          "ec2:DescribeSecurityGroups"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda deployment
resource "aws_lambda_function" "compliance_audit" {
  filename         = "lambda_function.zip"
  function_name    = "${var.project_name}-audit"
  role             = aws_iam_role.lambda_audit_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("lambda_function.zip")
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 512

  environment {
    variables = {
      ENVIRONMENT = var.environment
      LOG_LEVEL   = "INFO"
    }
  }
}

# HTTP API with CORS
resource "aws_apigatewayv2_api" "audit_api" {
  name          = "${var.project_name}-audit-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = var.cors_allow_origins
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["content-type", "authorization"]
  }
}

# API stage config
resource "aws_apigatewayv2_stage" "audit_api_stage" {
  api_id      = aws_apigatewayv2_api.audit_api.id
  name        = var.environment
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_logs.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      resourcePath   = "$context.resourcePath"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      error          = "$context.error.messageString"
    })
  }
}

# CloudWatch logs for API requests
resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/aws/api-gateway/${var.project_name}-audit"
  retention_in_days = 7
}

# Lambda proxy integration
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.audit_api.id
  integration_type = "AWS_PROXY"
  integration_method = "POST"
  integration_uri  = aws_lambda_function.compliance_audit.invoke_arn
  payload_format_version = "2.0"
}

# Route: GET /audit
resource "aws_apigatewayv2_route" "audit_route" {
  api_id    = aws_apigatewayv2_api.audit_api.id
  route_key = "GET /audit"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Route: OPTIONS /audit (CORS preflight)
resource "aws_apigatewayv2_route" "audit_route_options" {
  api_id    = aws_apigatewayv2_api.audit_api.id
  route_key = "OPTIONS /audit"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Allow API Gateway to invoke Lambda
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.compliance_audit.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.audit_api.execution_arn}/*"
}

# CloudWatch logs for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.compliance_audit.function_name}"
  retention_in_days = 7
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}
