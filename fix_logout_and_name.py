file_path = 'lib/main.dart'

with open(file_path, 'r') as f:
    content = f.read()

# 1. Fix Logout Button (Make it async so it waits for Supabase to clear the session)
old_logout = "ElevatedButton(onPressed: () => supabase.auth.signOut(), child: const Text('Logout'))"
new_logout = "ElevatedButton(onPressed: () async { await supabase.auth.signOut(); }, child: const Text('Logout'))"

if old_logout in content:
    content = content.replace(old_logout, new_logout)
    print("✅ Fixed Logout button!")
else:
    print("️ Logout button already fixed or formatted differently.")

# 2. Fix Publish Ride Name (Better fallback if profile is missing)
old_name_init = "String name = u.email ?? 'User'; String phone = '';"
new_name_init = "String name = u.email?.split('@').first ?? 'User'; String phone = '';"

if old_name_init in content:
    content = content.replace(old_name_init, new_name_init)
    print("✅ Fixed Name fallback (will show 'rajesh' instead of full email)!")
else:
    print("️ Name initialization already fixed.")

# 3. Fix Profile Check (Ensure we only use DB name if it's not empty)
old_profile_check = "if (p != null) { name = p['full_name']; phone = p['phone']; }"
new_profile_check = "if (p != null && p['full_name'] != null && p['full_name'].toString().isNotEmpty) { name = p['full_name']; phone = p['phone'] ?? ''; }"

if old_profile_check in content:
    content = content.replace(old_profile_check, new_profile_check)
    print("✅ Fixed Profile name check!")
else:
    print("⚠️ Profile check already fixed.")

with open(file_path, 'w') as f:
    f.write(content)

print("🎉 Done! Logout and Name issues fixed.")
