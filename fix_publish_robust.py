file_path = 'lib/main.dart'

with open(file_path, 'r') as f:
    content = f.read()

# We find the stable boundaries of the broken class
start_marker = "class PublishRidePage extends StatefulWidget {"
end_marker = "class MyTripsPage extends StatefulWidget {"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    # The perfectly clean, fully expanded class using GestureDetector to avoid InkWell errors
    clean_class = """class PublishRidePage extends StatefulWidget {
  const PublishRidePage({super.key});
  @override
  State<PublishRidePage> createState() => _PublishRidePageState();
}

class _PublishRidePageState extends State<PublishRidePage> {
  final _from = TextEditingController();
  final _to = TextEditingController();
  final _stops = TextEditingController();
  final _price = TextEditingController();
  final _car = TextEditingController();
  
  List<String> _fromSuggestions = [];
  List<String> _toSuggestions = [];
  List<String> _carSuggestions = [];
  
  int _seats = 1;
  bool _isLoading = false;
  DateTime _selectedDate = DateTime.now().add(const Duration(days: 1));
  TimeOfDay _selectedTime = const TimeOfDay(hour: 8, minute: 0);

  Widget _buildDropdown(List<String> list, Function(String) onTap) {
    if (list.isEmpty) return const SizedBox.shrink();
    return Container(
      margin: const EdgeInsets.only(top: 5),
      constraints: const BoxConstraints(maxHeight: 150),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(8), boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1))]),
      child: ListView(
        shrinkWrap: true,
        children: list.map((s) => ListTile(
          dense: true, 
          title: Text(s, style: const TextStyle(fontSize: 14)), 
          onTap: () => onTap(s)
        )).toList(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Publish Ride'), 
        backgroundColor: const Color(0xFF10B981), 
        foregroundColor: Colors.white, 
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context))
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            TextField(
              controller: _from,
              onChanged: (v) => setState(() => _fromSuggestions = v.length > 1 ? popularCities.where((c) => c.toLowerCase().contains(v.toLowerCase())).toList() : []),
              decoration: InputDecoration(labelText: 'From City', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
            ),
            _buildDropdown(_fromSuggestions, (v) { _from.text = v; setState(() => _fromSuggestions = []); }),
            const SizedBox(height: 16),
            
            TextField(
              controller: _to,
              onChanged: (v) => setState(() => _toSuggestions = v.length > 1 ? popularCities.where((c) => c.toLowerCase().contains(v.toLowerCase())).toList() : []),
              decoration: InputDecoration(labelText: 'To City', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
            ),
            _buildDropdown(_toSuggestions, (v) { _to.text = v; setState(() => _toSuggestions = []); }),
            const SizedBox(height: 16),
            
            TextField(controller: _stops, decoration: InputDecoration(labelText: 'Stops / Via Towns (comma separated)', hintText: 'e.g. Thane, Lonavala', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
            const SizedBox(height: 16),
            
            TextField(
              controller: _car,
              onChanged: (v) => setState(() => _carSuggestions = v.length > 1 ? popularCars.where((c) => c.toLowerCase().contains(v.toLowerCase())).toList() : []),
              decoration: InputDecoration(labelText: 'Car Model', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
            ),
            _buildDropdown(_carSuggestions, (v) { _car.text = v; setState(() => _carSuggestions = []); }),
            const SizedBox(height: 16),
            
            Row(
              children: [
                Expanded(
                  child: GestureDetector(
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
                  child: GestureDetector(
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
            ),
            const SizedBox(height: 16),
            
            TextField(controller: _price, keyboardType: TextInputType.number, decoration: InputDecoration(labelText: 'Price (₹)', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
            const SizedBox(height: 16),
            
            Row(
              mainAxisAlignment: MainAxisAlignment.center, 
              children: [
                IconButton(onPressed: () => setState(() => _seats--), icon: const Icon(Icons.remove)), 
                Text('$_seats Seats', style: const TextStyle(fontSize: 18)), 
                IconButton(onPressed: () => setState(() => _seats++), icon: const Icon(Icons.add))
              ]
            ),
            const SizedBox(height: 32),
            
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : () async {
                  final u = supabase.auth.currentUser;
                  if (u == null) return;
                  setState(() => _isLoading = true);
                  
                  String name = u.email ?? 'User'; 
                  String phone = '';
                  try { 
                    final p = await supabase.from('profiles').select('full_name, phone').eq('id', u.id).maybeSingle(); 
                    if (p != null) { name = p['full_name']; phone = p['phone']; } 
                  } catch (e) {}
                  
                  final departureTime = DateTime(_selectedDate.year, _selectedDate.month, _selectedDate.day, _selectedTime.hour, _selectedTime.minute);
                  
                  await supabase.from('rides').insert({
                    'id': 'r_${DateTime.now().millisecondsSinceEpoch}',
                    'driver_id': u.id, 
                    'driver_name': name, 
                    'driver_phone': phone,
                    'from_city': _from.text, 
                    'to_city': _to.text, 
                    'stops': _stops.text,
                    'date_time': departureTime.toIso8601String(),
                    'price': double.tryParse(_price.text) ?? 0, 
                    'total_seats': _seats, 
                    'available_seats': _seats, 
                    'car_model': _car.text, 
                    'status': 'open'
                  });
                  
                  setState(() => _isLoading = false);
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Ride Published!')));
                  Navigator.pop(context);
                },
                style: ElevatedButton.styleFrom(padding: const EdgeInsets.all(16), backgroundColor: const Color(0xFF10B981)),
                child: _isLoading ? const CircularProgressIndicator(color: Colors.white) : const Text('Publish Ride', style: TextStyle(color: Colors.white, fontSize: 16)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

"""

    # Replace the broken class with the clean one
    new_content = content[:start_idx] + clean_class + content[end_idx:]
    
    with open(file_path, 'w') as f:
        f.write(new_content)
        
    print("✅ SUCCESS: PublishRidePage completely replaced with clean code!")
else:
    print("❌ ERROR: Could not find the class boundaries. Please check your file.")
