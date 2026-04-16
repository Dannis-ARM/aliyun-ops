package main

import (
	"bytes"
	"errors"
	"flag"
	"io"
	"net/http"
	"os"
	"strings"
	"testing"

	"github.com/aliyun/alibaba-cloud-sdk-go/services/ecs"
)

// Helper function to reset flags for testing
func resetFlags() {
	flag.CommandLine = flag.NewFlagSet(os.Args[0], flag.ExitOnError)
}

// MockHTTPClient for getPublicIP tests
type MockHTTPClient struct {
	GetResponse *http.Response
	GetError    error
}

func (m *MockHTTPClient) Get(url string) (*http.Response, error) {
	return m.GetResponse, m.GetError
}

// MockECSClient for process tests
type MockECSClient struct {
	DescribeSecurityGroupAttributeResponse *ecs.DescribeSecurityGroupAttributeResponse
	DescribeSecurityGroupAttributeError    error
	AuthorizeSecurityGroupResponse         *ecs.AuthorizeSecurityGroupResponse
	AuthorizeSecurityGroupError            error
}

func (m *MockECSClient) DescribeSecurityGroupAttribute(request *ecs.DescribeSecurityGroupAttributeRequest) (*ecs.DescribeSecurityGroupAttributeResponse, error) {
	return m.DescribeSecurityGroupAttributeResponse, m.DescribeSecurityGroupAttributeError
}

func (m *MockECSClient) AuthorizeSecurityGroup(request *ecs.AuthorizeSecurityGroupRequest) (*ecs.AuthorizeSecurityGroupResponse, error) {
	return m.AuthorizeSecurityGroupResponse, m.AuthorizeSecurityGroupError
}

func TestLoadConfig_Flags(t *testing.T) {
	resetFlags()
	os.Clearenv() // Clear environment variables to ensure flags are prioritized

	// Set up command-line arguments
	os.Args = []string{
		"test",
		"-access-key-id", "flag_id",
		"-access-key-secret", "flag_secret",
		"-region-id", "flag_region",
		"-security-group-id", "flag_sg",
	}

	cfg, err := loadConfig()
	if err != nil {
		t.Fatalf("loadConfig returned an error: %v", err)
	}
	if cfg == nil {
		t.Fatal("loadConfig returned a nil config")
	}
	if cfg.AccessKeyID != "flag_id" {
		t.Errorf("Expected AccessKeyID 'flag_id', got '%s'", cfg.AccessKeyID)
	}
	if cfg.AccessKeySecret != "flag_secret" {
		t.Errorf("Expected AccessKeySecret 'flag_secret', got '%s'", cfg.AccessKeySecret)
	}
	if cfg.RegionID != "flag_region" {
		t.Errorf("Expected RegionID 'flag_region', got '%s'", cfg.RegionID)
	}
	if cfg.SecurityGroupID != "flag_sg" {
		t.Errorf("Expected SecurityGroupID 'flag_sg', got '%s'", cfg.SecurityGroupID)
	}
}

func TestLoadConfig_EnvironmentVariables(t *testing.T) {
	resetFlags()
	os.Clearenv() // Clear environment variables first

	// Set environment variables
	os.Setenv(ACCESS_KEY_ID_ENV, "env_id")
	os.Setenv(ACCESS_KEY_SECRET_ENV, "env_secret")
	os.Setenv(REGION_ID_ENV, "env_region")
	os.Setenv(SECURITY_GROUP_ID_ENV, "env_sg")

	// Ensure no flags are set
	os.Args = []string{"test"}

	cfg, err := loadConfig()
	if err != nil {
		t.Fatalf("loadConfig returned an error: %v", err)
	}
	if cfg == nil {
		t.Fatal("loadConfig returned a nil config")
	}
	if cfg.AccessKeyID != "env_id" {
		t.Errorf("Expected AccessKeyID 'env_id', got '%s'", cfg.AccessKeyID)
	}
	if cfg.AccessKeySecret != "env_secret" {
		t.Errorf("Expected AccessKeySecret 'env_secret', got '%s'", cfg.AccessKeySecret)
	}
	if cfg.RegionID != "env_region" {
		t.Errorf("Expected RegionID 'env_region', got '%s'", cfg.RegionID)
	}
	if cfg.SecurityGroupID != "env_sg" {
		t.Errorf("Expected SecurityGroupID 'env_sg', got '%s'", cfg.SecurityGroupID)
	}

	// Clean up environment variables
	os.Unsetenv(ACCESS_KEY_ID_ENV)
	os.Unsetenv(ACCESS_KEY_SECRET_ENV)
	os.Unsetenv(REGION_ID_ENV)
	os.Unsetenv(SECURITY_GROUP_ID_ENV)
}

func TestLoadConfig_Priority(t *testing.T) {
	resetFlags()
	os.Clearenv()

	// Set environment variables
	os.Setenv(ACCESS_KEY_ID_ENV, "env_id")
	os.Setenv(ACCESS_KEY_SECRET_ENV, "env_secret")

	// Set up command-line arguments (should override env vars for AccessKeyID and RegionID)
	os.Args = []string{
		"test",
		"-access-key-id", "flag_id",
		"-region-id", "flag_region",
	}

	cfg, err := loadConfig()
	if err != nil {
		t.Fatalf("loadConfig returned an error: %v", err)
	}
	if cfg == nil {
		t.Fatal("loadConfig returned a nil config")
	}
	if cfg.AccessKeyID != "flag_id" {
		t.Errorf("Expected AccessKeyID 'flag_id', got '%s'", cfg.AccessKeyID)
	}
	if cfg.AccessKeySecret != "env_secret" {
		t.Errorf("Expected AccessKeySecret 'env_secret', got '%s'", cfg.AccessKeySecret)
	}
	if cfg.RegionID != "flag_region" {
		t.Errorf("Expected RegionID 'flag_region', got '%s'", cfg.RegionID)
	}
	if cfg.SecurityGroupID != "" {
		t.Errorf("Expected SecurityGroupID '', got '%s'", cfg.SecurityGroupID)
	}

	os.Unsetenv(ACCESS_KEY_ID_ENV)
	os.Unsetenv(ACCESS_KEY_SECRET_ENV)
}

func TestValidateConfig_Valid(t *testing.T) {
	cfg := &Config{
		AccessKeyID:     "id",
		AccessKeySecret: "secret",
		RegionID:        "region",
		SecurityGroupID: "sg",
	}
	err := validateConfig(cfg)
	if err != nil {
		t.Errorf("validateConfig returned an unexpected error: %v", err)
	}
}

func TestValidateConfig_Invalid(t *testing.T) {
	tests := []struct {
		name string
		cfg  *Config
	}{
		{
			name: "Missing AccessKeyID",
			cfg: &Config{
				AccessKeyID:     "",
				AccessKeySecret: "secret",
				RegionID:        "region",
				SecurityGroupID: "sg",
			},
		},
		{
			name: "Missing AccessKeySecret",
			cfg: &Config{
				AccessKeyID:     "id",
				AccessKeySecret: "",
				RegionID:        "region",
				SecurityGroupID: "sg",
			},
		},
		{
			name: "Missing RegionID",
			cfg: &Config{
				AccessKeyID:     "id",
				AccessKeySecret: "secret",
				RegionID:        "",
				SecurityGroupID: "sg",
			},
		},
		{
			name: "Missing SecurityGroupID",
			cfg: &Config{
				AccessKeyID:     "id",
				AccessKeySecret: "secret",
				RegionID:        "region",
				SecurityGroupID: "",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validateConfig(tt.cfg)
			if err == nil {
				t.Errorf("validateConfig expected an error for %s, but got none", tt.name)
			}
			expectedErrorPart := "Alibaba Cloud credentials"
			if err != nil && !strings.Contains(err.Error(), expectedErrorPart) {
				t.Errorf("validateConfig expected error message to contain '%s', got '%s'", expectedErrorPart, err.Error())
			}
		})
	}
}

func TestGetPublicIP(t *testing.T) {
	// Save original clientHTTP and restore after test
	originalClientHTTP := clientHTTP
	defer func() { clientHTTP = originalClientHTTP }()

	tests := []struct {
		name        string
		mockResp    *http.Response
		mockErr     error
		expectedIP  string
		expectedErr string
	}{
		{
			name: "Successful IP retrieval",
			mockResp: &http.Response{
				StatusCode: 200,
				Body:       io.NopCloser(bytes.NewBufferString("192.168.1.1\n")),
			},
			mockErr:    nil,
			expectedIP: "192.168.1.1",
		},
		{
			name:        "HTTP Get error",
			mockResp:    nil,
			mockErr:     errors.New("network error"),
			expectedIP:  "",
			expectedErr: "failed to get public IP: network error",
		},
		{
			name: "Failed to read response body",
			mockResp: &http.Response{
				StatusCode: 200,
				Body:       io.NopCloser(errorReader{}),
			},
			mockErr:     nil,
			expectedIP:  "",
			expectedErr: "failed to read public IP response: read error",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			clientHTTP = &MockHTTPClient{
				GetResponse: tt.mockResp,
				GetError:    tt.mockErr,
			}

			ip, err := getPublicIP()

			if tt.expectedErr != "" {
				if err == nil || !strings.Contains(err.Error(), tt.expectedErr) {
					t.Errorf("Expected error containing '%s', got '%v'", tt.expectedErr, err)
				}
			} else {
				if err != nil {
					t.Errorf("Did not expect an error, but got: %v", err)
				}
				if ip != tt.expectedIP {
					t.Errorf("Expected IP '%s', got '%s'", tt.expectedIP, ip)
				}
			}
		})
	}
}

// errorReader is a mock io.Reader that always returns an error.
type errorReader struct{}

func (er errorReader) Read(p []byte) (n int, err error) {
	return 0, errors.New("read error")
}

func TestProcess(t *testing.T) {
	// Save original clientHTTP and restore after test
	originalClientHTTP := clientHTTP
	defer func() { clientHTTP = originalClientHTTP }()

	mockConfig := &Config{
		AccessKeyID:     "test_id",
		AccessKeySecret: "test_secret",
		RegionID:        "test_region",
		SecurityGroupID: "test_sg",
	}
	mockPublicIP := "1.2.3.4"

	t.Run("Successfully adds rule", func(t *testing.T) {
		clientHTTP = &MockHTTPClient{
			GetResponse: &http.Response{
				StatusCode: 200,
				Body:       io.NopCloser(bytes.NewBufferString(mockPublicIP + "\n")),
			},
			GetError: nil,
		}

		mockECS := &MockECSClient{
			DescribeSecurityGroupAttributeResponse: &ecs.DescribeSecurityGroupAttributeResponse{
				Permissions: ecs.Permissions{
					Permission: []ecs.Permission{}, // No existing rules
				},
			},
			AuthorizeSecurityGroupResponse: &ecs.AuthorizeSecurityGroupResponse{},
		}

		// Temporarily replace createECSClientFunc to return our mock
		originalCreateECSClientFunc := createECSClientFunc
		createECSClientFunc = func(cfg *Config) (ECSClientInterface, error) {
			return mockECS, nil
		}
		defer func() { createECSClientFunc = originalCreateECSClientFunc }()

		err := process(mockConfig)
		if err != nil {
			t.Errorf("process returned an unexpected error: %v", err)
		}
	})

	t.Run("Rule already exists", func(t *testing.T) {
		clientHTTP = &MockHTTPClient{
			GetResponse: &http.Response{
				StatusCode: 200,
				Body:       io.NopCloser(bytes.NewBufferString(mockPublicIP + "\n")),
			},
			GetError: nil,
		}

		mockECS := &MockECSClient{
			DescribeSecurityGroupAttributeResponse: &ecs.DescribeSecurityGroupAttributeResponse{
				Permissions: ecs.Permissions{
					Permission: []ecs.Permission{
						{
							IpProtocol:   "tcp",
							PortRange:    "443/443",
							SourceCidrIp: mockPublicIP + "/32",
							Direction:    "ingress",
						},
					},
				},
			},
			AuthorizeSecurityGroupError: errors.New("should not be called"), // Should not attempt to authorize
		}

		originalCreateECSClientFunc := createECSClientFunc
		createECSClientFunc = func(cfg *Config) (ECSClientInterface, error) {
			return mockECS, nil
		}
		defer func() { createECSClientFunc = originalCreateECSClientFunc }()

		err := process(mockConfig)
		if err != nil {
			t.Errorf("process returned an unexpected error: %v", err)
		}
	})

	t.Run("Error getting public IP", func(t *testing.T) {
		clientHTTP = &MockHTTPClient{
			GetResponse: nil,
			GetError:    errors.New("ip fetch error"),
		}

		err := process(mockConfig)
		if err == nil || !strings.Contains(err.Error(), "error getting public IP: ip fetch error") {
			t.Errorf("Expected error 'error getting public IP: ip fetch error', got '%v'", err)
		}
	})

	t.Run("Error creating ECS client", func(t *testing.T) {
		clientHTTP = &MockHTTPClient{
			GetResponse: &http.Response{
				StatusCode: 200,
				Body:       io.NopCloser(bytes.NewBufferString(mockPublicIP + "\n")),
			},
			GetError: nil,
		}

		originalCreateECSClientFunc := createECSClientFunc
		createECSClientFunc = func(cfg *Config) (ECSClientInterface, error) {
			return nil, errors.New("ecs client error")
		}
		defer func() { createECSClientFunc = originalCreateECSClientFunc }()

		err := process(mockConfig)
		if err == nil || !strings.Contains(err.Error(), "error creating ECS client: ecs client error") {
			t.Errorf("Expected error 'error creating ECS client: ecs client error', got '%v'", err)
		}
	})

	t.Run("Error checking security group rule", func(t *testing.T) {
		clientHTTP = &MockHTTPClient{
			GetResponse: &http.Response{
				StatusCode: 200,
				Body:       io.NopCloser(bytes.NewBufferString(mockPublicIP + "\n")),
			},
			GetError: nil,
		}

		mockECS := &MockECSClient{
			DescribeSecurityGroupAttributeError: errors.New("describe error"),
		}

		originalCreateECSClientFunc := createECSClientFunc
		createECSClientFunc = func(cfg *Config) (ECSClientInterface, error) {
			return mockECS, nil
		}
		defer func() { createECSClientFunc = originalCreateECSClientFunc }()

		err := process(mockConfig)
		if err == nil || !strings.Contains(err.Error(), "error checking security group rule: describe error") {
			t.Errorf("Expected error 'error checking security group rule: describe error', got '%v'", err)
		}
	})

	t.Run("Error adding security group rule", func(t *testing.T) {
		clientHTTP = &MockHTTPClient{
			GetResponse: &http.Response{
				StatusCode: 200,
				Body:       io.NopCloser(bytes.NewBufferString(mockPublicIP + "\n")),
			},
			GetError: nil,
		}

		mockECS := &MockECSClient{
			DescribeSecurityGroupAttributeResponse: &ecs.DescribeSecurityGroupAttributeResponse{
				Permissions: ecs.Permissions{
					Permission: []ecs.Permission{}, // No existing rules
				},
			},
			AuthorizeSecurityGroupError: errors.New("authorize error"),
		}

		originalCreateECSClientFunc := createECSClientFunc
		createECSClientFunc = func(cfg *Config) (ECSClientInterface, error) {
			return mockECS, nil
		}
		defer func() { createECSClientFunc = originalCreateECSClientFunc }()

		err := process(mockConfig)
		if err == nil || !strings.Contains(err.Error(), "error adding security group rule: authorize error") {
			t.Errorf("Expected error 'error adding security group rule: authorize error', got '%v'", err)
		}
	})
}
