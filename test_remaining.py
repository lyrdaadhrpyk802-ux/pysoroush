import asyncio
from pysoroush.account import AsyncClient

async def main():
    print("=" * 62)
    print("  PySoroush - Final Remaining Tests")
    print("=" * 62)

    session_file = "/storage/emulated/0/pysoroush_sessions/pysoroush_account"
    async with AsyncClient(session_file=session_file) as client:
        if not await client.is_authorized():
            print("[ERROR] Not logged in.")
            return
        print("  [OK] Authorized.\n")
        me = await client.get_me()

        # ============================================================
        # 1. TEST: clear_history (Safe on a temporary group)
        # ============================================================
        print("--- 1. Clear History (Safe Test) ---")
        try:
            print("      Creating temporary group...")
            group = await client.create_group("PySoroush ClearTest", [me.id])
            print("      Sending a message to group...")
            msg = await client.send_message(group, "This message will be deleted.")
            await asyncio.sleep(1) # Let server catch up
            
            print("      Clearing history...")
            await client.clear_history(group, revoke=True)
            print("  [PASS] clear_history")
            
            print("      Leaving group...")
            await client.leave_chat(group)
            print("  [PASS] leave_group")
        except Exception as e:
            print(f"  [FAIL] clear_history -> {e}")

        # ============================================================
        # 2. TEST: delete_channel (With wait time)
        # ============================================================
        print("\n--- 2. Delete Channel ---")
        try:
            print("      Creating temporary channel...")
            channel = await client.create_channel("PySoroush DeleteTest", about="To be deleted")
            print(f"      Channel created with ID: {channel.id}")
            print("      Waiting 3 seconds for server to sync entity...")
            await asyncio.sleep(3) 
            
            print("      Deleting channel...")
            await client.delete_channel(channel)
            print("  [PASS] delete_channel")
        except Exception as e:
            print(f"  [FAIL] delete_channel -> {e}")

        # ============================================================
        # 3. TEST: catch_up
        # ============================================================
        print("\n--- 3. Catch Up (Sync missed updates) ---")
        try:
            print("      Calling catch_up()...")
            await client.catch_up()
            print("  [PASS] catch_up")
        except Exception as e:
            print(f"  [FAIL] catch_up -> {e}")

        print("\n" + "=" * 62)
        print("  Done.")
        print("=" * 62)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
