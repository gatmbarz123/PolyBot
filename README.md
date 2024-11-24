# PolyBot CI/CD Automation

This repository manages the automation for building, pushing, and deploying the **PolyBot** image. PolyBot is a Telegram bot written in Python that interacts with users. The CI/CD pipeline ensures seamless updates to the bot across all cloud-hosted instances and keeps the system up-to-date with minimal manual intervention.

## Workflow Overview

The automation process consists of two main stages: **Continuous Integration (CI)** and **Continuous Deployment (CD)**. Below is a detailed explanation of how each stage works.

---

## Continuous Integration (CI)

The CI process is focused on:
1. **Building the Docker image for PolyBot.**
2. **Pushing the updated image to Docker Hub.**

### Steps in the CI Process:
1. **Docker Login:**  
   - Logs into Docker Hub using credentials stored as environment variables:
     - `vars.DOCKER_USR`: Docker username.
     - `secrets.DOCKER_PWD`: Docker password.
   - This ensures secure and automated access to Docker Hub.

2. **Docker Build:**  
   - Builds the PolyBot image from the `Dockerfile` in the repository.  
   - This step ensures that any updates to the bot's code are included in the image.

3. **Docker Tag:**  
   - Tags the newly built image with a version or latest identifier, ensuring that the correct image is always pushed and deployed.

4. **Docker Push:**  
   - Pushes the tagged image to Docker Hub.  
   - This makes the updated image available for deployment across the cloud-hosted instances.

### Key Points:
- The CI process runs every time a new change is pushed to the repository.
- It ensures that the latest version of the PolyBot image is always ready for deployment.

---

## Continuous Deployment (CD)

The CD process deploys the updated Docker image to all instances tagged with `PolyBot` in AWS. Additionally, it configures and updates the system environment to ensure the bot functions correctly.

### Steps in the CD Process:
1. **Installing Ansible and Configuring AWS Access:**  
   - Ansible is installed to handle deployment across multiple instances.
   - AWS access is configured using the following environment variables:
     - `AWS_SECRET_ACCESS_KEY`: AWS secret access key.
     - `AWS_ACCESS_KEY_ID`: AWS access key ID.
     - `AWS_REGION`: The AWS region where the instances are hosted.

2. **Generating `inventory.ini`:**  
   - The `inventory.ini` file is a dynamic inventory list required by Ansible.  
   - AWS CLI is used to fetch IP addresses of instances tagged as `PolyBot`:
     - `aws ec2 describe-instances` retrieves the instance information.
   - The IP addresses, along with SSH keys and connection details, are added to `inventory.ini`.  
   - This file allows Ansible to know which machines to target for deployment.

3. **Extracting Configuration Data from AWS:**  
   - Retrieves important environment variables required by PolyBot:
     - `dynamodb`: Database configuration.
     - `s3`: Storage configuration.
     - `sqs_name`: Name of the message queue.
     - `alb_url`: Application Load Balancer URL for the bot.
   - These values are stored securely as environment variables in GitHub Actions.

4. **Running the Ansible Playbook:**  
   - Executes the playbook to:
     - Pull the latest Docker image onto each PolyBot instance.
     - Update environment variables and configurations required by the bot.
     - Restart the bot to ensure it runs with the new image and settings.
   - An SSH private key (`secrets.PRIVATE_KEY`) is used to connect securely to all instances.

---

## Detailed Example of Automation Flow

1. **Triggering the Process:**  
   - A developer pushes changes to the repository.  
   - GitHub Actions trigger the CI pipeline to build and push the new image.  
   - Once the image is available, the CD pipeline begins deployment.

2. **Deploying to AWS Instances:**  
   - The CD pipeline dynamically fetches all instances tagged with `PolyBot`.  
   - Each instance is updated with the new image and its configurations.

3. **Updating PolyBot Instances:**  
   - Ansible ensures that:
     - The correct image is pulled from Docker Hub.
     - The necessary environment variables are applied.
     - The bot is restarted seamlessly.

4. **End Result:**  
   - All PolyBot instances in the cloud are running the latest version with updated settings.

---

## Environment Variables

The automation process uses the following environment variables for security and flexibility:

### Docker:
- `vars.DOCKER_USR`: Docker username.
- `secrets.DOCKER_PWD`: Docker password.

### AWS:
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key.
- `AWS_ACCESS_KEY_ID`: AWS access key ID.
- `AWS_REGION`: The AWS region for the infrastructure.

### SSH:
- `secrets.PRIVATE_KEY`: Private SSH key for accessing instances.


---

## Conclusion

This CI/CD pipeline leverages **GitHub Actions**, **Ansible**, and **AWS** to provide a robust and automated deployment process for PolyBot. By automating the build, push, and deployment processes, the system remains up-to-date, scalable, and efficient, ensuring seamless functionality for all cloud-hosted bots.
