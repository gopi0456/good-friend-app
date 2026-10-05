import re

file_path = 'lib/main.dart'
with open(file_path, 'r') as f:
    content = f.read()

# 1. Update Traveling Menu
menu_pattern = re.compile(r'class TravelingMenuPage extends StatelessWidget \{.*?(?=// ================= 4\. FIND RIDE)', re.DOTALL)
new_menu = """class TravelingMenuPage extends StatelessWidget {
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
        actions: [if (isAdmin) IconButton(icon: const Icon(Icons.admin_panel_settings), onPressed: () => _nav(context, const AdminPanelPage()))],
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
            _gridItem(Icons.people, 'Drivers', const Color(0xFF8B5CF6), () => _nav(context, const DriversListPage())),
            _gridItem(Icons.directions_car, 'Travels', const Color(0xFFF59E0B), () => _nav(context, const TravelsListPage())),
            _gridItem(Icons.message, 'Messages', const Color(0xFFEC4899), () => _nav(context, const MessagesPage())),
            _gridItem(Icons.person, 'My Trips', const Color(0xFF6366F1), () => _nav(context, const MyTripsPage())),
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
          children: [Icon(i, color: Colors.white, size: 40), const SizedBox(height: 10), Text(t, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold))],
        ),
      ),
    );
  }
}

// ================= NEW: DRIVERS LIST PAGE =================
class DriversListPage extends StatefulWidget {
  const DriversListPage({super.key});
  @override
  State<DriversListPage> createState() => _DriversListPageState();
}

class _DriversListPageState extends State<DriversListPage> {
  List<Map<String, dynamic>> _drivers = [];
  List<Map<String, dynamic>> _filtered = [];
  String _search = '';
  bool _isLoading = true;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() => _isLoading = true);
    final data = await supabase.from('profiles').select();
    setState(() { _drivers = List<Map<String, dynamic>>.from(data); _filtered = _drivers; _isLoading = false; });
  }

  void _filter(String q) {
    setState(() {
      _search = q;
      if (q.isEmpty) { _filtered = _drivers; } 
      else { _filtered = _drivers.where((d) => d['full_name'].toString().toLowerCase().contains(q.toLowerCase())).toList(); }
    });
  }

  Future<void> _editDriver(Map<String, dynamic> d) async {
    final nameC = TextEditingController(text: d['full_name']);
    final phoneC = TextEditingController(text: d['phone']);
    final licC = TextEditingController(text: d['license_number'] ?? '');
    final expC = TextEditingController(text: (d['experience_years'] ?? 0).toString());
    
    await showDialog(context: context, builder: (c) => AlertDialog(
      title: const Text('Edit Driver'),
      content: Column(mainAxisSize: MainAxisSize.min, children: [
        TextField(controller: nameC, decoration: const InputDecoration(labelText: 'Name')),
        TextField(controller: phoneC, decoration: const InputDecoration(labelText: 'Phone')),
        TextField(controller: licC, decoration: const InputDecoration(labelText: 'License')),
        TextField(controller: expC, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Experience (Years)')),
      ]),
      actions: [TextButton(onPressed: () => Navigator.pop(c), child: const Text('Cancel')), ElevatedButton(onPressed: () async {
        await supabase.from('profiles').update({'full_name': nameC.text, 'phone': phoneC.text, 'license_number': licC.text, 'experience_years': int.tryParse(expC.text) ?? 0}).eq('id', d['id']);
        Navigator.pop(c); _load();
      }, child: const Text('Save'))],
    ));
  }

  @override
  Widget build(BuildContext context) {
    final u = supabase.auth.currentUser;
    final isAdmin = u?.email == adminEmail;
    return Scaffold(
      appBar: AppBar(title: const Text('Drivers'), backgroundColor: const Color(0xFF8B5CF6), foregroundColor: Colors.white, leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context))),
      body: Column(children: [
        Padding(padding: const EdgeInsets.all(16), child: TextField(onChanged: _filter, decoration: InputDecoration(hintText: 'Search drivers...', prefixIcon: const Icon(Icons.search), border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))))),
        Expanded(child: _isLoading ? const Center(child: CircularProgressIndicator()) : ListView.builder(
          padding: const EdgeInsets.all(16), itemCount: _filtered.length,
          itemBuilder: (c, i) {
            final d = _filtered[i];
            final isMe = u?.id == d['id'];
            return Container(margin: const EdgeInsets.only(bottom: 12), padding: const EdgeInsets.all(16), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12), boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05))]),
            child: Row(children: [
              CircleAvatar(radius: 30, backgroundColor: const Color(0xFF8B5CF6).withOpacity(0.1), child: Text(d['full_name'][0].toUpperCase(), style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF8B5CF6)))),
              const SizedBox(width: 16),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(d['full_name'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                Text('📞 ${d['phone']}', style: TextStyle(color: Colors.grey[700], fontSize: 12)),
                Text(' License: ${d['license_number'] ?? 'N/A'}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                Text('⭐ ${d['experience_years'] ?? 0} Years Exp', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              ])),
              Column(children: [
                if (isMe || isAdmin) IconButton(icon: const Icon(Icons.edit, color: Colors.blue, size: 20), onPressed: () => _editDriver(d)),
                if (isMe || isAdmin) IconButton(icon: const Icon(Icons.delete, color: Colors.red, size: 20), onPressed: () async { await supabase.from('profiles').delete().eq('id', d['id']); _load(); }),
                IconButton(icon: const Icon(Icons.message, color: Colors.green, size: 20), onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ChatScreen(rideId: 'direct_${d['id']}', otherUserId: d['id'], otherUserName: d['full_name'], myId: u!.id)))),
              ]),
            ]));
          },
        )),
      ]),
    );
  }
}

// ================= NEW: TRAVELS LIST PAGE =================
class TravelsListPage extends StatefulWidget {
  const TravelsListPage({super.key});
  @override
  State<TravelsListPage> createState() => _TravelsListPageState();
}

class _TravelsListPageState extends State<TravelsListPage> {
  List<Map<String, dynamic>> _rides = [];
  List<Map<String, dynamic>> _filtered = [];
  String _search = '';
  bool _isLoading = true;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() => _isLoading = true);
    final data = await supabase.from('rides').select().eq('status', 'open');
    setState(() { _rides = List<Map<String, dynamic>>.from(data); _filtered = _rides; _isLoading = false; });
  }

  void _filter(String q) {
    setState(() {
      _search = q;
      if (q.isEmpty) { _filtered = _rides; } 
      else { _filtered = _rides.where((r) => r['from_city'].toString().toLowerCase().contains(q.toLowerCase()) || r['to_city'].toString().toLowerCase().contains(q.toLowerCase()) || r['driver_name'].toString().toLowerCase().contains(q.toLowerCase())).toList(); }
    });
  }

  @override
  Widget build(BuildContext context) {
    final u = supabase.auth.currentUser;
    final isAdmin = u?.email == adminEmail;
    return Scaffold(
      appBar: AppBar(title: const Text('Travels'), backgroundColor: const Color(0xFFF59E0B), foregroundColor: Colors.white, leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context))),
      body: Column(children: [
        Padding(padding: const EdgeInsets.all(16), child: TextField(onChanged: _filter, decoration: InputDecoration(hintText: 'Search city or driver...', prefixIcon: const Icon(Icons.search), border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))))),
        Expanded(child: _isLoading ? const Center(child: CircularProgressIndicator()) : ListView.builder(
          padding: const EdgeInsets.all(16), itemCount: _filtered.length,
          itemBuilder: (c, i) {
            final r = _filtered[i];
            final isMe = u?.id == r['driver_id'];
            return Container(margin: const EdgeInsets.only(bottom: 12), padding: const EdgeInsets.all(16), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12), boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05))]),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [
                const Icon(Icons.directions_car, color: Color(0xFFF59E0B)), const SizedBox(width: 10),
                Expanded(child: Text('${r['from_city']} → ${r['to_city']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16))),
                Text('₹${r['price']}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green)),
              ]),
              const SizedBox(height: 8),
              Text('Driver: ${r['driver_name']} • Car: ${r['car_model']}', style: TextStyle(color: Colors.grey[700])),
              Text('Date: ${r['date_time'].toString().substring(0, 16)}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              const SizedBox(height: 12),
              Row(mainAxisAlignment: MainAxisAlignment.end, children: [
                if (isMe || isAdmin) IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () async { await supabase.from('rides').delete().eq('id', r['id']); _load(); }),
                IconButton(icon: const Icon(Icons.message, color: Colors.green), onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ChatScreen(rideId: r['id'], otherUserId: r['driver_id'], otherUserName: r['driver_name'], myId: u!.id)))),
              ]),
            ]));
          },
        )),
      ]),
    );
  }
}

"""
content = menu_pattern.sub(new_menu, content)

# 2. Update Messages Page to show list of users to chat with
msg_pattern = re.compile(r'class MessagesPage extends StatefulWidget \{.*?(?=// ================= 8\. COMMUNITY)', re.DOTALL)
new_msg = """class MessagesPage extends StatefulWidget {
  const MessagesPage({super.key});
  @override
  State<MessagesPage> createState() => _MessagesPageState();
}

class _MessagesPageState extends State<MessagesPage> {
  List<Map<String, dynamic>> _users = [];
  bool _isLoading = true;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() => _isLoading = true);
    final data = await supabase.from('profiles').select();
    setState(() { _users = List<Map<String, dynamic>>.from(data); _isLoading = false; });
  }

  @override
  Widget build(BuildContext context) {
    final u = supabase.auth.currentUser;
    return Scaffold(
      appBar: AppBar(title: const Text('Messages'), backgroundColor: const Color(0xFFEC4899), foregroundColor: Colors.white, leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context))),
      body: _isLoading ? const Center(child: CircularProgressIndicator()) : ListView.builder(
        itemCount: _users.length,
        itemBuilder: (c, i) {
          final d = _users[i];
          if (d['id'] == u?.id) return const SizedBox.shrink(); // Don't show self
          return ListTile(
            leading: CircleAvatar(child: Text(d['full_name'][0].toUpperCase())),
            title: Text(d['full_name']),
            subtitle: Text('Tap to start chatting'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ChatScreen(rideId: 'direct_${d['id']}', otherUserId: d['id'], otherUserName: d['full_name'], myId: u!.id))),
          );
        },
      ),
    );
  }
}

"""
content = msg_pattern.sub(new_msg, content)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ SUCCESS: Added Drivers, Travels lists with Search & Permissions!")
