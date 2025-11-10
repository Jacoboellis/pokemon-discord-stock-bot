# 🚀 GitHub Upload Guide - Pokemon Discord Bot

## Step-by-Step Instructions to Upload Your Bot to GitHub

### 1. 📋 Prerequisites
- [x] Git installed (installing now...)
- [ ] GitHub account created
- [ ] Your bot code is ready (✅ Done!)

### 2. 🔧 Prepare Your Repository

Once Git is installed, run these commands in your project folder:

```bash
# Initialize Git repository
git init

# Add all files to tracking
git add .

# Create your first commit
git commit -m "Initial commit: Pokemon Discord Stock Bot for NZ"

# Set your Git identity (replace with your info)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. 📱 Create GitHub Repository

1. **Go to GitHub**: https://github.com
2. **Sign up/Login** to your account
3. **Click "New Repository"** (green button)
4. **Repository Settings**:
   - **Name**: `pokemon-discord-stock-bot` (or whatever you prefer)
   - **Description**: `Pokemon card stock monitoring bot for New Zealand stores`
   - **Visibility**: Choose Public or Private
   - **DON'T** initialize with README (we already have one)
5. **Click "Create Repository"**

### 4. 🔗 Connect Local Repository to GitHub

After creating the GitHub repository, you'll see commands like these:

```bash
# Add GitHub as remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/pokemon-discord-stock-bot.git

# Push your code to GitHub
git branch -M main
git push -u origin main
```

### 5. ✅ Verify Upload

1. **Refresh your GitHub repository page**
2. **You should see**:
   - ✅ All your bot files
   - ✅ README.md displaying properly
   - ✅ Directory structure showing

### 6. 🔒 Important: Protect Your Secrets

**BEFORE UPLOADING**: Make sure your `config.py` file is NOT uploaded!

```bash
# Check what's being tracked
git status

# If config.py appears, remove it:
git rm --cached config.py
git commit -m "Remove config.py from tracking"
```

The `.gitignore` file we created should prevent this automatically.

### 7. 🎯 Next Steps After Upload

1. **Clone to new computers**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pokemon-discord-stock-bot.git
   ```

2. **Keep repository updated**:
   ```bash
   git add .
   git commit -m "Add new features"
   git push
   ```

3. **Share with others**: Send them your repository link!

### 8. 📝 Repository Features to Enable

**In your GitHub repository settings**:
- ✅ Enable Issues (for bug reports)
- ✅ Enable Discussions (for community)
- ✅ Add topics: `discord-bot`, `pokemon`, `new-zealand`, `stock-monitoring`
- ✅ Add a description and website link

### 9. 🌟 Make it Professional

**Optional improvements**:
- Add a LICENSE file (MIT is popular)
- Create releases for stable versions
- Add screenshots to README
- Set up GitHub Actions for automated testing

### 🎉 Ready to Upload!

Once Git finishes installing, you're ready to upload your awesome Pokemon Discord bot to GitHub and preserve all your hard work!

**Your bot includes**:
- ✅ Complete Discord bot with slash commands
- ✅ Daily scanning system
- ✅ New Zealand store focus
- ✅ Community reporting features
- ✅ Comprehensive documentation
- ✅ Professional project structure

**Perfect for sharing with the Pokemon community!** 🎯🇳🇿