# ── Bedrock Model Access ────────────────────────────────────
# Note: Model access must be enabled in the AWS Console for
# the account. These resources configure IAM permissions and
# logging for Bedrock usage.

resource "aws_iam_policy" "bedrock_access" {
  name        = "ayurvani-bedrock-access"
  description = "Permissions for AyurVani to invoke Amazon Nova models"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "InvokeNovaModels"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.nova-lite-v1:0",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.nova-sonic-v1:0",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.nova-embed-multimodal-v1:0"
        ]
      },
      {
        Sid    = "ListModels"
        Effect = "Allow"
        Action = [
          "bedrock:ListFoundationModels",
          "bedrock:GetFoundationModel"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_bedrock" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.bedrock_access.arn
}

# ── Bedrock Logging ─────────────────────────────────────────
resource "aws_cloudwatch_log_group" "bedrock" {
  name              = "/aws/bedrock/ayurvani"
  retention_in_days = 90
}

resource "aws_s3_bucket" "bedrock_logs" {
  bucket = "ayurvani-bedrock-logs-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "bedrock_logs" {
  bucket                  = aws_s3_bucket.bedrock_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ── OpenSearch Serverless for Vector Search ─────────────────
resource "aws_opensearchserverless_collection" "knowledge_base" {
  name        = "ayurvani-kb"
  description = "Vector store for Ayurveda knowledge base embeddings"
  type        = "VECTORSEARCH"
}

resource "aws_opensearchserverless_security_policy" "encryption" {
  name = "ayurvani-kb-encryption"
  type = "encryption"

  policy = jsonencode({
    Rules = [{
      ResourceType = "collection"
      Resource      = ["collection/ayurvani-kb"]
    }]
    AWSOwnedKey = true
  })
}

resource "aws_opensearchserverless_access_policy" "data_access" {
  name = "ayurvani-kb-access"
  type = "data"

  policy = jsonencode([{
    Rules = [
      {
        ResourceType = "collection"
        Resource      = ["collection/ayurvani-kb"]
        Permission   = [
          "aoss:CreateCollectionItems",
          "aoss:UpdateCollectionItems",
          "aoss:DescribeCollectionItems"
        ]
      },
      {
        ResourceType = "index"
        Resource      = ["index/ayurvani-kb/*"]
        Permission   = [
          "aoss:CreateIndex",
          "aoss:UpdateIndex",
          "aoss:DescribeIndex",
          "aoss:ReadDocument",
          "aoss:WriteDocument"
        ]
      }
    ]
    Principal = [aws_iam_role.ecs_task.arn]
  }])
}

resource "aws_opensearchserverless_security_policy" "network" {
  name = "ayurvani-kb-network"
  type = "network"

  policy = jsonencode([{
    Rules = [{
      ResourceType = "collection"
      Resource      = ["collection/ayurvani-kb"]
    }]
    AllowFromPublic = false
    SourceVPCEs     = [] # Add VPC endpoint ID when configured
  }])
}

output "opensearch_endpoint" {
  value = aws_opensearchserverless_collection.knowledge_base.collection_endpoint
}