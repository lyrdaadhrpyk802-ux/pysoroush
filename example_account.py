"""
Interactive login and test script for PySoroush Account (Self) API using async with.
"""

import asyncio
from pysoroush.account import AsyncClient
from splusthon.sessions import StringSession
from splusthon.errors import SessionPasswordNeededError

async def main():
    print("=== PySoroush Account Login Test ===")
    
    session = StringSession()
    
    # Using async with ensures the session is closed even if an error occurs
    async with AsyncClient(session_string=session.save()) as client:
        
        if await client.is_authorized():
            print("You are already logged in!")
        else:
            phone = input("Enter your phone number (e.g., 989123456789): ").strip()
            if phone.startswith('+'):
                phone = phone[1:]
                
            print(f"Requesting OTP code for {phone}...")
            
            def code_callback():
                return input("Enter the OTP code you received: ").strip()

            try:
                await client.start(phone=phone, code_callback=code_callback)
                print("Login successful!")
            except SessionPasswordNeededError:
                print("Two-step verification is enabled.")
                password = input("Enter your password: ")
                await client.sign_in(password=password)
                print("Login successful with password!")
            except Exception as e:
                print(f"Login failed: {e}")
                return

        print("\nFetching your profile info...")
        me = await client.get_me()
        print(f"Logged in as: {me.first_name} (Username: {me.username})")

        print("\nFetching your recent chats (Dialogs)...")
        dialogs = await client.get_dialogs(limit=5)
        for dialog in dialogs:
            print(f"- {dialog.name} (ID: {dialog.id})")

        print("\nSending a test message to yourself...")
        try:
            await client.send_message("me", "Hello from PySoroush Account API!")
            print("Message sent successfully!")
        except Exception as e:
            print(f"Failed to send message: {e}")

    print("\nDone.")

if __name__ == "__main__":
    asyncio.run(main())
