
How to use the script:

1- Install the new dependency:

    Open your terminal and run the following command:
    pip install -r requirements.txt

2- Get a Telegram Bot Token:

    Open the Telegram app and search for the official account called @BotFather.

    Start a chat with @BotFather and send the /newbot command.

    Follow the instructions to choose a name and a username for your new bot.

    @BotFather will give you a unique HTTP API token. Copy this token.

3- Get your Telegram Channel ID:

    Create a new channel and add your bot to it as an administrator.

    To get the Channel ID, you have a few options:

    Option 1 (Easiest): Change your channel's type to public temporarily and set a public username (e.g., https://t.me/MyAwesomeChannel). The channel ID will be -100 followed by the channel's unique numerical ID (e.g., -1001234567890).

    Option 2: Use a service like https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates after your bot has joined the channel.
    The ID will be a number prefixed with -100. Copy this full number.

4- Set Environment Variables:
    For security, the script uses environment variables. This keeps your token and ID out of the script's code.

    On Linux/macOS:
    export TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"
    export TELEGRAM__Blogs_CHANNEL_ID="YOUR_CHANNEL_ID_HERE"
    (Note: You'll need to do this in the terminal session you plan to run the script in, or add it to your .bashrc or .zshrc file for permanent use.)

    On Windows (Command Prompt):
    set TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"
    set TELEGRAM__Blogs_CHANNEL_ID="YOUR_CHANNEL_ID_HERE"

5- Run the script:

    With environment variables set, you can now run the script:
    python main.py

The script will check all your feeds and send any new posts to your Telegram channel. The last_posts.json file will be updated so you don't receive duplicate notifications on subsequent runs.