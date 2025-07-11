# Offline Docker + Django Criminology Deployment  <!-- omit in toc -->

This guide helps you install Docker, Docker Compose, and deploy the Django Criminology project **offline**, using PostgreSQL, Redis, and Nginx.

---
### Table of Contents <!-- omit in toc -->
- [What’s in This Repository](#whats-in-this-repository)
- [Step 1: Get Docker and Docker Images (Online Machine)](#step-1-get-docker-and-docker-images-online-machine)
- [Step 3: Install Docker (Offline Machine)](#step-3-install-docker-offline-machine)
- [Step 4: Load and Run Docker Images (Offline Machine)](#step-4-load-and-run-docker-images-offline-machine)
- [Once the Site is Up](#once-the-site-is-up)
- [Tips \& Reminders](#tips--reminders)
- [Issues](#issues)


---

## What’s in This Repository

- Zip Folders: `Ubuntu18.04.zip`, `Ubuntu20.04.zip`, `Ubuntu22.04.zip`, `Ubuntu24.04.zip`
  Contains Docker Engine and Docker Compose `.deb` packages for Ubuntu **18.04 through 24.04** Respectively, including:

  - `docker-ce_<version>.deb`
  - `docker-ce-cli_<version>.deb`
  - `containerd.io_<version>.deb`
  - `docker-compose-plugin_<version>.deb`

- A zip folder: `start-up.zip`
  Contains items to run `docker compose` including

  - `docker-compose.yaml`
  - a base `.env.prod`
  - `nginx/conf.d/default.conf`
---


## Step 1: Get Docker and Docker Images (Online Machine)

### Download Zip Files <!-- omit in toc -->
#### Get the Required files to Run Docker <!-- omit in toc -->
From the GitHub repository:

1. **Download and`Ubuntu<YourVersion>.04`.**

#### Get the Required Files to Run Using `docker compose` <!-- omit in toc -->

From the GitHub repository:

1. **Download `start-up.zip`.**
#### Get Docker Images From Docker Hub <!-- omit in toc -->
1. **Pull the required images:**
   ```bash
   docker pull postgres:17
   docker pull redis:alpine
   docker pull nginx:alpine
   docker pull steyaertc23/criminology:latest
   ```
2. **Generate Secret Key for .env.prod** (Optional to do on Online machine, Must do before running `docker compose`)
   ```bash
   docker run --rm steyaertc23/criminology generate_secret_key
   ```
   Save this for later
3. **Save them to `.tar` files:**
   ```bash
   docker save postgres:17 > postgres.tar
   docker save redis:alpine > redis.tar
   docker save nginx:alpine > nginx.tar
   docker save steyaertc23/criminology:latest > website.tar
   ```
##### Transfer these `.tar` files to your offline machine (via USB or secure transfer). <!-- omit in toc -->

## Step 3: Install Docker (Offline Machine)

### On the offline machine (Ubuntu 18.04–24.04): <!-- omit in toc -->

1. **Extract the zip** for your Ubuntu version.

2. **Extract the `start-up.zip` file**.

3. **Install Docker and Compose** by running in the folder:

   ```bash
   sudo dpkg -i *.deb
   ```

4. **Start Docker:**
   ```bash
   sudo systemctl enable docker
   sudo systemctl start docker
   ```
5. **Check Docker Installation:**
   ```bash
   docker --version
   docker compose version
   ```
   

## Step 4: Load and Run Docker Images (Offline Machine)

From the transferred `.tar` files:

1. **Run `docker load`:**
   ```bash
   docker load -i postgres.tar
   docker load -i redis.tar
   docker load -i nginx.tar
   docker load -i website.tar
   ```
2. **Run `docker image ls` and check that you loaded your `.tar` files**
   ```bash
   docker image ls
   ```
   It should give something like this:
   ```
   REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
   postgres            17                  image ID Here       X days ago          size here
   ```
3. **If you haven't already**, run:
   ```bash
   docker run --rm steyaertc23/criminology generate_secret_key
   ```

4. **Edit .env.prod**
   ```bash
   SECRET_KEY=GENERATED_SECRET_KEY # Key just generated

   ALLOWED_HOSTS=yourdomainorip.com,www.yourdomainorip.com # Customize to your liking, can be one if you want, no comma necessary
   CSRF_TRUSTED_ORIGINS=http://www.yourdomainorip.com,https://yourdomainorip.com # Include https:// if you can get your own SSL, if not, just remove it and remove the comma as well.

   DATABASE_PASSWORD=YOUR-STRONG-PASSWORD # Must match the POSTGRES_PASSWORD
   POSTGRES_PASSWORD=YOUR-STRONG-PASSWORD # Must match the DATABASE_PASSWORD
   ```

5. **Create Super User for Website**
   ```bash
   docker run --rm -it steyaertc23/criminology createsuperuser
   ```
   Follow the prompts.
6. **Collect Static Files**
   The site won't render the CSS or JS without running this first:
   ```bash
   docker run --rm steyaertc23/criminology collectstatic
   ```
7. **Run Docker Compose**
   ```bash
   docker compose up -d
   ```
## Once the Site is Up

Go to the /admin endpoint on your url and add a staff account under `Users` for yourself. This will be more secure than using the super user for everything.

Do the same for any teacher. The Students can be made on the site once the staff account is made, or via the super user account.

---

## Tips & Reminders

- **View Logs**  
  If you need to debug something or just want to see output from the services:
  ```bash
  docker compose logs -f
  ```
- **Restart the App**
  After editing `.env.prod` or making changes, restart:
  ```bash
  docker compose down
  docker compose up -d
  ```
- **Regenerate a Django Secret Key**
  You can always generate another one with:
  ```bash
  docker run --rm steyaertc23/criminology generate_secret_key
  ```
- **Static Files Not Showing?**
  Make sure Nginx is serving static files properly, and that they were collected during build. If needed, re-run collectstatic inside the image:

  ```bash
  docker run --rm steyaertc23/criminology collectstatic
  ```

- **Make Sure Ports Are Open**
  Confirm that port 80 is open and exposed if you're accessing from another device or network.

- **Docker Cleanup (Optional)**
  Remove unused images and containers to save space:

  ```bash
  docker system prune -a
  ```
---
## Issues

Having Issues? Add an issue on GitHub.- [Offline Docker + Django Criminology Deployment]