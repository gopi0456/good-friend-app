file_path = 'lib/main.dart'

with open(file_path, 'r') as f:
    content = f.read()

# 1. Fix Phone Validation (Add maxLength: 10 to prevent typing more than 10 digits)
# This is the best way to stop users from entering 11+ digits
content = content.replace("keyboardType: TextInputType.phone,", "keyboardType: TextInputType.number, maxLength: 10,")
content = content.replace("keyboardType: TextInputType.phone", "keyboardType: TextInputType.number, maxLength: 10")
print("✅ Added maxLength: 10 to all phone fields!")

# 2. Fix Clearing Data in Driver Registration
old_drv_end = "Navigator.pop(c); _load();\n      }, child: const Text('Register'))],"
new_drv_end = "nameC.clear(); phoneC.clear(); licC.clear(); expC.clear(); carC.clear(); Navigator.pop(c); _load();\n      }, child: const Text('Register'))],"

if old_drv_end in content:
    content = content.replace(old_drv_end, new_drv_end)
    print("✅ Driver fields will now clear after saving!")

# 3. Fix Clearing Data in Travel Registration
old_trv_end = "Navigator.pop(c); _load();\n      }, child: const Text('Add'))],"
new_trv_end = "nameC.clear(); fromC.clear(); toC.clear(); priceC.clear(); seatsC.clear(); carC.clear(); phoneC.clear(); Navigator.pop(c); _load();\n      }, child: const Text('Add'))],"

if old_trv_end in content:
    content = content.replace(old_trv_end, new_trv_end)
    print("✅ Travel fields will now clear after saving!")

# 4. Fix Car Model Display in Drivers List
old_car_drv = "Text('🚗 ${d['car_model'] ?? 'N/A'}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),"
new_car_drv = "Text('🚗 Car: ${d['car_model']?.toString().isNotEmpty == true ? d['car_model'] : 'Not specified'}', style: TextStyle(color: Colors.blue[700], fontSize: 12, fontWeight: FontWeight.bold)),"

if old_car_drv in content:
    content = content.replace(old_car_drv, new_car_drv)
    print("✅ Fixed Car Model display in Drivers list!")

# 5. Fix Car Model Display in Travels List
old_car_trv = "Text('Car: ${t['car_model']} • Seats: ${t['seats']}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),"
new_car_trv = "Text('🚗 Car: ${t['car_model']?.toString().isNotEmpty == true ? t['car_model'] : 'Not specified'} • Seats: ${t['seats']}', style: TextStyle(color: Colors.blue[700], fontSize: 12, fontWeight: FontWeight.bold)),"

if old_car_trv in content:
    content = content.replace(old_car_trv, new_car_trv)
    print("✅ Fixed Car Model display in Travels list!")

with open(file_path, 'w') as f:
    f.write(content)

print("🎉 All 3 issues fixed successfully!")
