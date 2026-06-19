output "api_endpoint" {
  description = "API Gateway HTTP API endpoint"
  value       = aws_apigatewayv2_api.audit_api.api_endpoint
}

output "api_id" {
  description = "API Gateway HTTP API ID"
  value       = aws_apigatewayv2_api.audit_api.id
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.compliance_audit.function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.compliance_audit.arn
}

output "lambda_role_arn" {
  description = "Lambda execution role ARN"
  value       = aws_iam_role.lambda_audit_role.arn
}

output "audit_url" {
  description = "Full URL to trigger compliance audit"
  value       = "${aws_apigatewayv2_api.audit_api.api_endpoint}/${var.environment}/audit"
}
