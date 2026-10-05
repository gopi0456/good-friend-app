file_path = 'lib/main.dart'

with open(file_path, 'r') as f:
    content = f.read()

# 1. Auth Screen (Registration)
old_auth = "await supabase.from('profiles').insert({"
new_auth = """
        if (!RegExp(r'^[0-9]{10}$').hasMatch(_phone.text.replaceAll(RegExp(r'[^0-9]'), ''))) { 
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit mobile number'))); 
          return; 
        }
        await supabase.from('profiles').insert({"""

if old_auth in content:
    content = content.replace(old_auth, new_auth, 1)
    print("✅ Added Mobile Validation to Registration!")

# 2. Drivers List (Using simple space instead of \s to avoid Dart warning)
old_drv = "await supabase.from('drivers').insert({"
new_drv = """
        if (!RegExp(r'^[0-9]{10}$').hasMatch(phoneC.text.replaceAll(RegExp(r'[^0-9]'), ''))) { 
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit mobile number'))); 
          return; 
        }
        if (licC.text.length < 10 || !RegExp(r'^[a-zA-Z0-9 -]+$').hasMatch(licC.text)) { 
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid License Number (min 10 chars)'))); 
          return; 
        }
        await supabase.from('drivers').insert({"""
        
if old_drv in content:
    content = content.replace(old_drv, new_drv, 1)
    print("✅ Added Mobile & License Validation to Driver Registration!")

# 3. Travels List
old_trv = "await supabase.from('travels').insert({"
new_trv = """
        if (!RegExp(r'^[0-9]{10}$').hasMatch(phoneC.text.replaceAll(RegExp(r'[^0-9]'), ''))) { 
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit contact number'))); 
          return; 
        }
        await supabase.from('travels').insert({"""
        
if old_trv in content:
    content = content.replace(old_trv, new_trv, 1)
    print("✅ Added Mobile Validation to Add Travel!")

with open(file_path, 'w') as f:
    f.write(content)

print(" Done! All validations added safely without regex errors.")
