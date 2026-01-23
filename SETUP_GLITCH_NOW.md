# Quick Glitch Setup - Do This Now!

## 1. Go to Glitch
👉 **https://glitch.com**

Click "Sign in" → Choose "Sign in with GitHub"

## 2. Create New Project
1. Click **"New Project"**
2. Choose **"glitch-hello-node"**
3. Wait for it to load

## 3. Replace Files

### Delete these files:
- Click on `server.js` → three dots → Delete

### Update `package.json`:
1. Click on `package.json`
2. Delete everything
3. Paste this:

```json
{
  "name": "morse-code-multiplayer",
  "version": "1.0.0",
  "description": "WebSocket server for multiplayer morse code trainer",
  "main": "morse-server.js",
  "scripts": {
    "start": "node morse-server.js"
  },
  "dependencies": {
    "ws": "^8.14.2"
  },
  "engines": {
    "node": "18.x"
  }
}
```

### Create `morse-server.js`:
1. Click **"New File"**
2. Name it `morse-server.js`
3. Copy-paste the entire contents of your local `morse-server.js` file into it

## 4. Get Your Server URL

Look at the top of the page - you'll see your project name (something like `glowing-amazing-cheetah`)

Your WebSocket URL is: `wss://YOUR-PROJECT-NAME.glitch.me`

Example: `wss://glowing-amazing-cheetah.glitch.me`

## 5. Tell Me Your Project Name

Once you've created the project, tell me the project name and I'll update the HTML file for you!

The project name is shown at the top of the Glitch editor.
