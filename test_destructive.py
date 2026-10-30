"""
Safe live test for destructive methods.
"""
import asyncio
from pysoroush.account import AsyncClient

results = {"passed": 0, "failed": 0, "skipped": 0}

def log(name, status, detail=""):
    if status == "PASS":
        results["passed"] += 1
        print(f"  [PASS] {name}")
    elif status == "FAIL":
        results["failed"] += 1
        print(f"  [FAIL] {name}  ->  {detail}")
    elif status == "SKIP":
        results["skipped"] += 1
        print(f"  [SKIP] {name}  ({detail})")

async def test(name, coro):
    try:
        result = await coro
        log(name, "PASS")
        return result
    except Exception as e:
        log(name, "FAIL", f"{type(e).__name__}: {str(e)[:150]}")
        return None


async def main():
    print("=" * 62)
    print("  PySoroush - Destructive Methods Test (with cleanup)")
    print("=" * 62)

    session_file = "/storage/emulated/0/pysoroush_sessions/pysoroush_account"
    async with AsyncClient(session_file=session_file) as client:
        if not await client.is_authorized():
            print("[ERROR] Not logged in.")
            return

        print("  [OK] Authorized.\n")

        # ============================================================
        # 1. Create & Delete Channel (immediately)
        # ============================================================
        print("--- 1. Channels ---")
        channel = await test("create_channel", client.create_channel("PySoroush Test Channel", about="Temporary test"))
        if channel:
            # Try to delete immediately while session is fresh
            await test("delete_channel", client.delete_channel(channel))
        else:
            log("delete_channel", "SKIP", "channel creation failed")

        # ============================================================
        # 2. Create & Leave Group
        # ============================================================
        print("\n--- 2. Groups ---")
        me = await client.get_me()
        group = await test("create_group (with self)", client.create_group("PySoroush Test Group", [me.id]))
        if group:
            await test("leave_group", client.leave_chat(group))

        # ============================================================
        # 3. Block & Unblock User
        # ============================================================
        print("\n--- 3. Block/Unblock ---")
        try:
            bot_entity = await client.get_entity(70326421)
            blocked = await test("block_user", client.block_user(bot_entity))
            if blocked:
                await test("unblock_user", client.unblock_user(bot_entity))
        except Exception as e:
            log("block_user", "SKIP", f"cannot resolve test bot: {e}")

        # ============================================================
        # 4. Archive / Unarchive Saved Messages
        # ============================================================
        print("\n--- 4. Archive ---")
        await test("archive_chat", client.archive_chat("me"))
        await test("unarchive_chat", client.unarchive_chat("me"))

        # ============================================================
        # 5. Scheduled Message
        # ============================================================
        print("\n--- 5. Scheduled Message ---")
        from datetime import datetime, timedelta
        schedule_date = datetime.now() + timedelta(hours=1)
        sched_msg = await test("send_scheduled_message",
                                client.send_scheduled_message("me", "Scheduled test", schedule_date))
        if sched_msg and hasattr(sched_msg, 'id'):
            await test("delete_scheduled_message", client.delete_messages("me", [sched_msg.id]))

        # ============================================================
        # 6. Username (no-op)
        # ============================================================
        print("\n--- 6. Username (no-op) ---")
        if me and getattr(me, 'username', None):
            try:
                await client.update_username(me.username)
                log("update_username (no-op)", "PASS")
            except Exception as e:
                if "not different" in str(e).lower():
                    log("update_username (no-op)", "PASS")
                else:
                    log("update_username (no-op)", "FAIL", str(e)[:80])
        else:
            log("update_username", "SKIP", "no username set")

        # ============================================================
        # 7. Edit Folder
        # ============================================================
        print("\n--- 7. Folders ---")
        await test("edit_folder (create)", client.edit_folder(2, "PySoroush Temp Folder"))
        try:
            await client.edit_folder(2, "")
            log("edit_folder (delete)", "PASS")
        except Exception as e:
            log("edit_folder (delete)", "FAIL", str(e)[:80])

        # ============================================================
        # 8. Clear History (skip - dangerous)
        # ============================================================
        print("\n--- 8. Clear History ---")
        log("clear_history", "SKIP", "would wipe Saved Messages - not safe to test")

        # ============================================================
        # 9. Profile Photo (skip - needs file upload)
        # ============================================================
        print("\n--- 9. Profile Photo ---")
        log("set_profile_photo", "SKIP", "needs file upload (WebSocket restriction)")
        log("delete_profile_photos", "SKIP", "needs existing photos to delete")

        print("\n" + "=" * 62)
        print(f"  FINAL: {results['passed']} PASSED | {results['failed']} FAILED | {results['skipped']} SKIPPED")
        print("=" * 62)

        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
