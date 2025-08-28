# Project Plan: Alibaba Cloud Security Group Whitelist Automation

**Project Goal:** Create a Go program to automatically whitelist the machine's public IP in an Alibaba Cloud security group for port 443, and register it as a startup service on Windows using PowerShell.

## Detailed Plan:

1.  **Go Project Initialization:**
    *   Initialize a new Go module within the `sg-whitelist-automation` directory.
    *   Create a `main.go` file to house the application logic.

1.1. **Configuration Handling:**
    *   The program will prioritize configuration values in the following order:
        1.  **Command-line flags:** Values provided directly when executing the program (e.g., `--access-key-id "your_id"`).
        2.  **Environment variables:** System-wide environment variables (e.g., `ALIBABA_CLOUD_ACCESS_KEY_ID`).
        3.  **`.env` file:** A `.env` file located in the same directory as the executable.

2.  **Obtain Public IP Address:**
    *   The Go program will use an external service (e.g., `icanhazip.com`, `ipify.org`) to reliably fetch the machine's current public IP address. This will involve making an HTTP GET request and parsing the response.

3.  **Alibaba Cloud API Interaction:**
    *   **Authentication:** The program will authenticate with Alibaba Cloud using Access Key ID and Access Key Secret. These credentials will be retrieved as described in "1.1. Configuration Handling".
    *   **SDK Usage:** Utilize the official Alibaba Cloud Go SDK for ECS (Elastic Compute Service) to interact with security groups.
    *   **Security Group Identification:** The program will need to know which security group to modify. This ID will be retrieved as described in "1.1. Configuration Handling".
    *   **Check Existing Rules:** Before adding a new rule, the program will list the ingress rules for the specified security group. It will check if a rule already exists that allows access from the current public IP to port 443.
    *   **Add Rule (if needed):** If no such rule exists, the program will add a new security group rule allowing TCP access on port 443 from the obtained public IP address. The rule description can be set to indicate it's an automated entry.

4.  **PowerShell Script for Startup:**
    *   A PowerShell script will be created to register the compiled Go executable as a scheduled task or a service that runs automatically on system startup.
    *   **Scheduled Task (Recommended):** This is generally simpler for user-level applications. The script will create a scheduled task that executes the Go program with appropriate permissions.
    *   **Service (More Complex):** Registering as a Windows Service provides more robust background execution but requires more setup (e.g., using `nssm` or similar tools, or writing more complex PowerShell to manage service creation). For this task, a scheduled task is likely sufficient.
    *   The PowerShell script will need to know the path to the compiled Go executable.



### END Result
The Go program `sg-whitelist-automation.exe` and the PowerShell script `install-service.ps1` have been created in the `sg-whitelist-automation` directory.

__To use the solution:__

1.  **Build the Go Program:**
    Open PowerShell, navigate to the `sg-whitelist-automation` directory, and run the `build.ps1` script:
    ```powershell
    cd e:\Projects\PythonProjects\aliyun-ops\sg-whitelist-automation
    .\build.ps1
    ```
    This will compile the Go program and place the `sg-whitelist-automation.exe` executable in the `dist` subdirectory.

2.  **Configure Alibaba Cloud Credentials:** Provide your Alibaba Cloud credentials using one of the following methods (in order of precedence):
    *   **Command-line flags:** When running `sg-whitelist-automation.exe`, provide flags like `--access-key-id "your_id"`, `--access-key-secret "your_secret"`, `--region-id "your_region"`, and `--security-group-id "your_sg_id"`.
    *   **Environment variables:** Set system environment variables: `ALIBABA_CLOUD_ACCESS_KEY_ID`, `ALIBABA_CLOUD_ACCESS_KEY_SECRET`, `ALIBABA_CLOUD_REGION_ID`, `ALIBABA_CLOUD_SECURITY_GROUP_ID`.
    *   **`.env` file (Fallback):** In the `sg-whitelist-automation` directory, create a file named `.env` with your credentials.
        ```
        ALIBABA_CLOUD_ACCESS_KEY_ID="your_access_key_id"
        ALIBABA_CLOUD_ACCESS_KEY_SECRET="your_access_key_secret"
        ALIBABA_CLOUD_REGION_ID="your_region_id"
        ALIBABA_CLOUD_SECURITY_GROUP_ID="your_security_group_id"
        ```

3.  **Run the PowerShell Service Installation Script:**
    Open PowerShell as an **Administrator**, navigate to the `sg-whitelist-automation` directory, and run the `install-service.ps1` script:
    ```powershell
    cd e:\Projects\PythonProjects\aliyun-ops\sg-whitelist-automation
    .\install-service.ps1
    ```
    This script will create a scheduled task named `AliyunSGWhitelist` that runs the `sg-whitelist-automation.exe` program (from the `dist` folder) on system startup. The program's output will be logged to `sg-whitelist-automation.log` in the `sg-whitelist-automation` directory.

__Verification:__ After running the `install-service.ps1` script, you can check the Scheduled Task Scheduler (Taskschd.msc) to confirm the task has been created. Upon the next system restart, the task should execute, and you can check the `sg-whitelist-automation.log` file for its output.
