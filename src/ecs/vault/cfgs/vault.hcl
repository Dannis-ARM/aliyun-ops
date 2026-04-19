# Use Cloudflare R2 as the storage backend (S3 compatible)
storage "s3" {
  # Replace with your Cloudflare Account ID
  endpoint = "https://<YOUR_CF_ACCOUNT_ID>.r2.cloudflarestorage.com"
  bucket   = "vault-secrets"
  region   = "auto"
  
  # Credentials should be injected via ENV or replaced here
  access_key = "YOUR_R2_ACCESS_KEY"
  secret_key = "YOUR_R2_SECRET_KEY"
}

# TCP Listener configuration
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 1 # Set to 0 if you have certs
}

# Enable the web UI
ui = true

# Audit logging (Optional but recommended for SRE)
# Note: Ensure the container has write access to this path
# path = "/vault/logs/audit.log"

api_addr     = "http://<YOUR_ALI_IP>:8200"
cluster_addr = "http://<YOUR_ALI_IP>:8201"