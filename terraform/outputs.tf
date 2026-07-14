output "pipeline_sa_key_base64" {
  description = "Base64-encoded service account key JSON — decode this into a real key file, never commit it to Git."
  value       = google_service_account_key.pipeline_sa_key.private_key
  sensitive   = true
}