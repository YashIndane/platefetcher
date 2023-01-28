#Creating the S3 Bucket for using Textract functionality

resource "aws_s3_bucket" "platfetcher-buck" {
  bucket = var.bucket_name
  tags = {
    Name = var.bucket_name
  }
}

resource "aws_s3_bucket_public_access_block" "s3_public_access" {
  bucket                  = aws_s3_bucket.platfetcher-buck.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "Public_access_to_bucket" {
  bucket = aws_s3_bucket.platfetcher-buck.id
  policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:*",
        "Resource": "${aws_s3_bucket.platfetcher-buck.arn}/*"

      }

    ]
  }
  EOF
}

#Creating RDS instance

resource "aws_db_instance" "platefetcher-db" {
  identifier          = var.identifier
  allocated_storage   = 10
  engine              = var.db_engine
  engine_version      = var.db_engine_version
  instance_class      = var.db_class
  username            = var.db_username
  password            = var.db_pass
  skip_final_snapshot = true
  publicly_accessible = true

}

output "rds_instance_endpoint" {
  value = aws_db_instance.platefetcher-db.endpoint
}
