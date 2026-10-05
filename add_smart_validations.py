import re

file_path = 'lib/main.dart'

with open(file_path, 'r') as f:
    content = f.read()

# 1. Auth Screen (Registration) - Mobile Validation
auth_val = """
        if (!RegExp(r'^[0-9]{10}$').hasMatch(_phone.text.replaceAll(RegExp(r'[^0-9]'), ''))) { 
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit mobile number'))); 
          return; 
        }
"""
content = re.sub(r"(\s*)(await supabase\.from\('profiles'\)\.insert\(\{)", r"\n" + auth_val + r"\2", content, count=1)

# 2. Drivers List - Mobile & License Validation
drv_val = """
        if (!RegExp(r'^[0-9]{10}$').hasMatch(phoneC.text.replaceAll(RegExp(r'[^0-9]'), ''))) { 
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit mobile number'))); 
          return; 
        }
        if (licC.text.length < 10 || !RegExp(r'^[a-zA-Z0-9\s-]+$').hasMatch(licC.text)) { 
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid License Number (min 10 chars, alphanumeric)'))); 
          return; 
        }
"""
content = re.sub(r"(\s*)(await supabase\.from\('drivers'\)\.insert\(\{)", r"\n" + drv_val + r"\2", content, count=1)

# 3. Travels List - Mobile Validation
trv_val = """
        if (!RegExp(r'^[0-9]{10}$').hasMatch(phoneC.text.replaceAll(RegExp(r'[^0-9]'), ''))) { 
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit contact number'))); 
          return; 
        }
"""
content = re.sub(r"(\s*)(await supabase\.from\('travels'\)\.insert\(\{)", r"\n" + trv_val + r"\2", content, count=1)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ SUCCESS: Smart validations injected successfully!")
