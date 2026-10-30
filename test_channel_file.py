import asyncio
from pysoroush.account import AsyncClient

async def main():
    print("=== Testing File Upload to a Channel ===")
    session_file = "/storage/emulated/0/pysoroush_sessions/pysoroush_account"
    
    async with AsyncClient(session_file=session_file) as client:
        if not await client.is_authorized():
            print("Not authorized.")
            return

        # Create a tiny valid JPEG file
        import base64
        with open("/storage/emulated/0/test_channel_img.jpg", "wb") as f:
            f.write(base64.b64decode('/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA='))

        # Get a channel from your dialogs to send to
        dialogs = await client.get_dialogs(limit=10)
        target_channel = None
        for d in dialogs:
            if d.is_channel and d.id != 69741326: # Don't send to Saved Messages
                target_channel = d
                break
        
        if not target_channel:
            print("No channel found to test. Sending to Saved Messages.")
            target = "me"
        else:
            print(f"Targeting channel: {target_channel.name} (ID: {target_channel.id})")
            target = target_channel.id

        print("Sending photo...")
        try:
            await client.send_photo(target, "/storage/emulated/0/test_channel_img.jpg", caption="Test Photo")
            print(">>> SUCCESS: File sent to channel successfully! <<<")
        except Exception as e:
            print(f">>> FAILED: {e} <<<")

if __name__ == "__main__":
    asyncio.run(main())
