file_path = 'lib/main.dart'

with open(file_path, 'r') as f:
    content = f.read()

# 1. Add Mobile Validation to Auth Screen (Registration)
old_auth = "if (_name.text.isEmpty || _phone.text.isEmpty) { ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Name and Phone required'))); return; }"
new_auth = """if (_name.text.isEmpty || _phone.text.isEmpty) { ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Name and Phone required'))); return; }
        if (!RegExp(r'^[0-9]{10}$').hasMatch(_phone.text.replaceAll(' ', '').replaceAll('+91', ''))) { ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit mobile number'))); return; }"""

if old_auth in content:
    content = content.replace(old_auth, new_auth)
    print("✅ Added Mobile Validation to Registration!")
else:
    print("️ Auth screen validation already exists or format changed.")

# 2. Add Mobile & License Validation to Drivers List (Register as Driver)
old_drv = "await supabase.from('drivers').insert({"
new_drv = """if (!RegExp(r'^[0-9]{10}$').hasMatch(phoneC.text.replaceAll(' ', '').replaceAll('+91', ''))) { ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit mobile number'))); return; }
        if (!RegExp(r'^[a-zA-Z0-9\\s-]{10,20}$').hasMatch(licC.text)) { ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid License Number (10-20 alphanumeric chars)'))); return; }
        await supabase.from('drivers').insert({"""

if old_drv in content:
    content = content.replace(old_drv, new_drv)
    print("✅ Added Mobile & License Validation to Driver Registration!")
else:
    print("⚠️ Driver registration validation already exists or format changed.")

# 3. Add Mobile Validation to Travels List (Add Travel)
old_trv = "await supabase.from('travels').insert({"
new_trv = """if (!RegExp(r'^[0-9]{10}$').hasMatch(phoneC.text.replaceAll(' ', '').replaceAll('+91', ''))) { ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit contact number'))); return; }
        await supabase.from('travels').insert({"""

if old_trv in content:
    content = content.replace(old_trv, new_trv)
    print("✅ Added Mobile Validation to Add Travel!")
else:
    print("️ Travel add validation already exists or format changed.")

with open(file_path, 'w') as f:
    f.write(content)

print("🎉 Done! Validations added successfully without changing existing logic.")
