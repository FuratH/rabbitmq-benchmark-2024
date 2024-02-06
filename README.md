# RabbitMQ Benchmark for Cloud Service Benchmark at TU Berlin

This repository contains tools and configurations for benchmarking RabbitMQ as part of the "Cloud Service Benchmark" course at TU Berlin. The project is designed to be deployed on Google Cloud and includes an analysis component, a benchmarking tool, a failure injector module, Terraform setup for infrastructure provisioning, and a load balancer configuration.

## Components

- **Analysis**: Scripts and tools for analyzing benchmark results.
- **Benchmark**: Core benchmarking tool to measure RabbitMQ performance.
- **FailureInjector**: Module for injecting failures to test RabbitMQ resilience.
- **TerraformSetup**: Infrastructure as Code (IaC) setup for provisioning required resources on Google Cloud.
- **LoadBalancer**: Configuration for setting up a load balancer to distribute client requests across RabbitMQ nodes.

## Prerequisites

- Google Cloud account
- Terraform installed on your local machine
- Git (for cloning this repository)

## Installation Guide

### 1. Create Project and Service Account on Google Cloud

1. Log in to your Google Cloud account and create a new project named `csb-2023`.
2. Create a new service account within the `csb-2023` project.
3. Assign the necessary roles to the service account
4. Copy the email adress of the service account

### 2. Configure Terraform

1. Clone the repository to your local machine:
    ```sh
    git clone https://github.com/yourusername/rabbitmq-benchmark-2024.git
    ```
2. Navigate to the `TerraformSetup` directory:
    ```sh
    cd rabbitmq-benchmark-2024/TerraformSetup
    ```
3. Initialize Terraform:
    ```sh
    terraform init
    ```
4. Add the service account to the client VM
    ```sh
      service_account {
        email  = "Add email here!"
        scopes = ["cloud-platform"]
      }
    ```
6. Plan the Terraform deployment to review the resources that will be created:
    ```sh
    terraform plan
    ```
7. Apply the Terraform configuration to provision the infrastructure:
    ```sh
    terraform apply --auto-approve
    ```

### 3. Create Google Cloud Storage Bucket

- Create a bucket named `rabbitmq-benchmark-results` for storing benchmark results.

### 4. Deploy and Run Benchmark

1. After the infrastructure is provisioned, find the IP address of the load balancer in the Google Cloud Console.
2. Log in to the RabbitMQ management portal at `http://loadbalancerip:15672` with username `rabbitmq` and password `password`.
3. Wait until all three nodes are connected.
4. Log in to the client VM provisioned by Terraform.
5. Change directory to the root:
    ```sh
    cd ../..
    ```
6. Run the benchmark tool:
    ```sh
    sudo nohup java -jar rabbitmq-benchmark-2024/Benchmark/target/rabbitmq-benchmark-1.0.0-jar-with-dependencies.jar rabbitmq-benchmark-2024/Benchmark/config.yaml &
    ```

### 5. Cleanup

- To destroy the resources created by Terraform after the benchmarking is complete, run:
    ```sh
    terraform destroy
    ```

## Additional Information

- For detailed analysis of the benchmark results, refer to the `Analysis` directory.
- Custom configurations for the benchmark can be adjusted in the `config.yaml` file located in the `Benchmark` directory.
