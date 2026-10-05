import re

file_path = 'lib/main.dart'

fixed_class = """class PublishRidePage extends StatefulWidget {
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

  Widget _buildSuggestionDropdown(List<String> suggestions, Function(String) onTap) {
    if (suggestions.isEmpty) return const SizedBox.shrink();
    return Container(
      margin: const EdgeInsets.only(top: 5),
      constraints: const BoxConstraints(maxHeight: 150),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(8), boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 4)]),
      child: ListView(shrinkWrap: true, children: suggestions.map((s) => ListTile(dense: true, title: Text(s, style: const TextStyle(fontSize: 14)), onTap: () => onTap(s))).toList()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Publish Ride'), backgroundColor: const Color(0xFF10B981), foregroundColor: Colors.white, leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context))),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            TextField(controller: _from, onChanged: (v) { if (v.length > 1) setState(() => _fromSuggestions = popularCities.where((c) => c.toLowerCase().contains(v.toLowerCase())).toList()); else setState(() => _fromSuggestions = []); }, decoration: InputDecoration(labelText: 'From City', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
            _buildSuggestionDropdown(_fromSuggestions, (v) { _from.text = v; setState(() => _fromSuggestions = []); }),
            const SizedBox(height: 16),
            TextField(controller: _to, onChanged: (v) { if (v.length > 1) setState(() => _toSuggestions = popularCities.where((c) => c.toLowerCase().contains(v.toLowerCase())).toList()); else setState(() => _toSuggestions = []); }, decoration: InputDecoration(labelText: 'To City', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
            _buildSuggestionDropdown(_toSuggestions, (v) { _to.text = v; setState(() => _toSuggestions = []); }),
            const SizedBox(height: 16),
            TextField(controller: _stops, decoration: InputDecoration(labelText: 'Stops / Via Towns (comma separated)', hintText: 'e.g. Thane, Lonavala', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
            const SizedBox(height: 16),
            TextField(controller: _car, onChanged: (v) { if (v.length > 1) setState(() => _carSuggestions = popularCars.where((c) => c.toLowerCase().contains(v.toLowerCase())).toList()); else setState(() => _carSuggestions = []); }, decoration: InputDecoration(labelText: 'Car Model', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
            _buildSuggestionDropdown(_carSuggestions, (v) { _car.text = v; setState(() => _carSuggestions = []); }),
            const SizedBox(height: 16),
            Row(
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
            ),
            const SizedBox(height: 16),
            TextField(controller: _price, keyboardType: TextInputType.number, decoration: InputDecoration(labelText: 'Price (₹)', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
            const SizedBox(height: 16),
            Row(mainAxisAlignment: MainAxisAlignment.center, children: [IconButton(onPressed: () => setState(() => _seats--), icon: const Icon(Icons.remove)), Text('$_seats Seats', style: const TextStyle(fontSize: 18)), IconButton(onPressed: () => setState(() => _seats++), icon: const Icon(Icons.add))]),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : () async {
                  final u = supabase.auth.currentUser;
                  if (u == null) return;
                  setState(() => _isLoading = true);
                  String name = u.email ?? 'User'; String phone = '';
                  try { final p = await supabase.from('profiles').select('full_name, phone').eq('id', u.id).maybeSingle(); if (p != null) { name = p['full_name']; phone = p['phone']; } } catch (e) {}
                  final departureTime = DateTime(_selectedDate.year, _selectedDate.month, _selectedDate.day, _selectedTime.hour, _selectedTime.minute);
                  await supabase.from('rides').insert({
                    'id': 'r_${DateTime.now().millisecondsSinceEpoch}',
                    'driver_id': u.id, 'driver_name': name, 'driver_phone': phone,
                    'from_city': _from.text, 'to_city': _to.text, 'stops': _stops.text,
                    'date_time': departureTime.toIso8601String(),
                    'price': double.tryParse(_price.text) ?? 0, 'total_seats': _seats, 'available_seats': _seats, 'car_model': _car.text, 'status': 'open'
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
}"""

with open(file_path, 'r') as f:
    content = f.read()

pattern = re.compile(r'class PublishRidePage extends StatefulWidget \{.*?(?=// ================= 6\. MY TRIPS)', re.DOTALL)

if pattern.search(content):
    new_content = pattern.sub(fixed_class + "\n\n", content)
    with open(file_path, 'w') as f:
        f.write(new_content)
    print("SUCCESS: PublishRidePage patched!")
else:
    print("ERROR: Could not find the class to replace.")
