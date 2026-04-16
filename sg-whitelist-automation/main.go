package main

import (
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"

	"github.com/aliyun/alibaba-cloud-sdk-go/services/ecs"
	"github.com/joho/godotenv"
)

const (
	ACCESS_KEY_ID_ENV     = "ALIBABA_CLOUD_ACCESS_KEY_ID"
	ACCESS_KEY_SECRET_ENV = "ALIBABA_CLOUD_ACCESS_KEY_SECRET"
	REGION_ID_ENV         = "ALIBABA_CLOUD_REGION_ID"
	SECURITY_GROUP_ID_ENV = "ALIBABA_CLOUD_SECURITY_GROUP_ID"
)

// Config holds the Alibaba Cloud configuration
type Config struct {
	AccessKeyID     string
	AccessKeySecret string
	RegionID        string
	SecurityGroupID string
}

// ECSClientInterface defines the methods from ecs.Client that we use.
// This allows for easier mocking in tests.
type ECSClientInterface interface {
	DescribeSecurityGroupAttribute(request *ecs.DescribeSecurityGroupAttributeRequest) (*ecs.DescribeSecurityGroupAttributeResponse, error)
	AuthorizeSecurityGroup(request *ecs.AuthorizeSecurityGroupRequest) (*ecs.AuthorizeSecurityGroupResponse, error)
}

// httpClient is an interface for http.Client to allow mocking in tests.
type httpClient interface {
	Get(url string) (*http.Response, error)
}

// defaultHTTPClient implements httpClient using the default http.Client.
type defaultHTTPClient struct{}

func (d *defaultHTTPClient) Get(url string) (*http.Response, error) {
	return http.Get(url)
}

var clientHTTP httpClient = &defaultHTTPClient{}

func getPublicIP() (string, error) {
	resp, err := clientHTTP.Get("https://checkip.amazonaws.com")
	if err != nil {
		return "", fmt.Errorf("failed to get public IP: %w", err)
	}
	defer resp.Body.Close()

	ip, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read public IP response: %w", err)
	}

	return strings.TrimSpace(string(ip)), nil
}

// loadConfig loads configuration from command-line flags, environment variables, and .env file.
func loadConfig() (*Config, error) {
	cfg := &Config{}

	// Define command-line flags
	flag.StringVar(&cfg.AccessKeyID, "access-key-id", "", "Alibaba Cloud Access Key ID")
	flag.StringVar(&cfg.AccessKeySecret, "access-key-secret", "", "Alibaba Cloud Access Key Secret")
	flag.StringVar(&cfg.RegionID, "region-id", "", "Alibaba Cloud Region ID")
	flag.StringVar(&cfg.SecurityGroupID, "security-group-id", "", "Alibaba Cloud Security Group ID")
	flag.Parse()

	// Load .env file as a fallback
	err := godotenv.Load(".env")
	if err != nil {
		fmt.Printf("Warning: Error loading .env file, falling back to environment variables: %v\n", err)
	}

	// Prioritize configuration: flags > environment variables > .env file
	if cfg.AccessKeyID == "" {
		cfg.AccessKeyID = os.Getenv(ACCESS_KEY_ID_ENV)
	}
	if cfg.AccessKeySecret == "" {
		cfg.AccessKeySecret = os.Getenv(ACCESS_KEY_SECRET_ENV)
	}
	if cfg.RegionID == "" {
		cfg.RegionID = os.Getenv(REGION_ID_ENV)
	}
	if cfg.SecurityGroupID == "" {
		cfg.SecurityGroupID = os.Getenv(SECURITY_GROUP_ID_ENV)
	}

	return cfg, nil
}

// validateConfig validates that all required configuration values are present.
func validateConfig(cfg *Config) error {
	if cfg.AccessKeyID == "" || cfg.AccessKeySecret == "" || cfg.RegionID == "" || cfg.SecurityGroupID == "" {
		return fmt.Errorf("Alibaba Cloud credentials (Access Key ID, Access Key Secret, Region ID, Security Group ID) must be provided via command-line flags, environment variables, or a .env file")
	}
	return nil
}

// createECSClientFunc is a variable that holds the function to create an ECS client.
// This allows it to be mocked in tests.
var createECSClientFunc = func(cfg *Config) (ECSClientInterface, error) {
	client, err := ecs.NewClientWithAccessKey(cfg.RegionID, cfg.AccessKeyID, cfg.AccessKeySecret)
	if err != nil {
		return nil, fmt.Errorf("error creating ECS client: %w", err)
	}
	return client, nil
}

// checkSecurityGroupRule checks if a security group rule for the given IP and port already exists.
func checkSecurityGroupRule(client ECSClientInterface, cfg *Config, publicIP string) (bool, error) {
	describeSecurityGroupAttributeRequest := ecs.CreateDescribeSecurityGroupAttributeRequest()
	describeSecurityGroupAttributeRequest.SecurityGroupId = cfg.SecurityGroupID
	describeSecurityGroupAttributeRequest.RegionId = cfg.RegionID

	describeSecurityGroupAttributeResponse, err := client.DescribeSecurityGroupAttribute(describeSecurityGroupAttributeRequest)
	if err != nil {
		return false, fmt.Errorf("error describing security group attributes: %w", err)
	}

	for _, permission := range describeSecurityGroupAttributeResponse.Permissions.Permission {
		fmt.Printf("Checking permission: IpProtocol=%s, PortRange=%s, SourceCidrIp=%s, Direction=%s, Policy=%s, NicType=%s\n",
			permission.IpProtocol, permission.PortRange, permission.SourceCidrIp, permission.Direction, permission.Policy, permission.NicType)

		if strings.ToLower(permission.IpProtocol) == "tcp" &&
			permission.PortRange == "443/443" &&
			permission.SourceCidrIp == publicIP+"/32" &&
			permission.Direction == "ingress" {
			return true, nil
		}
	}
	return false, nil
}

// addSecurityGroupRule adds a new security group rule for the given IP and port.
func addSecurityGroupRule(client ECSClientInterface, cfg *Config, publicIP string) error {
	authorizeSecurityGroupRequest := ecs.CreateAuthorizeSecurityGroupRequest()
	authorizeSecurityGroupRequest.SecurityGroupId = cfg.SecurityGroupID
	authorizeSecurityGroupRequest.RegionId = cfg.RegionID
	authorizeSecurityGroupRequest.IpProtocol = "tcp"
	authorizeSecurityGroupRequest.PortRange = "443/443"
	authorizeSecurityGroupRequest.SourceCidrIp = publicIP + "/32"
	authorizeSecurityGroupRequest.Policy = "accept"
	authorizeSecurityGroupRequest.NicType = "internet"
	fmt.Printf("Attempting to add rule with NicType: %s\n", authorizeSecurityGroupRequest.NicType)

	_, err := client.AuthorizeSecurityGroup(authorizeSecurityGroupRequest)
	if err != nil {
		return fmt.Errorf("error authorizing security group rule: %w", err)
	}

	return nil
}

// process contains the core logic of the application.
func process(cfg *Config) error {
	publicIP, err := getPublicIP()
	if err != nil {
		return fmt.Errorf("error getting public IP: %w", err)
	}
	fmt.Printf("Current public IP: %s\n", publicIP)

	client, err := createECSClientFunc(cfg)
	if err != nil {
		return fmt.Errorf("error creating ECS client: %w", err)
	}

	ruleExists, err := checkSecurityGroupRule(client, cfg, publicIP)
	if err != nil {
		return fmt.Errorf("error checking security group rule: %w", err)
	}

	if ruleExists {
		fmt.Printf("Security group rule for IP %s on port 443 already exists. Skipping.\n", publicIP)
		return nil // Exit successfully if rule exists
	}

	err = addSecurityGroupRule(client, cfg, publicIP)
	if err != nil {
		return fmt.Errorf("error adding security group rule: %w", err)
	}

	fmt.Printf("Successfully added security group rule for IP %s on port 443.\n", publicIP)
	return nil
}

func main() {
	cfg, err := loadConfig()
	if err != nil {
		fmt.Printf("Error loading configuration: %v\n", err)
		os.Exit(1)
	}

	err = validateConfig(cfg)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	if err := process(cfg); err != nil {
		fmt.Printf("Error during processing: %v\n", err)
		os.Exit(1)
	}
}
