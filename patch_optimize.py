import re

file_path = 'lib/main.dart'
with open(file_path, 'r') as f:
    content = f.read()

# ==========================================
# 1. Patch TravelingMenuPage (Move Admin inside)
# ==========================================
traveling_pattern = re.compile(r'class TravelingMenuPage extends StatelessWidget \{.*?(?=// ================= 4\. FIND RIDE)', re.DOTALL)
traveling_new = """class TravelingMenuPage extends StatelessWidget {
  const TravelingMenuPage({super.key});
  void _nav(BuildContext c, Widget p) => Navigator.push(c, MaterialPageRoute(builder: (_) => p));

  @override
  Widget build(BuildContext context) {
    final isAdmin = supabase.auth.currentUser?.email == adminEmail;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Traveling Services'),
        backgroundColor: const Color(0xFF3B82F6),
        foregroundColor: Colors.white,
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context)),
        actions: [
          if (isAdmin) IconButton(icon: const Icon(Icons.admin_panel_settings), onPressed: () => _nav(context, const AdminPanelPage())),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: GridView.count(
          crossAxisCount: 2,
          crossAxisSpacing: 15,
          mainAxisSpacing: 15,
          children: [
            _gridItem(Icons.search, 'Find a Ride', const Color(0xFF3B82F6), () => _nav(context, const FindRidePage())),
            _gridItem(Icons.add_road, 'Publish Ride', const Color(0xFF10B981), () => _nav(context, const PublishRidePage())),
            _gridItem(Icons.directions_car, 'My Trips', const Color(0xFFF59E0B), () => _nav(context, const MyTripsPage())),
            _gridItem(Icons.message, 'Messages', const Color(0xFF8B5CF6), () => _nav(context, const MessagesPage())),
          ],
        ),
      ),
    );
  }

  Widget _gridItem(IconData i, String t, Color c, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(color: c, borderRadius: BorderRadius.circular(16), boxShadow: [BoxShadow(color: c.withOpacity(0.4), blurRadius: 8, offset: const Offset(0, 4))]),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(i, color: Colors.white, size: 40),
            const SizedBox(height: 10),
            Text(t, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}

"""
content = traveling_pattern.sub(traveling_new, content)

# ==========================================
# 2. Patch AdminPanelPage (Instant Deletes)
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
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(title: const Text('Admin Full Control'), backgroundColor: Colors.red, foregroundColor: Colors.white, leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context)), bottom: const TabBar(tabs: [Tab(text: 'Users'), Tab(text: 'Rides'), Tab(text: 'Bookings')])),
        body: TabBarView(children: [
          ListView.builder(itemCount: _users.length, itemBuilder: (c, i) { 
            final u = _users[i]; 
            return ListTile(title: Text(u['full_name']), subtitle: Text(u['email']), trailing: IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () async { 
              await supabase.from('profiles').delete().eq('id', u['id']); 
              setState(() { _users.removeAt(i); }); // Instant delete without reload
            })); 
          }),
          ListView.builder(itemCount: _rides.length, itemBuilder: (c, i) { 
            final r = _rides[i]; 
            return ListTile(title: Text('${r['from_city']} → ${r['to_city']}'), subtitle: Text('Driver: ${r['driver_name']} • Status: ${r['status']}'), trailing: Row(mainAxisSize: MainAxisSize.min, children: [
              IconButton(icon: const Icon(Icons.edit, color: Colors.blue), onPressed: () => _editRide(r)), 
              IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () async { 
                await supabase.from('rides').delete().eq('id', r['id']); 
                setState(() { _rides.removeAt(i); }); // Instant delete without reload
              })
            ])); 
          }),
          ListView.builder(itemCount: _bookings.length, itemBuilder: (c, i) { 
            final b = _bookings[i]; 
            final r = _getRideForBooking(b['ride_id']); 
            return ListTile(title: Text('${r?['from_city'] ?? 'Unknown'} → ${r?['to_city'] ?? ''}'), subtitle: Text('Passenger: ${b['passenger_name']}'), trailing: IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () async { 
              await supabase.from('bookings').delete().eq('id', b['id']); 
              setState(() { _bookings.removeAt(i); }); // Instant delete without reload
            })); 
          }),
        ]),
      ),
    );
  }
}

"""
content = admin_pattern.sub(admin_new, content)

with open(file_path, 'w') as f:
    f.write(content)

print("SUCCESS: Admin moved to Traveling menu & Deletes are now instant!")
