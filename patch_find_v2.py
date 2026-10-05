import re

file_path = 'lib/main.dart'
with open(file_path, 'r') as f:
    content = f.read()

# Find the FindRidePage class and replace it
# We look for the class start and stop right before "5. PUBLISH RIDE"
pattern = re.compile(r'class FindRidePage extends StatefulWidget \{.*?(?=// ================= 5\. PUBLISH RIDE)', re.DOTALL)

fixed_class = """class FindRidePage extends StatefulWidget {
  const FindRidePage({super.key});
  @override
  State<FindRidePage> createState() => _FindRidePageState();
}

class _FindRidePageState extends State<FindRidePage> {
  final _fromCtrl = TextEditingController();
  final _toCtrl = TextEditingController();
  List<String> _fromSuggestions = [];
  List<String> _toSuggestions = [];
  
  // We load rides once into memory for instant searching
  List<Map<String, dynamic>> _allRides = []; 
  List<Map<String, dynamic>> _results = [];
  bool _isLoading = false;
  bool _hasSearched = false;

  @override
  void initState() {
    super.initState();
    _loadInitialRides();
  }

  // Load recent future rides once (Fast!)
  Future<void> _loadInitialRides() async {
    setState(() => _isLoading = true);
    try {
      // Fetch only open rides with seats, happening in the future, limit 50 for speed
      final data = await supabase
          .from('rides')
          .select()
          .eq('status', 'open')
          .gt('available_seats', 0)
          .gte('date_time', DateTime.now().toIso8601String())
          .order('date_time', ascending: true)
          .limit(50);
      
      if (mounted) {
        setState(() { 
          _allRides = List<Map<String, dynamic>>.from(data); 
          _results = _allRides; // Show all initially
          _isLoading = false; 
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _updateSuggestions(String query, bool isFrom) {
    if (query.length < 2) {
      setState(() { if (isFrom) _fromSuggestions = []; else _toSuggestions = []; });
      return;
    }
    final matches = popularCities.where((c) => c.toLowerCase().contains(query.toLowerCase())).toList();
    setState(() { if (isFrom) _fromSuggestions = matches; else _toSuggestions = matches; });
  }

  // Instant Local Search (No Database Delay!)
  void _searchRides() {
    setState(() { _isLoading = true; _hasSearched = true; });
    
    // Simulate a tiny delay for UX so the spinner shows
    Future.delayed(const Duration(milliseconds: 200), () {
      List<Map<String, dynamic>> filtered = _allRides;
      
      String fromQ = _fromCtrl.text.toLowerCase().trim();
      String toQ = _toCtrl.text.toLowerCase().trim();

      if (fromQ.isNotEmpty) {
        filtered = filtered.where((r) => r['from_city'].toString().toLowerCase().contains(fromQ)).toList();
      }
      if (toQ.isNotEmpty) {
        filtered = filtered.where((r) => r['to_city'].toString().toLowerCase().contains(toQ)).toList();
      }

      if (mounted) {
        setState(() { 
          _results = filtered; 
          _isLoading = false; 
        });
      }
    });
  }

  Future<void> _bookRide(Map<String, dynamic> ride) async {
    final user = supabase.auth.currentUser;
    if (user == null) return;
    String pName = user.email ?? 'User';
    String pPhone = '';
    try {
      final prof = await supabase.from('profiles').select('full_name, phone').eq('id', user.id).maybeSingle();
      if (prof != null) { pName = prof['full_name']; pPhone = prof['phone']; }
    } catch (e) {}
    try {
      await supabase.from('bookings').insert({
        'id': 'book_${DateTime.now().millisecondsSinceEpoch}',
        'ride_id': ride['id'],
        'passenger_id': user.id,
        'passenger_name': pName,
        'passenger_phone': pPhone,
        'seats_booked': 1,
        'status': 'confirmed'
      });
      await supabase.from('rides').update({'available_seats': ride['available_seats'] - 1}).eq('id', ride['id']);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('✅ Booked with ${ride['driver_name']}!'), backgroundColor: Colors.green));
        _loadInitialRides(); // Refresh the main list
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red));
    }
  }

  Widget _buildSuggestionDropdown(List<String> suggestions, Function(String) onTap) {
    if (suggestions.isEmpty) return const SizedBox.shrink();
    return Container(
      margin: const EdgeInsets.only(top: 5),
      constraints: const BoxConstraints(maxHeight: 150),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(8), boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 4)]),
      child: ListView(
        shrinkWrap: true,
        children: suggestions.map((s) => ListTile(dense: true, title: Text(s, style: const TextStyle(fontSize: 14)), onTap: () => onTap(s))).toList(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Find a Ride'),
        backgroundColor: const Color(0xFF3B82F6),
        foregroundColor: Colors.white,
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context)),
      ),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.grey.shade50,
            child: Column(
              children: [
                TextField(
                  controller: _fromCtrl,
                  onChanged: (v) => _updateSuggestions(v, true),
                  decoration: InputDecoration(labelText: 'Leaving from', prefixIcon: const Icon(Icons.location_on, color: Colors.green), border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
                ),
                _buildSuggestionDropdown(_fromSuggestions, (v) { _fromCtrl.text = v; setState(() => _fromSuggestions = []); }),
                const SizedBox(height: 10),
                TextField(
                  controller: _toCtrl,
                  onChanged: (v) => _updateSuggestions(v, false),
                  decoration: InputDecoration(labelText: 'Going to', prefixIcon: const Icon(Icons.flag, color: Colors.red), border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
                ),
                _buildSuggestionDropdown(_toSuggestions, (v) { _toCtrl.text = v; setState(() => _toSuggestions = []); }),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _isLoading ? null : _searchRides,
                    icon: _isLoading ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)) : const Icon(Icons.search),
                    label: const Text('Search Rides', style: TextStyle(fontSize: 16)),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF3B82F6),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: _isLoading 
              ? const Center(child: CircularProgressIndicator()) 
              : _results.isEmpty 
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.search_off, size: 60, color: Colors.grey[400]),
                        const SizedBox(height: 10),
                        Text(_hasSearched ? 'No rides found for your search' : 'Enter cities above to find rides', style: TextStyle(color: Colors.grey[600])),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _results.length,
                    itemBuilder: (context, index) => _buildRideCard(_results[index]),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildRideCard(Map<String, dynamic> r) {
    String stops = r['stops'] ?? '';
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12), boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 5)]),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const CircleAvatar(radius: 22, backgroundColor: Color(0xFF3B82F6), child: Icon(Icons.person, color: Colors.white, size: 22)),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(r['driver_name'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                    Text('📞 ${r['driver_phone']}', style: TextStyle(color: Colors.grey[700], fontSize: 12)),
                    Text('🚗 ${r['car_model']}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                  ],
                ),
              ),
              Container(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6), decoration: BoxDecoration(color: Colors.green.shade100, borderRadius: BorderRadius.circular(8)), child: Text('₹${r['price']}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green))),
            ],
          ),
          const Divider(height: 20),
          Row(
            children: [
              Column(children: [Text(r['from_city'], style: const TextStyle(fontWeight: FontWeight.bold)), Text(r['date_time'].toString().substring(11, 16), style: TextStyle(color: Colors.grey[600], fontSize: 12))]),
              Expanded(child: Container(height: 2, color: Colors.grey.shade300, margin: const EdgeInsets.symmetric(horizontal: 10))),
              Column(children: [Text(r['to_city'], style: const TextStyle(fontWeight: FontWeight.bold)), Text('${r['available_seats']} seats', style: TextStyle(color: Colors.orange, fontSize: 12))]),
            ],
          ),
          if (stops.isNotEmpty) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(color: Colors.blue.shade50, borderRadius: BorderRadius.circular(8)),
              child: Row(
                children: [
                  Icon(Icons.location_city, color: Colors.blue.shade700, size: 16),
                  const SizedBox(width: 8),
                  Expanded(child: Text('Stops: $stops', style: TextStyle(color: Colors.blue.shade900, fontSize: 12))),
                ],
              ),
            ),
          ],
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () => _bookRide(r),
              icon: const Icon(Icons.check_circle, size: 18),
              label: const Text('Book Ride'),
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF10B981), foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(vertical: 10), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))),
            ),
          ),
        ],
      ),
    );
  }
}

"""

if pattern.search(content):
    new_content = pattern.sub(fixed_class, content)
    with open(file_path, 'w') as f:
        f.write(new_content)
    print("SUCCESS: FindRidePage patched! Search is now instant and fast.")
else:
    print("ERROR: Could not find the class to replace.")
