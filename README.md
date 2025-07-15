# Offline Docker + Django Criminology Deployment <!-- omit in toc -->

This guide helps you install Docker, Docker Compose, and deploy the Django Criminology project **offline**, using PostgreSQL, Redis, and Nginx.

---

### Table of Contents <!-- omit in toc -->

- [What You Need to Download](#what-you-need-to-download)
- [Step 1: Get Docker and Docker Images (Online Machine)](#step-1-get-docker-and-docker-images-online-machine)
    - [Get Docker Images From Docker Hub](#get-docker-images-from-docker-hub)
- [Step 2: Install Docker (Offline Machine)](#step-2-install-docker-offline-machine)
- [Step 3: Load and Run Docker Images (Offline Machine)](#step-3-load-and-run-docker-images-offline-machine)
- [Once the Site is Up](#once-the-site-is-up)
- [Tips \& Reminders](#tips--reminders)
- [Issues](#issues)

---

## What You Need to Download

- A Zip Folder [Here](https://www.dropbox.com/scl/fo/legp2fqohajm9zddepunb/AGwZugGR4jYU4sdlA-YD3fw?rlkey=i8u71368cmasbbh6xsdy2j8e8&st=k457hz50&dl=0), Which Matches Your UbuntuOS: `Ubuntu18.04.zip`, `Ubuntu20.04.zip`, `Ubuntu22.04.zip`, `Ubuntu24.04.zip`<br/>
  Contains Docker Engine and Docker Compose `.deb` packages for Ubuntu **18.04 through 24.04** Respectively, including:

  - `docker-ce_<version>.deb`
  - `docker-ce-cli_<version>.deb`
  - `containerd.io_<version>.deb`
  - `docker-compose-plugin_<version>.deb`
    <br/>

- A [Zip Folder](https://example.broken): `start-up.zip`<br/>
  Contains items to run `docker compose` including

  - `docker-compose.yaml`
  - `.env.example`
  - `nginx/conf.d/default.conf`

---

## Step 1: Get Docker and Docker Images (Online Machine)

### Download Zip Files If you Haven't Yet <!-- omit in toc -->

You Can Skip to [Get Docker Images](#get-docker-images-from-docker-hub) if You Have

#### Get the Required files to Run Docker <!-- omit in toc -->

From this [link](https://www.dropbox.com/scl/fo/legp2fqohajm9zddepunb/AGwZugGR4jYU4sdlA-YD3fw?rlkey=i8u71368cmasbbh6xsdy2j8e8&st=k457hz50&dl=0):
<small>Note that only the Ubuntu 18-24.04 versions are in the folder</small>

1. **Download `Ubuntu<YourVersion>.04.zip`.**

#### Get the Required Files to Run Using `docker compose` <!-- omit in toc -->

From DropBox if you haven't already:

1. **[Download](https://example.broken) `start-up.zip`.**

#### Get Docker Images From Docker Hub

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

## Step 2: Install Docker (Offline Machine)

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

## Step 3: Load and Run Docker Images (Offline Machine)

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

4. **Copy `.env.example` and edit** the following:

   1. Copy using:
      ```bash
      cp .env.example .env.prod
      ```
   2. Edit using `nano`:

      ```bash
      nano .env.prod
      ```

      then replace the following:

      ```bash
      # 🔐 REQUIRED: Generate with `docker run --rm steyaertc23/criminology generate_secret_key`
      SECRET_KEY=REPLACE_ME

      # 🌐 REQUIRED: Use your domain name or server's IP address (no trailing slashes)
      ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

      # ⚠️ Required: must include http:// and/or https://
      CSRF_TRUSTED_ORIGINS=https://yourdomain.com,http://www.yourdomain.com

      # ⏱ Optional: Automatically sets up periodic tasks (like user expiration cleanup)
      RUN_PERIODIC_SETUP=true

      # ... Redis Configuration ...
      # ... DATABASE_ENGINE,DATABASE_NAME,DATABASE_USER ...

      # ⚠️ Don’t use weak passwords — these credentials are used by both Django and Postgres and are critical to security.
      DATABASE_PASSWORD=REPLACE_WITH_STRONG_PASSWORD

      # ... DATABASE_HOST,DATABASE_Port; POSTGRES_DB,POSTGRES_USER ...

      # ⚠️ Don’t use weak passwords — these credentials are used by both Django and Postgres and are critical to security.
      DATABASE_PASSWORD=REPLACE_WITH_STRONG_PASSWORD
      ```

   You don't have to change the `RUN_PERIODIC_SETUP` if you don't want to.
   **Save the File** as **_`.env.prod`_**

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

Do the same for any teacher. The students' accounts can be made on the site once the staff account is made, or via the super user account.

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

Having Issues? [Add an issue on GitHub.](https://github.com/Steyaertc23/criminology/issues)
