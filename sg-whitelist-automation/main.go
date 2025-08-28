package main

import (
	// Added for command-line flag parsing
	"flag"
	"fmt"
	"io" // Use "io" instead of "io/ioutil"
	"net/http"
	"os"
	"strings"

	"github.com/aliyun/alibaba-cloud-sdk-go/services/ecs"
	"github.com/joho/godotenv"
)

const (
	// Environment variables for Alibaba Cloud credentials
	ACCESS_KEY_ID_ENV     = "ALIBABA_CLOUD_ACCESS_KEY_ID"
	ACCESS_KEY_SECRET_ENV = "ALIBABA_CLOUD_ACCESS_KEY_SECRET"
	REGION_ID_ENV         = "ALIBABA_CLOUD_REGION_ID"
	SECURITY_GROUP_ID_ENV = "ALIBABA_CLOUD_SECURITY_GROUP_ID"
)

// Variables to hold configuration values
var (
	accessKeyID     string
	accessKeySecret string
	regionID        string
	securityGroupID string
)

func getPublicIP() (string, error) {
	resp, err := http.Get("https://checkip.amazonaws.com")
	if err != nil {
		return "", fmt.Errorf("failed to get public IP: %w", err)
	}
	defer resp.Body.Close()

	ip, err := io.ReadAll(resp.Body) // Use io.ReadAll
	if err != nil {
		return "", fmt.Errorf("failed to read public IP response: %w", err)
	}

	return strings.TrimSpace(string(ip)), nil
}

func main() {
	// Define command-line flags
	flag.StringVar(&accessKeyID, "access-key-id", "", "Alibaba Cloud Access Key ID")
	flag.StringVar(&accessKeySecret, "access-key-secret", "", "Alibaba Cloud Access Key Secret")
	flag.StringVar(&regionID, "region-id", "", "Alibaba Cloud Region ID")
	flag.StringVar(&securityGroupID, "security-group-id", "", "Alibaba Cloud Security Group ID")
	flag.Parse()

	// Load .env file as a fallback
	err := godotenv.Load(".env")
	if err != nil {
		fmt.Printf("Warning: Error loading .env file, falling back to environment variables: %v\n", err)
	}

	// Prioritize configuration: flags > environment variables > .env file
	if accessKeyID == "" {
		accessKeyID = os.Getenv(ACCESS_KEY_ID_ENV)
	}
	if accessKeySecret == "" {
		accessKeySecret = os.Getenv(ACCESS_KEY_SECRET_ENV)
	}
	if regionID == "" {
		regionID = os.Getenv(REGION_ID_ENV)
	}
	if securityGroupID == "" {
		securityGroupID = os.Getenv(SECURITY_GROUP_ID_ENV)
	}

	// Validate credentials
	if accessKeyID == "" || accessKeySecret == "" || regionID == "" || securityGroupID == "" {
		fmt.Printf("Error: Alibaba Cloud credentials (Access Key ID, Access Key Secret, Region ID, Security Group ID) must be provided via command-line flags, environment variables, or a .env file.\n")
		os.Exit(1)
	}

	// 1. Get public IP
	publicIP, err := getPublicIP()
	if err != nil {
		fmt.Printf("Error getting public IP: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Current public IP: %s\n", publicIP)

	// 2. Create ECS client
	client, err := ecs.NewClientWithAccessKey(regionID, accessKeyID, accessKeySecret)
	if err != nil {
		fmt.Printf("Error creating ECS client: %v\n", err)
		os.Exit(1)
	}

	// 4. Check if rule exists
	describeSecurityGroupAttributeRequest := ecs.CreateDescribeSecurityGroupAttributeRequest()
	describeSecurityGroupAttributeRequest.SecurityGroupId = securityGroupID
	describeSecurityGroupAttributeRequest.RegionId = regionID

	describeSecurityGroupAttributeResponse, err := client.DescribeSecurityGroupAttribute(describeSecurityGroupAttributeRequest)
	if err != nil {
		fmt.Printf("Error describing security group attributes: %v\n", err)
		os.Exit(1)
	}

	ruleExists := false
	for _, permission := range describeSecurityGroupAttributeResponse.Permissions.Permission {
		fmt.Printf("Checking permission: IpProtocol=%s, PortRange=%s, SourceCidrIp=%s, Direction=%s, Policy=%s, NicType=%s\n",
			permission.IpProtocol, permission.PortRange, permission.SourceCidrIp, permission.Direction, permission.Policy, permission.NicType)

		if strings.ToLower(permission.IpProtocol) == "tcp" &&
			permission.PortRange == "443/443" &&
			permission.SourceCidrIp == publicIP+"/32" &&
			permission.Direction == "ingress" { // Added case-insensitive NicType check
			ruleExists = true
			break
		}
	}

	if ruleExists {
		fmt.Printf("Security group rule for IP %s on port 443 already exists. Skipping.\n", publicIP)
		os.Exit(0)
	}

	// 5. Add rule if it doesn't exist
	authorizeSecurityGroupRequest := ecs.CreateAuthorizeSecurityGroupRequest()
	authorizeSecurityGroupRequest.SecurityGroupId = securityGroupID
	authorizeSecurityGroupRequest.RegionId = regionID
	authorizeSecurityGroupRequest.IpProtocol = "tcp"
	authorizeSecurityGroupRequest.PortRange = "443/443"
	authorizeSecurityGroupRequest.SourceCidrIp = publicIP + "/32"
	authorizeSecurityGroupRequest.Policy = "accept"
	authorizeSecurityGroupRequest.NicType = "internet" // Changed to "internet" for public IP access
	fmt.Printf("Attempting to add rule with NicType: %s\n", authorizeSecurityGroupRequest.NicType)

	_, err = client.AuthorizeSecurityGroup(authorizeSecurityGroupRequest)
	if err != nil {
		fmt.Printf("Error authorizing security group rule: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Successfully added security group rule for IP %s on port 443.\n", publicIP)
}
