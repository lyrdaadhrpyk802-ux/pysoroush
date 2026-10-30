"""
Simple Account API test for PySoroush.
"""
import asyncio
import warnings
from pysoroush.account import AsyncClient

# Suppress the harmless aiohttp warning at shutdown
warnings.filterwarnings("ignore", category=ResourceWarning)


async def main():
    # Path to the session file (already authenticated)
    session_path = "/storage/emulated/0/pysoroush_sessions/pysoroush_account"

    print("Connecting to Soroush Plus...")
    async with AsyncClient(session_file=session_path) as client:
        
        # 1. Show profile info
        me = await client.get_me()
        print(f"\n[+] Logged in as: {me.first_name} (ID: {me.id})")
        print(f"[+] Username: {me.username or 'None'}")
        print(f"[+] Phone: {me.phone}")

        # 2. Show recent dialogs
        print("\n[+] Your recent chats:")
        dialogs = await client.get_dialogs(limit=5)
        for i, dialog in enumerate(dialogs, 1):
            print(f"    {i}. {dialog.name}")

        # 3. Send a test message to Saved Messages
        print("\n[+] Sending test message to Saved Messages...")
        msg = await client.send_message("me", "Hello from PySoroush! This is a simple test.")
        print(f"[+] Message sent successfully! (ID: {msg.id})")

        print("\nDone!")

    # Give aiohttp a moment to close cleanly
    await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
