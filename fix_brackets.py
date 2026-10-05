import re

file_path = 'lib/main.dart'
with open(file_path, 'r') as f:
    content = f.read()

# Find the broken minified Row containing the Date and Time pickers
broken_row_pattern = re.compile(r'Row\(children: \[Expanded\(child: InkWell\(onTap: \(\) async \{ final date =.*?Text\(_selectedTime\.format\(context\)\)\)\)\),', re.DOTALL)

# The correctly formatted Row with perfectly matched brackets
fixed_row = """Row(
              children: [
                Expanded(
                  child: InkWell(
                    onTap: () async {
                      final date = await showDatePicker(context: context, initialDate: _selectedDate, firstDate: DateTime.now(), lastDate: DateTime.now().add(const Duration(days: 365)));
                      if (date != null) setState(() => _selectedDate = date);
                    },
                    child: InputDecorator(
                      decoration: InputDecoration(labelText: 'Date', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
                      child: Text('${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}'),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: InkWell(
                    onTap: () async {
                      final time = await showTimePicker(context: context, initialTime: _selectedTime);
                      if (time != null) setState(() => _selectedTime = time);
                    },
                    child: InputDecorator(
                      decoration: InputDecoration(labelText: 'Time', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
                      child: Text(_selectedTime.format(context)),
                    ),
                  ),
                ),
              ],
            ),"""

if broken_row_pattern.search(content):
    new_content = broken_row_pattern.sub(fixed_row, content)
    with open(file_path, 'w') as f:
        f.write(new_content)
    print("✅ SUCCESS: Fixed the parenthesis error in PublishRidePage!")
else:
    print("❌ ERROR: Could not find the broken Date/Time row. Make sure you are in the right folder.")
