# Setting Up Morse Code Server on Glitch (Free!)

Follow these steps to host your WebSocket server for free on Glitch.com:

## Step 1: Create a Glitch Account

1. Go to https://glitch.com
2. Click "Sign in" in the top right
3. Choose "Sign in with GitHub" (easiest since you already have GitHub)
4. Authorize Glitch to access your GitHub account

## Step 2: Create a New Project

1. Once signed in, click "New Project" button
2. Select "glitch-hello-node" (basic Node.js project)
3. Wait for the project to be created

## Step 3: Upload Your Server Files

You have two options:

### Option A: Manual Upload (Easier)
1. In your Glitch project, you'll see files on the left sidebar
2. Delete the existing `server.js` file (click the three dots → Delete)
3. Click "New File" and create `morse-server.js`
4. Copy the contents from your local `morse-server.js` and paste it in
5. Click on `package.json` and replace its contents with `glitch-package.json`

### Option B: Import from GitHub (Faster)
1. Click "Tools" at the bottom left of the Glitch editor
2. Click "Import and Export"
3. Click "Import from GitHub"
4. Enter: `oryxandcake/chris`
5. Wait for it to import
6. Rename `glitch-package.json` to `package.json`
7. Make sure `morse-server.js` is set as the main file

## Step 4: Configure the Project

1. Make sure `package.json` has this in it:
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

2. Glitch will automatically run `npm install` and start your server

## Step 5: Get Your Server URL

1. Look at the bottom of the Glitch editor
2. You'll see "Show" button with options
3. Your app URL will be something like: `https://YOUR-PROJECT-NAME.glitch.me`
4. For WebSocket, you'll use: `wss://YOUR-PROJECT-NAME.glitch.me` (note the `wss` not `ws`)
5. **Important:** Glitch uses port 443 (default HTTPS/WSS port), not 8080

## Step 6: Update Your HTML File

1. Open `morse-code-trainer copy.html` on your computer
2. Find line 829 that says:
   ```javascript
   const wsUrl = 'ws://localhost:8080';
   ```
3. Change it to:
   ```javascript
   const wsUrl = 'wss://YOUR-PROJECT-NAME.glitch.me';
   ```
   (Replace `YOUR-PROJECT-NAME` with your actual Glitch project name)

## Step 7: Update Your Server for Glitch

Glitch expects your server to listen on the PORT environment variable. Update your `morse-server.js`:

Change this line:
```javascript
const PORT = 8080;
```

To:
```javascript
const PORT = process.env.PORT || 8080;
```

This makes it work both on Glitch (which provides PORT automatically) and locally (uses 8080).

## Step 8: Test It!

1. Push your updated HTML to GitHub (with the new WebSocket URL)
2. Visit your website
3. The "ONLINE USERS" section should now show "ONLINE" in green!
4. Open the page in another tab or share with a friend
5. Try transmitting morse code - you should see each other!

## Troubleshooting

**Server won't start on Glitch:**
- Check the Logs (Tools → Logs)
- Make sure `package.json` is correct
- Verify `morse-server.js` is the main file

**Still showing OFFLINE:**
- Check the browser console (F12) for errors
- Make sure you updated the WebSocket URL correctly
- Verify your Glitch project is running (green status)

**Connection fails:**
- Use `wss://` not `ws://` (secure WebSocket)
- Don't include port 8080 in the URL
- Make sure there are no typos in the project name

## Glitch Free Tier Notes

- Your project stays active as long as it's being used
- If inactive for 5 minutes, it goes to sleep
- First request after sleep takes ~10 seconds to wake up
- This is perfect for your use case - it wakes up when someone visits!
- Completely free, no credit card required

## Your Project Settings

After setup, your configuration will be:
- **Server URL:** `wss://YOUR-PROJECT-NAME.glitch.me`
- **Server runs:** 24/7 (sleeps when inactive, wakes on request)
- **Cost:** $0 (free forever)

Good luck! Once this is set up, anyone visiting your website can use the multiplayer morse code trainer together!
