file_path = 'lib/main.dart'

with open(file_path, 'r') as f:
    content = f.read()

# Fix the extra parenthesis in the Date picker
old_date = "Text('${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}')))),"
new_date = "Text('${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}')),"

# Fix the extra parenthesis in the Time picker
old_time = "Text(_selectedTime.format(context))))),"
new_time = "Text(_selectedTime.format(context))),"

if old_date in content:
    content = content.replace(old_date, new_date)
    print("✅ Fixed Date picker brackets!")
else:
    print("⚠️ Date picker was already correct or formatted differently.")

if old_time in content:
    content = content.replace(old_time, new_time)
    print("✅ Fixed Time picker brackets!")
else:
    print("️ Time picker was already correct or formatted differently.")

with open(file_path, 'w') as f:
    f.write(content)

print("🎉 Done! Try running your app now.")
