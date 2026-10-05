import re

file_path = 'lib/main.dart'
with open(file_path, 'r') as f:
    content = f.read()

# Find the AdminPanelPage class and replace it
pattern = re.compile(r'class AdminPanelPage extends StatefulWidget \{.*?(?=// ================= 10\. PROFILE)', re.DOTALL)

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
  
  // Controls which screen is shown: 'main', 'traveling', or 'matrimonial'
  String _adminView = 'main'; 

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
    // If we are in a sub-menu, show the specific admin controls
    if (_adminView == 'traveling') {
      return _buildTravelingAdmin();
    } else if (_adminView == 'matrimonial') {
      return _buildMatrimonialAdmin();
    }

    // MAIN ADMIN HOME (Two big cards like the Home Page)
    return Scaffold(
      appBar: AppBar(
        title: const Text('Admin Dashboard'), 
        backgroundColor: Colors.red, 
        foregroundColor: Colors.white, 
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context))
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text('Select Service to Manage', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 40),
            Row(
              children: [
                Expanded(child: _adminHomeCard('Traveling Admin', 'Manage rides, users & bookings', Icons.directions_car, const Color(0xFF3B82F6), () => setState(() => _adminView = 'traveling'))),
                const SizedBox(width: 20),
                Expanded(child: _adminHomeCard('Matrimonial Admin', 'Manage profiles & matches', Icons.favorite, const Color(0xFFEC4899), () => setState(() => _adminView = 'matrimonial'))),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // Widget for the Main Admin Home Cards
  Widget _adminHomeCard(String title, String subtitle, IconData icon, Color color, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        height: 180,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: LinearGradient(colors: [color, color.withOpacity(0.7)]),
          borderRadius: BorderRadius.circular(20),
          boxShadow: [BoxShadow(color: color.withOpacity(0.4), blurRadius: 10, offset: const Offset(0, 5))],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Icon(icon, color: Colors.white, size: 40),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
                Text(subtitle, style: TextStyle(color: Colors.white.withOpacity(0.9), fontSize: 12)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // ==========================================
  // TRAVELING ADMIN CONTROLS
  // ==========================================
  Widget _buildTravelingAdmin() {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Traveling Admin'), 
          backgroundColor: const Color(0xFF3B82F6), 
          foregroundColor: Colors.white, 
          leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => setState(() => _adminView = 'main')), // Back to Admin Home
          bottom: const TabBar(tabs: [Tab(text: 'Users'), Tab(text: 'Rides'), Tab(text: 'Bookings')]),
        ),
        body: TabBarView(children: [
          ListView.builder(itemCount: _users.length, itemBuilder: (c, i) { 
            final u = _users[i]; 
            return ListTile(title: Text(u['full_name']), subtitle: Text(u['email']), trailing: IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () async { 
              await supabase.from('profiles').delete().eq('id', u['id']); 
              setState(() { _users.removeAt(i); }); 
            })); 
          }),
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
    );
  }

  // ==========================================
  // MATRIMONIAL ADMIN CONTROLS
  // ==========================================
  Widget _buildMatrimonialAdmin() {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Matrimonial Admin'), 
          backgroundColor: const Color(0xFFEC4899), 
          foregroundColor: Colors.white, 
          leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => setState(() => _adminView = 'main')), // Back to Admin Home
          bottom: const TabBar(tabs: [Tab(text: 'Profiles'), Tab(text: 'Requests')]),
        ),
        body: TabBarView(children: [
          // Profiles Tab (Reusing users list for now as placeholder)
          ListView.builder(itemCount: _users.length, itemBuilder: (c, i) { 
            final u = _users[i]; 
            return ListTile(
              leading: CircleAvatar(backgroundColor: const Color(0xFFEC4899).withOpacity(0.2), child: Icon(Icons.person, color: const Color(0xFFEC4899))),
              title: Text(u['full_name']), 
              subtitle: Text(u['email']), 
              trailing: IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () async { 
                await supabase.from('profiles').delete().eq('id', u['id']); 
                setState(() { _users.removeAt(i); }); 
              })
            ); 
          }),
          // Requests Tab (Placeholder)
          const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.favorite_border, size: 60, color: Colors.grey),
                SizedBox(height: 16),
                Text('No matrimonial requests yet.', style: TextStyle(color: Colors.grey, fontSize: 16)),
              ],
            ),
          ),
        ]),
      ),
    );
  }
}

"""

if pattern.search(content):
    new_content = pattern.sub(admin_new, content)
    with open(file_path, 'w') as f:
        f.write(new_content)
    print("SUCCESS: Admin Panel now has Traveling & Matrimonial menus!")
else:
    print("ERROR: Could not find the AdminPanelPage class to replace.")
