variable "access_key" {
  description = "AWS Access Key"
  type        = string
}

variable "secret_key" {
  description = "AWS Secrect Key"
  type        = string
}

variable "bucket_name" {
  description = "AWS S3 bucket name"
  type        = string
}

variable "identifier" {
  description = "RDS instance name"
  type        = string
}

variable "db_engine" {
  description = "RDS instance db engine"
  type        = string
  default     = "mysql"
}

variable "db_engine_version" {
  description = "RDS instance db version"
  type        = string
  default     = "5.7"
}

variable "db_class" {
  description = "RDS instance db class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_username" {
  description = "RDS db username"
  type        = string
}

variable "db_pass" {
  description = "RDS db password"
  type        = string
}
