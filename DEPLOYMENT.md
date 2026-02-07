# Deploy EduRoom globally

To make your classroom site available on the internet (not just localhost), use one of these options.

---

## Option 1: Render (free tier, recommended)

1. **Push your code to GitHub**  
   Create a repo and push the `Teacher_Student` project (or the whole folder).

2. **Sign up** at [render.com](https://render.com) and log in.

3. **Create a PostgreSQL database**  
   - Dashboard → **New +** → **PostgreSQL**  
   - Name it (e.g. `eduroom-db`), choose free region, **Create**  
   - Open the DB and copy **Internal Database URL** (you’ll use it in the next step).

4. **Create a Web Service**  
   - **New +** → **Web Service**  
   - Connect your GitHub repo and select the repo (and branch).  
   - **Root Directory**: if the app is inside a subfolder (e.g. `Teacher_Student`), set it to `Teacher_Student`. Otherwise leave blank.  
   - **Runtime**: Python 3  
   - **Build Command**:  
     ```bash
     pip install -r requirements.txt
     ```  
   - **Start Command**:  
     ```bash
     gunicorn -w 2 -b 0.0.0.0:$PORT app:app
     ```  
   - **Environment variables** (under **Environment**):  
     - `SECRET_KEY` = any long random string (e.g. generate one at [randomkeygen.com](https://randomkeygen.com))  
     - `DATABASE_URL` = paste the **Internal Database URL** from step 3  

5. Click **Create Web Service**.  
   After the build finishes, Render will give you a URL like `https://your-app-name.onrender.com`. That is your **global** classroom URL.

**Note:** On the free tier the app may sleep after inactivity; the first visit after that can take 30–60 seconds to wake up. File uploads are stored on the server; for production you’d later consider cloud storage (e.g. S3).

---

## Option 2: Railway

1. Sign up at [railway.app](https://railway.app) and install the GitHub integration.

2. **New Project** → **Deploy from GitHub** → select your repo.  
   If the app is in a subfolder, set **Root Directory** to that folder (e.g. `Teacher_Student`).

3. **Variables** (in the service → Variables):  
   - `SECRET_KEY` = a long random string  
   - Leave `DATABASE_URL` unset to use SQLite, or add a Postgres plugin and use the provided `DATABASE_URL`.

4. **Settings** → **Deploy**:  
   - **Build Command**: `pip install -r requirements.txt`  
   - **Start Command**: `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`  
   (Use `PORT` if Railway provides it; otherwise try `gunicorn -w 2 -b 0.0.0.0:5000 app:app`.)

5. Railway will assign a public URL; use **Generate Domain** if needed. That URL is your global deployment.

---

## Option 3: Run with Gunicorn locally (for a VPS or your own server)

On a Linux server or VPS (e.g. Ubuntu on DigitalOcean, AWS, etc.):

```bash
cd /path/to/Teacher_Student
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="your-secret-key"
export PORT=5000
gunicorn -w 2 -b 0.0.0.0:$PORT app:app
```

To expose it to the internet, open port `5000` (or your `PORT`) in the firewall and point a domain or public IP to this server. For a proper production setup you’d add Nginx and HTTPS (e.g. Let’s Encrypt).

---

## Summary

| Step | What to do |
|------|------------|
| 1 | Put the project on **GitHub**. |
| 2 | Choose **Render** or **Railway** and connect the repo. |
| 3 | Set **SECRET_KEY** and (on Render) **DATABASE_URL** to a Postgres URL. |
| 4 | Use **Build**: `pip install -r requirements.txt` and **Start**: `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`. |
| 5 | Use the URL the platform gives you as your **global** classroom site. |

After deployment, share that URL so students and teachers can log in from anywhere.
