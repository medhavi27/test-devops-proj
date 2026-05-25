# Multi-Container Flask App with CI/CD on AWS ECS Fargate

A production-ready demonstration of a containerized Flask application using a **Sidecar Pattern** for PostgreSQL, deployed via an automated **GitHub Actions CI/CD pipeline** to **AWS ECS Fargate**.

## 🏗️ Architecture Overview

This project leverages modern DevOps practices to ensure a highly available and automated deployment.

* **Application:** Flask (Python 3.11) with SQLAlchemy ORM.
* **Database:** PostgreSQL 15 (deployed as a sidecar container).
* **Orchestration:** Amazon ECS (Elastic Container Service) with Fargate (Serverless compute).
* **Networking:** ECS `awsvpc` mode allowing sidecars to communicate via `localhost`.
* **CI/CD:** GitHub Actions for automated testing, Docker image building, and ECS deployment.
* **Security:** IAM Role-based access and Security Groups restricting traffic to Port 5000.

## 🚀 Deployment Pipeline

The CI/CD pipeline defined in `.github/workflows/deploy.yml` automates the following lifecycle:

1. **Continuous Integration (Test):**
* Triggers on every push to the `master` branch.
* Sets up a Python environment and runs unit tests using `unittest`.


2. **Dockerization:**
* Authenticates with **Amazon ECR** (Elastic Container Registry).
* Builds a fresh Docker image tagged with the unique GitHub Commit SHA.
* Pushes the image to a private ECR repository.


3. **Continuous Deployment (ECS):**
* Downloads the current **Task Definition** from AWS.
* Updates the container image URI to the newly built version.
* Registers a new Task Definition revision.
* Updates the **ECS Service** with "Force New Deployment" and waits for service stability (ensuring zero-downtime rolling updates).



## 🛠️ Key Technical Challenges Solved

* **The "Sidecar" Startup Race:** Implemented `depends_on` conditions in the ECS Task Definition to ensure the PostgreSQL container is fully initialized before the Flask app attempts to connect.
* **Task Definition Sanitization:** Resolved `AccessDenied` and `Unexpected Key` errors by refining IAM policies and upgrading GitHub Actions to `v2` to handle modern AWS metadata.
* **Networking via Localhost:** Configured the application to connect to the database via `localhost:5432` rather than a service name, leveraging Fargate's shared network interface for sidecar containers.

## 📁 Repository Structure

```text
.
├── .github/workflows/
│   └── deploy.yml       # Full CI/CD Pipeline
├── app.py               # Flask Application & DB Logic
├── Dockerfile           # Multi-stage Docker build
├── requirements.txt     # Python Dependencies
├── test_app.py          # Unit Tests
└── task-definition.json # ECS Blueprint (Sidecar config)

```

## 📋 Environment Variables

The application expects the following variables (configured as GitHub Secrets or ECS Environment Variables):

* `DATABASE_URL`: `postgresql://admin:secretpass@localhost:5432/restaurant_db`
* `POSTGRES_USER`: `admin`
* `POSTGRES_PASSWORD`: `secretpass`
* `POSTGRES_DB`: `restaurant_db`

## 🚦 Future Improvements

* **Datadog Integration:** Implement the Datadog Agent as a third sidecar container for full-stack observability (Tracing, Logs, and Metrics).
* **Infrastructure as Code (IaC):** Migrate manual AWS console setup to Terraform or AWS CDK.
* **Load Balancing:** Add an Application Load Balancer (ALB) to handle traffic and provide a permanent DNS record.



## 🛠️ Developer Workflow

### 1. Running Locally (Development)

To test changes before pushing to AWS, you can run the stack locally using Docker.

**Prerequisites:**

* Docker and Docker Compose installed.
* An `.env` file with the database credentials.

**Command:**

```bash
# Build and start the containers
docker-compose up --build

```

* **Access the app:** `http://localhost:5000`
* **Access the DB:** `localhost:5432`

---

### 2. Making Code Changes (The CI/CD Flow)

Since we have automated the pipeline, deploying new code is a single-step process.

1. **Modify your code:** Edit `app.py`, CSS, or HTML files.
2. **Commit and Push:**
```bash
git add .
git commit -m "Refactor: Optimized database query logic"
git push origin master

```


3. **Monitor:** Go to the **Actions** tab in GitHub. The pipeline will automatically:
* Run your unit tests.
* Build a new Docker image.
* Update the ECS Service.
* Perform a rolling update (AWS will replace the old container with the new one automatically).



---

### 3. Updating AWS Configurations

If you need to change environment variables (e.g., a new DB password) or hardware specs (CPU/RAM):

1. **Edit Task Definition:** Go to the **ECS Console** -> **Task Definitions** -> **Create New Revision**.
2. **Modify Settings:** Update the environment variables or container limits.
3. **Register:** Click **Create**.
4. **Update Service:**
* Go to your **ECS Service** -> **Update**.
* Select the **latest Revision number** you just created.
* Check **Force new deployment**.
* Click **Update**.
* *Note: If you add new secrets, remember to update them in **GitHub Secrets** as well if the `deploy.yml` relies on them.*



---

### 4. Viewing Logs & Debugging

If the app fails after a deployment:

* **GitHub Side:** Check the "Deploy" step logs in GitHub Actions.
* **AWS Side:** 1. Go to **ECS Cluster** -> **Tasks**.
2. Click the **Stopped** tab to find the failed task.
3. Click the task ID -> **Logs** tab.
4. Toggle between `web-app` and `menu-db` in the dropdown to see specific container errors.

