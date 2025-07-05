# PythonAnywhere Deployment Guide

## Prerequisites
- PythonAnywhere account (Paid account recommended for web apps)
- GitHub repository with your code

## Deployment Steps

1. **Create a new Web App**
   - Log in to PythonAnywhere
   - Go to the "Web" tab and click "Add a new web app"
   - Choose "Manual Configuration" (not "Flask" or "Django")
   - Select Python 3.8 or higher

2. **Set up the virtual environment**
   - In the PythonAnywhere console:
     ```bash
     mkvirtualenv --python=/usr/bin/python3.8 venv
     workon venv
     pip install -r requirements-pa.txt
     ```

3. **Set up environment variables**
   - In the Web tab, go to "Environment variables"
   - Add all necessary environment variables from your `.env` file

4. **Configure WSGI**
   - In the Web tab, click on the WSGI configuration file link
   - Replace the content with:
     ```python
     import os
     import sys
     
     path = '/home/yourusername/youtube_sponsorship_detector'
     if path not in sys.path:
         sys.path.append(path)
     
     from wsgi import app as application
     ```
   - Replace `yourusername` with your PythonAnywhere username

5. **Static files (if any)**
   - In the Web tab, go to "Static files"
   - Add any static file directories if your application has them

6. **Start the application**
   - Go back to the Web tab and click the big green "Reload" button
   - Check the error log if the app doesn't start

## Scheduled Tasks (Optional)
If you need to run periodic tasks:
1. Go to the "Tasks" tab
2. Add a new task with your desired schedule, for example:
   ```
   /home/yourusername/venv/bin/python /home/yourusername/youtube_sponsorship_detector/your_script.py
   ```

## Troubleshooting
- Check the error log in the Web tab
- Make sure all environment variables are set
- Verify that all dependencies are installed in the virtual environment
- Ensure the Python version matches your local environment

## Notes
- The free tier of PythonAnywhere doesn't support webhooks
- Consider upgrading to a paid plan for better performance and features
- Make sure to keep your dependencies updated regularly
