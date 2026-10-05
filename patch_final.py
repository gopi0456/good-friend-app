import re

file_path = 'lib/main.dart'
with open(file_path, 'r') as f:
    content = f.read()

# ==========================================
# 1. Patch PublishRidePage (Fix Suggestions)
# ==========================================
publish_pattern = re.compile(r'class PublishRidePage extends StatefulWidget \{.*?(?=// ================= 6\. MY TRIPS)', re.DOTALL)
publish_new = """class PublishRidePage extends StatefulWidget {
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
      child: ListView(shrinkWrap: true, children: list.map((s) => ListTile(dense: true, title: Text(s, style: const TextStyle(fontSize: 14)), onTap: () => onTap(s))).toList()),
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
            TextField(
              controller: _from,
              onChanged: (v) {
                setState(() {
                  _fromSuggestions = v.length > 1 ? popularCities.where((c) => c.toLowerCase().contains(v.toLowerCase())).toList() : [];
                });
              },
              decoration: InputDecoration(labelText: 'From City', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
            ),
            _buildDropdown(_fromSuggestions, (v) { _from.text = v; setState(() => _fromSuggestions = []); }),
            const SizedBox(height: 16),
            TextField(
              controller: _to,
              onChanged: (v) {
                setState(() {
                  _toSuggestions = v.length > 1 ? popularCities.where((c) => c.toLowerCase().contains(v.toLowerCase())).toList() : [];
                });
              },
              decoration: InputDecoration(labelText: 'To City', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
            ),
            _buildDropdown(_toSuggestions, (v) { _to.text = v; setState(() => _toSuggestions = []); }),
            const SizedBox(height: 16),
            TextField(controller: _stops, decoration: InputDecoration(labelText: 'Stops / Via Towns (comma separated)', hintText: 'e.g. Thane, Lonavala', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
            const SizedBox(height: 16),
            TextField(
              controller: _car,
              onChanged: (v) {
                setState(() {
                  _carSuggestions = v.length > 1 ? popularCars.where((c) => c.toLowerCase().contains(v.toLowerCase())).toList() : [];
                });
              },
              decoration: InputDecoration(labelText: 'Car Model', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
            ),
            _buildDropdown(_carSuggestions, (v) { _car.text = v; setState(() => _carSuggestions = []); }),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(child: InkWell(onTap: () async { final date = await showDatePicker(context: context, initialDate: _selectedDate, firstDate: DateTime.now(), lastDate: DateTime.now().add(const Duration(days: 365))); if (date != null) setState(() => _selectedDate = date); }, child: InputDecorator(decoration: InputDecoration(labelText: 'Date', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))), child: Text('${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}')))),
                const SizedBox(width: 10),
                Expanded(child: InkWell(onTap: () async { final time = await showTimePicker(context: context, initialTime: _selectedTime); if (time != null) setState(() => _selectedTime = time); }, child: InputDecorator(decoration: InputDecoration(labelText: 'Time', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))), child: Text(_selectedTime.format(context)))),
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
}

"""
content = publish_pattern.sub(publish_new, content)

# ==========================================
# 2. Patch MyTripsPage (Fix Refresh Issue)
# ==========================================
trips_pattern = re.compile(r'class MyTripsPage extends StatefulWidget \{.*?(?=// ================= 7\. MESSAGES PAGE)', re.DOTALL)
trips_new = """class MyTripsPage extends StatefulWidget {
  const MyTripsPage({super.key});
  @override
  State<MyTripsPage> createState() => _MyTripsPageState();
}

class _MyTripsPageState extends State<MyTripsPage> {
  List<Map<String, dynamic>> _myRides = [];
  List<Map<String, dynamic>> _myBookings = [];
  List<Map<String, dynamic>> _relatedRides = [];
  bool _isLoading = true;

  @override
  void initState() { super.initState(); _loadData(); }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final u = supabase.auth.currentUser;
    try {
      if (u != null) {
        _myRides = await supabase.from('rides').select().eq('driver_id', u.id);
        final bookingsData = await supabase.from('bookings').select().eq('passenger_id', u.id);
        _myBookings = List<Map<String, dynamic>>.from(bookingsData);
        final rideIds = _myBookings.map((b) => b['ride_id'] as String).toList();
        if (rideIds.isNotEmpty) {
          final ridesData = await supabase.from('rides').select().inFilter('id', rideIds);
          _relatedRides = List<Map<String, dynamic>>.from(ridesData);
        } else { _relatedRides = []; }
      }
      if (mounted) setState(() => _isLoading = false);
    } catch (e) { if (mounted) setState(() => _isLoading = false); }
  }

  Future<void> _deleteRide(int index, String rideId) async {
    final confirm = await showDialog<bool>(context: context, builder: (c) => AlertDialog(title: const Text('Delete Ride?'), content: const Text('This cannot be undone.'), actions: [TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('Cancel')), ElevatedButton(onPressed: () => Navigator.pop(c, true), style: ElevatedButton.styleFrom(backgroundColor: Colors.red), child: const Text('Delete'))]));
    if (confirm == true) { 
      await supabase.from('rides').delete().eq('id', rideId); 
      setState(() { _myRides.removeAt(index); }); // Instant local update
    }
  }

  Future<void> _cancelBooking(int index, String bookingId) async {
    final confirm = await showDialog<bool>(context: context, builder: (c) => AlertDialog(title: const Text('Cancel Booking?'), content: const Text('Your seat will be released.'), actions: [TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('No')), ElevatedButton(onPressed: () => Navigator.pop(c, true), style: ElevatedButton.styleFrom(backgroundColor: Colors.orange), child: const Text('Yes, Cancel'))]));
    if (confirm == true) { 
      await supabase.from('bookings').delete().eq('id', bookingId); 
      setState(() { _myBookings.removeAt(index); }); // Instant local update
    }
  }

  Map<String, dynamic>? _getRideForBooking(String rideId) {
    try { return _relatedRides.firstWhere((r) => r['id'] == rideId); } catch (e) { return null; }
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(title: const Text('My Trips'), backgroundColor: const Color(0xFFF59E0B), foregroundColor: Colors.white, leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context)), bottom: const TabBar(tabs: [Tab(text: 'My Offers'), Tab(text: 'My Bookings')])),
        body: _isLoading ? const Center(child: CircularProgressIndicator()) : TabBarView(children: [
          _myRides.isEmpty ? const Center(child: Text('No published rides.')) : ListView.builder(
            padding: const EdgeInsets.all(16), itemCount: _myRides.length,
            itemBuilder: (c, i) {
              final r = _myRides[i];
              return Card(margin: const EdgeInsets.only(bottom: 12), child: ListTile(title: Text('${r['from_city']} → ${r['to_city']}', style: const TextStyle(fontWeight: FontWeight.bold)), subtitle: Text('Seats: ${r['available_seats']}/${r['total_seats']} • ₹${r['price']}'), trailing: Row(mainAxisSize: MainAxisSize.min, children: [IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () => _deleteRide(i, r['id']))])));
            },
          ),
          _myBookings.isEmpty ? const Center(child: Text('No bookings yet.')) : ListView.builder(
            padding: const EdgeInsets.all(16), itemCount: _myBookings.length,
            itemBuilder: (c, i) {
              final b = _myBookings[i];
              final r = _getRideForBooking(b['ride_id']);
              if (r == null) return const SizedBox.shrink();
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  title: Text('${r['from_city']} → ${r['to_city']}', style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text('Driver: ${r['driver_name']} (${r['driver_phone']})'),
                  trailing: IconButton(icon: const Icon(Icons.cancel, color: Colors.orange), onPressed: () => _cancelBooking(i, b['id'])),
                ),
              );
            },
          ),
        ]),
      ),
    );
  }
}

"""
content = trips_pattern.sub(trips_new, content)

# ==========================================
# 3. Patch AdminPanelPage (Two Menu Cards)
# ==========================================
admin_pattern = re.compile(r'class AdminPanelPage extends StatefulWidget \{.*?(?=// ================= 10\. PROFILE)', re.DOTALL)
admin_new = """class AdminPanelPage extends StatefulWidget {
  const AdminPanelPage({super.key});
  @override
  State<AdminPanelPage> createState() => _AdminPanelPageState();
}

class _AdminPanelPageState extends State<AdminPanelPage> {
  List<Map<String, dynamic>> _users = [];
  List<Map<String, dynamic>> _rides = [];
  List<Map<String, dynamic>> _bookings = [];
  List<Map<String, dynamic>> _allRidesForBookings = [];
  String _activeTab = 'users'; // 'users' or 'rides'

  @override
  void initState() { super.initState(); _loadAll(); }

  Future<void> _loadAll() async {
    _users = await supabase.from('profiles').select();
    _rides = await supabase.from('rides').select();
    final bookingsData = await supabase.from('bookings').select();
    _bookings = List<Map<String, dynamic>>.from(bookingsData);
    final rideIds = _bookings.map((b) => b['ride_id'] as String).toList();
    if (rideIds.isNotEmpty) {
      final ridesData = await supabase.from('rides').select().inFilter('id', rideIds);
      _allRidesForBookings = List<Map<String, dynamic>>.from(ridesData);
    }
    setState(() {});
  }

  Map<String, dynamic>? _getRideForBooking(String rideId) {
    try { return _allRidesForBookings.firstWhere((r) => r['id'] == rideId); } catch (e) { return null; }
  }

  Future<void> _editRide(Map<String, dynamic> ride) async {
    final priceCtrl = TextEditingController(text: ride['price'].toString());
    final seatsCtrl = TextEditingController(text: ride['available_seats'].toString());
    final statusCtrl = TextEditingController(text: ride['status'].toString());
    await showDialog(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Admin Edit Ride'),
        content: Column(mainAxisSize: MainAxisSize.min, children: [TextField(controller: priceCtrl, decoration: const InputDecoration(labelText: 'Price')), TextField(controller: seatsCtrl, decoration: const InputDecoration(labelText: 'Seats')), TextField(controller: statusCtrl, decoration: const InputDecoration(labelText: 'Status (open/cancelled)'))]),
        actions: [TextButton(onPressed: () => Navigator.pop(c), child: const Text('Cancel')), ElevatedButton(onPressed: () async { await supabase.from('rides').update({'price': double.tryParse(priceCtrl.text) ?? 0, 'available_seats': int.tryParse(seatsCtrl.text) ?? 1, 'status': statusCtrl.text}).eq('id', ride['id']); Navigator.pop(c); _loadAll(); }, child: const Text('Save'))],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Admin Control'), backgroundColor: Colors.red, foregroundColor: Colors.white, leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context))),
      body: Column(
        children: [
          // Two Menu Cards like Home Page
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.white,
            child: Row(
              children: [
                Expanded(child: _adminMenuCard('Manage Users', Icons.people, const Color(0xFF8B5CF6), _activeTab == 'users')),
                const SizedBox(width: 15),
                Expanded(child: _adminMenuCard('Manage Rides', Icons.directions_car, const Color(0xFFEF4444), _activeTab == 'rides')),
              ],
            ),
          ),
          const Divider(height: 1),
          // Content Area
          Expanded(
            child: _activeTab == 'users' 
              ? ListView.builder(itemCount: _users.length, itemBuilder: (c, i) { 
                  final u = _users[i]; 
                  return ListTile(title: Text(u['full_name']), subtitle: Text(u['email']), trailing: IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () async { 
                    await supabase.from('profiles').delete().eq('id', u['id']); 
                    setState(() { _users.removeAt(i); }); 
                  })); 
                })
              : DefaultTabController(
                  length: 2,
                  child: Column(
                    children: [
                      const TabBar(tabs: [Tab(text: 'Rides'), Tab(text: 'Bookings')]),
                      Expanded(
                        child: TabBarView(children: [
                          ListView.builder(itemCount: _rides.length, itemBuilder: (c, i) { 
                            final r = _rides[i]; 
                            return ListTile(title: Text('${r['from_city']} → ${r['to_city']}'), subtitle: Text('Driver: ${r['driver_name']} • Status: ${r['status']}'), trailing: Row(mainAxisSize: MainAxisSize.min, children: [
                              IconButton(icon: const Icon(Icons.edit, color: Colors.blue), onPressed: () => _editRide(r)), 
                              IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () async { 
                                await supabase.from('rides').delete().eq('id', r['id']); 
                                setState(() { _rides.removeAt(i); }); 
                              })
                            ])); 
                          }),
                          ListView.builder(itemCount: _bookings.length, itemBuilder: (c, i) { 
                            final b = _bookings[i]; 
                            final r = _getRideForBooking(b['ride_id']); 
                            return ListTile(title: Text('${r?['from_city'] ?? 'Unknown'} → ${r?['to_city'] ?? ''}'), subtitle: Text('Passenger: ${b['passenger_name']}'), trailing: IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () async { 
                              await supabase.from('bookings').delete().eq('id', b['id']); 
                              setState(() { _bookings.removeAt(i); }); 
                            })); 
                          }),
                        ]),
                      ),
                    ],
                  ),
                ),
          ),
        ],
      ),
    );
  }

  Widget _adminMenuCard(String title, IconData icon, Color color, bool isActive) {
    return InkWell(
      onTap: () => setState(() => _activeTab = title.contains('Users') ? 'users' : 'rides'),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: isActive ? LinearGradient(colors: [color, color.withOpacity(0.7)]) : null,
          color: isActive ? null : Colors.grey.shade100,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [BoxShadow(color: color.withOpacity(0.3), blurRadius: 8, offset: const Offset(0, 4))],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: isActive ? Colors.white : color, size: 32),
            const SizedBox(height: 8),
            Text(title, textAlign: TextAlign.center, style: TextStyle(color: isActive ? Colors.white : Colors.grey[700], fontSize: 14, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}

"""
content = admin_pattern.sub(admin_new, content)

with open(file_path, 'w') as f:
    f.write(content)

print("SUCCESS: All 3 issues fixed! (Suggestions, Refresh, Admin Menu)")
