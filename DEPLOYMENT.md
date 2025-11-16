# BugHunter Deployment Guide for Render

## Prerequisites
1. GitHub repository with your code
2. Render account (free tier available)
3. Gmail account for email functionality

## Deployment Steps

### 1. Prepare Repository
- Ensure all files are committed to GitHub
- Include these deployment files:
  - `build.sh` - Build script
  - `render.yaml` - Render configuration
  - `requirements.txt` - Python dependencies
  - `runtime.txt` - Python version
  - `.env.example` - Environment variables template

### 2. Create Render Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: bughunter
   - **Environment**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn bughunter_site.wsgi:application`

### 3. Environment Variables
Add these in Render dashboard:

**Required:**
- `SECRET_KEY`: Generate a secure key
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `your-app-name.onrender.com`

**Email (Optional but recommended):**
- `EMAIL_HOST_USER`: Your Gmail address
- `EMAIL_HOST_PASSWORD`: Gmail app password
- `EMAIL_HOST`: `smtp.gmail.com`
- `EMAIL_PORT`: `587`
- `EMAIL_USE_TLS`: `True`

### 4. Database Setup
Render will automatically:
- Create PostgreSQL database
- Set `DATABASE_URL` environment variable
- Run migrations via build script

### 5. Gmail Setup (for email verification)
1. Enable 2-factor authentication on Gmail
2. Generate App Password:
   - Google Account → Security → App passwords
   - Select "Mail" and generate password
3. Use this password in `EMAIL_HOST_PASSWORD`

### 6. Deploy
1. Click "Create Web Service"
2. Wait for build to complete (~5-10 minutes)
3. Your app will be available at: `https://your-app-name.onrender.com`

## Post-Deployment

### Create Superuser (Optional)
```bash
# In Render shell
python manage.py createsuperuser
```

### Test Functionality
1. Visit your deployed site
2. Test user registration with email verification
3. Test code analysis (users need their own Gemini API keys)

## Important Notes

### Free Tier Limitations
- Service spins down after 15 minutes of inactivity
- Cold starts take 30-60 seconds
- 750 hours/month limit

### User API Keys
- Users must provide their own Gemini API keys
- This ensures cost control and API quota management
- Keys are stored securely per user

### File Uploads
- Temporary files are cleaned up automatically
- 50MB upload limit configured
- Files are processed in memory when possible

## Troubleshooting

### Build Fails
- Check `build.sh` has execute permissions
- Verify all dependencies in `requirements.txt`
- Check Python version in `runtime.txt`

### Database Issues
- Ensure migrations run in build script
- Check `DATABASE_URL` is set by Render
- Verify PostgreSQL service is created

### Email Not Working
- Verify Gmail app password is correct
- Check 2FA is enabled on Gmail account
- Ensure `EMAIL_USE_TLS=True`

### Static Files Missing
- Verify `collectstatic` runs in build script
- Check WhiteNoise middleware is configured
- Ensure `STATIC_ROOT` is set correctly

## Monitoring
- Use Render dashboard for logs and metrics
- Monitor database usage and connections
- Track email delivery in Gmail sent folder

## Scaling
- Upgrade to paid plan for:
  - No spin-down
  - Faster cold starts
  - More resources
  - Custom domains