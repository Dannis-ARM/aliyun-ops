package main

import (
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
	// Load .env file
	err := godotenv.Load(".env")
	if err != nil {
		fmt.Printf("Warning: Error loading .env file, falling back to system environment variables: %v\n", err)
	}

	// 1. Get public IP
	publicIP, err := getPublicIP()
	if err != nil {
		fmt.Printf("Error getting public IP: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Current public IP: %s\n", publicIP)

	// 2. Get Alibaba Cloud credentials and region from environment variables
	accessKeyID := os.Getenv(ACCESS_KEY_ID_ENV)
	accessKeySecret := os.Getenv(ACCESS_KEY_SECRET_ENV)
	regionID := os.Getenv(REGION_ID_ENV)
	securityGroupID := os.Getenv(SECURITY_GROUP_ID_ENV)

	if accessKeyID == "" || accessKeySecret == "" || regionID == "" || securityGroupID == "" {
		fmt.Printf("Error: Alibaba Cloud credentials (ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET, ALIBABA_CLOUD_REGION_ID, ALIBABA_CLOUD_SECURITY_GROUP_ID) must be set as environment variables.\n")
		os.Exit(1)
	}

	// 3. Create ECS client
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
		if permission.IpProtocol == "tcp" &&
			permission.PortRange == "443/443" &&
			permission.SourceCidrIp == publicIP+"/32" &&
			permission.Direction == "ingress" {
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

	_, err = client.AuthorizeSecurityGroup(authorizeSecurityGroupRequest)
	if err != nil {
		fmt.Printf("Error authorizing security group rule: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Successfully added security group rule for IP %s on port 443.\n", publicIP)
}
