import re

file_path = 'lib/main.dart'
with open(file_path, 'r') as f:
    content = f.read()

# 1. Update DriversListPage to use separate drivers table
drivers_pattern = re.compile(r'class DriversListPage extends StatefulWidget \{.*?(?=// ================= NEW: TRAVELS LIST PAGE)', re.DOTALL)
new_drivers = """class DriversListPage extends StatefulWidget {
  const DriversListPage({super.key});
  @override
  State<DriversListPage> createState() => _DriversListPageState();
}

class _DriversListPageState extends State<DriversListPage> {
  List<Map<String, dynamic>> _drivers = [];
  List<Map<String, dynamic>> _filtered = [];
  bool _isLoading = true;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() => _isLoading = true);
    final data = await supabase.from('drivers').select();
    setState(() { _drivers = List<Map<String, dynamic>>.from(data); _filtered = _drivers; _isLoading = false; });
  }

  void _filter(String q) {
    setState(() {
      if (q.isEmpty) { _filtered = _drivers; } 
      else { _filtered = _drivers.where((d) => d['full_name'].toString().toLowerCase().contains(q.toLowerCase())).toList(); }
    });
  }

  Future<void> _registerAsDriver() async {
    final u = supabase.auth.currentUser;
    if (u == null) return;
    
    final nameC = TextEditingController();
    final phoneC = TextEditingController();
    final licC = TextEditingController();
    final expC = TextEditingController(text: '0');
    final carC = TextEditingController();
    
    // Pre-fill with user profile data
    try {
      final p = await supabase.from('profiles').select('full_name, phone').eq('id', u.id).maybeSingle();
      if (p != null) { nameC.text = p['full_name'] ?? ''; phoneC.text = p['phone'] ?? ''; }
    } catch (e) {}
    
    await showDialog(context: context, builder: (c) => AlertDialog(
      title: const Text('Register as Driver'),
      content: SingleChildScrollView(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(controller: nameC, decoration: const InputDecoration(labelText: 'Full Name')),
          TextField(controller: phoneC, decoration: const InputDecoration(labelText: 'Phone')),
          TextField(controller: licC, decoration: const InputDecoration(labelText: 'License Number')),
          TextField(controller: expC, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Experience (Years)')),
          TextField(controller: carC, decoration: const InputDecoration(labelText: 'Car Model')),
        ]),
      ),
      actions: [TextButton(onPressed: () => Navigator.pop(c), child: const Text('Cancel')), ElevatedButton(onPressed: () async {
        await supabase.from('drivers').insert({
          'id': 'drv_${DateTime.now().millisecondsSinceEpoch}',
          'user_id': u.id,
          'full_name': nameC.text,
          'phone': phoneC.text,
          'license_number': licC.text,
          'experience_years': int.tryParse(expC.text) ?? 0,
          'car_model': carC.text,
        });
        Navigator.pop(c); _load();
      }, child: const Text('Register'))],
    ));
  }

  Future<void> _editDriver(Map<String, dynamic> d) async {
    final nameC = TextEditingController(text: d['full_name']);
    final phoneC = TextEditingController(text: d['phone']);
    final licC = TextEditingController(text: d['license_number'] ?? '');
    final expC = TextEditingController(text: (d['experience_years'] ?? 0).toString());
    final carC = TextEditingController(text: d['car_model'] ?? '');
    
    await showDialog(context: context, builder: (c) => AlertDialog(
      title: const Text('Edit Driver'),
      content: SingleChildScrollView(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(controller: nameC, decoration: const InputDecoration(labelText: 'Name')),
          TextField(controller: phoneC, decoration: const InputDecoration(labelText: 'Phone')),
          TextField(controller: licC, decoration: const InputDecoration(labelText: 'License')),
          TextField(controller: expC, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Experience (Years)')),
          TextField(controller: carC, decoration: const InputDecoration(labelText: 'Car Model')),
        ]),
      ),
      actions: [TextButton(onPressed: () => Navigator.pop(c), child: const Text('Cancel')), ElevatedButton(onPressed: () async {
        await supabase.from('drivers').update({'full_name': nameC.text, 'phone': phoneC.text, 'license_number': licC.text, 'experience_years': int.tryParse(expC.text) ?? 0, 'car_model': carC.text}).eq('id', d['id']);
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
      floatingActionButton: FloatingActionButton(onPressed: _registerAsDriver, backgroundColor: const Color(0xFF8B5CF6), child: const Icon(Icons.add, color: Colors.white)),
      body: Column(children: [
        Padding(padding: const EdgeInsets.all(16), child: TextField(onChanged: _filter, decoration: InputDecoration(hintText: 'Search drivers...', prefixIcon: const Icon(Icons.search), border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))))),
        Expanded(child: _isLoading ? const Center(child: CircularProgressIndicator()) : _drivers.isEmpty ? const Center(child: Text('No drivers registered yet. Tap + to register!')) : ListView.builder(
          padding: const EdgeInsets.all(16), itemCount: _filtered.length,
          itemBuilder: (c, i) {
            final d = _filtered[i];
            final isMe = u?.id == d['user_id'];
            return Container(margin: const EdgeInsets.only(bottom: 12), padding: const EdgeInsets.all(16), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12), boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05))]),
            child: Row(children: [
              CircleAvatar(radius: 30, backgroundColor: const Color(0xFF8B5CF6).withOpacity(0.1), child: Text(d['full_name'][0].toUpperCase(), style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF8B5CF6)))),
              const SizedBox(width: 16),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(d['full_name'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                Text('📞 ${d['phone']}', style: TextStyle(color: Colors.grey[700], fontSize: 12)),
                Text(' License: ${d['license_number'] ?? 'N/A'}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                Text('⭐ ${d['experience_years'] ?? 0} Years Exp', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                Text('🚗 ${d['car_model'] ?? 'N/A'}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              ])),
              Column(children: [
                if (isMe || isAdmin) IconButton(icon: const Icon(Icons.edit, color: Colors.blue, size: 20), onPressed: () => _editDriver(d)),
                if (isMe || isAdmin) IconButton(icon: const Icon(Icons.delete, color: Colors.red, size: 20), onPressed: () async { await supabase.from('drivers').delete().eq('id', d['id']); _load(); }),
                IconButton(icon: const Icon(Icons.message, color: Colors.green, size: 20), onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ChatScreen(rideId: 'direct_${d['user_id']}', otherUserId: d['user_id'], otherUserName: d['full_name'], myId: u!.id)))),
              ]),
            ]));
          },
        )),
      ]),
    );
  }
}

"""
content = drivers_pattern.sub(new_drivers, content)

# 2. Update TravelsListPage to use separate travels table
travels_pattern = re.compile(r'class TravelsListPage extends StatefulWidget \{.*?(?=// ================= 4\. FIND RIDE)', re.DOTALL)
new_travels = """class TravelsListPage extends StatefulWidget {
  const TravelsListPage({super.key});
  @override
  State<TravelsListPage> createState() => _TravelsListPageState();
}

class _TravelsListPageState extends State<TravelsListPage> {
  List<Map<String, dynamic>> _travels = [];
  List<Map<String, dynamic>> _filtered = [];
  bool _isLoading = true;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() => _isLoading = true);
    final data = await supabase.from('travels').select();
    setState(() { _travels = List<Map<String, dynamic>>.from(data); _filtered = _travels; _isLoading = false; });
  }

  void _filter(String q) {
    setState(() {
      if (q.isEmpty) { _filtered = _travels; } 
      else { _filtered = _travels.where((t) => t['travel_name'].toString().toLowerCase().contains(q.toLowerCase()) || t['from_city'].toString().toLowerCase().contains(q.toLowerCase()) || t['to_city'].toString().toLowerCase().contains(q.toLowerCase())).toList(); }
    });
  }

  Future<void> _addTravel() async {
    final u = supabase.auth.currentUser;
    if (u == null) return;
    
    final nameC = TextEditingController();
    final fromC = TextEditingController();
    final toC = TextEditingController();
    final priceC = TextEditingController();
    final seatsC = TextEditingController(text: '1');
    final carC = TextEditingController();
    final phoneC = TextEditingController();
    
    await showDialog(context: context, builder: (c) => AlertDialog(
      title: const Text('Add Travel'),
      content: SingleChildScrollView(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(controller: nameC, decoration: const InputDecoration(labelText: 'Travel Name')),
          TextField(controller: fromC, decoration: const InputDecoration(labelText: 'From City')),
          TextField(controller: toC, decoration: const InputDecoration(labelText: 'To City')),
          TextField(controller: priceC, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Price (₹)')),
          TextField(controller: seatsC, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Seats')),
          TextField(controller: carC, decoration: const InputDecoration(labelText: 'Car Model')),
          TextField(controller: phoneC, decoration: const InputDecoration(labelText: 'Contact Phone')),
        ]),
      ),
      actions: [TextButton(onPressed: () => Navigator.pop(c), child: const Text('Cancel')), ElevatedButton(onPressed: () async {
        await supabase.from('travels').insert({
          'id': 'trv_${DateTime.now().millisecondsSinceEpoch}',
          'user_id': u.id,
          'travel_name': nameC.text,
          'from_city': fromC.text,
          'to_city': toC.text,
          'date_time': DateTime.now().toIso8601String(),
          'price': double.tryParse(priceC.text) ?? 0,
          'seats': int.tryParse(seatsC.text) ?? 1,
          'car_model': carC.text,
          'contact_phone': phoneC.text,
        });
        Navigator.pop(c); _load();
      }, child: const Text('Add'))],
    ));
  }

  @override
  Widget build(BuildContext context) {
    final u = supabase.auth.currentUser;
    final isAdmin = u?.email == adminEmail;
    return Scaffold(
      appBar: AppBar(title: const Text('Travels'), backgroundColor: const Color(0xFFF59E0B), foregroundColor: Colors.white, leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context))),
      floatingActionButton: FloatingActionButton(onPressed: _addTravel, backgroundColor: const Color(0xFFF59E0B), child: const Icon(Icons.add, color: Colors.white)),
      body: Column(children: [
        Padding(padding: const EdgeInsets.all(16), child: TextField(onChanged: _filter, decoration: InputDecoration(hintText: 'Search travel name or city...', prefixIcon: const Icon(Icons.search), border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))))),
        Expanded(child: _isLoading ? const Center(child: CircularProgressIndicator()) : _travels.isEmpty ? const Center(child: Text('No travels added yet. Tap + to add!')) : ListView.builder(
          padding: const EdgeInsets.all(16), itemCount: _filtered.length,
          itemBuilder: (c, i) {
            final t = _filtered[i];
            final isMe = u?.id == t['user_id'];
            return Container(margin: const EdgeInsets.only(bottom: 12), padding: const EdgeInsets.all(16), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12), boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05))]),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [
                const Icon(Icons.directions_car, color: Color(0xFFF59E0B)), const SizedBox(width: 10),
                Expanded(child: Text(t['travel_name'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16))),
                Text('₹${t['price']}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green)),
              ]),
              const SizedBox(height: 8),
              Text('${t['from_city']} → ${t['to_city']}', style: TextStyle(color: Colors.grey[700])),
              Text('Car: ${t['car_model']} • Seats: ${t['seats']}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              Text('📞 ${t['contact_phone']}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              const SizedBox(height: 12),
              Row(mainAxisAlignment: MainAxisAlignment.end, children: [
                if (isMe || isAdmin) IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () async { await supabase.from('travels').delete().eq('id', t['id']); _load(); }),
                IconButton(icon: const Icon(Icons.message, color: Colors.green), onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ChatScreen(rideId: 'trv_${t['user_id']}', otherUserId: t['user_id'], otherUserName: t['travel_name'], myId: u!.id)))),
              ]),
            ]));
          },
        )),
      ]),
    );
  }
}

"""
content = travels_pattern.sub(new_travels, content)

# 3. Optimize FindRidePage to load faster
find_pattern = re.compile(r'Future<void> _loadInitialRides\(\) async \{.*?\}', re.DOTALL)
optimized_load = """Future<void> _loadInitialRides() async {
    setState(() => _isLoading = true);
    try {
      final data = await supabase
          .from('rides')
          .select()
          .eq('status', 'open')
          .gt('available_seats', 0)
          .order('date_time', ascending: true)
          .limit(30);
      
      if (mounted) {
        setState(() { 
          _allRides = List<Map<String, dynamic>>.from(data); 
          _results = _allRides;
          _isLoading = false; 
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }"""
content = find_pattern.sub(optimized_load, content)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ SUCCESS: Created separate Drivers & Travels lists with registration!")
