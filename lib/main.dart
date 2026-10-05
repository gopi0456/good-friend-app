import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'config.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Supabase.initialize(url: AppConfig.supabaseUrl, anonKey: AppConfig.supabaseAnonKey);
  runApp(const MyApp());
}

final supabase = Supabase.instance.client;
const String adminEmail = 'gopi.h2703@gmail.com';

const List<String> popularCities = ['Mumbai', 'Pune', 'Delhi', 'Jaipur', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata', 'Ahmedabad', 'Goa', 'Nashik', 'Indore', 'Surat', 'Thane', 'Lonavala'];
const List<String> popularCars = ['Maruti Swift', 'Maruti Dzire', 'Hyundai Creta', 'Tata Nexon', 'Toyota Innova', 'Honda City', 'Kia Seltos', 'Mahindra XUV700'];

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Good Friend Service',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.indigo, useMaterial3: true),
      home: StreamBuilder<AuthState>(
        stream: supabase.auth.onAuthStateChange,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) return const Scaffold(body: Center(child: CircularProgressIndicator()));
          return snapshot.data?.session != null ? const HomePage() : const AuthScreen();
        },
      ),
    );
  }
}

// ================= 1. AUTH SCREEN =================
class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});
  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _email = TextEditingController();
  final _pass = TextEditingController();
  final _name = TextEditingController();
  final _phone = TextEditingController();
  bool _isLogin = true;
  bool _isLoading = false;

  Future<void> _submit() async {
    if (_email.text.isEmpty || _pass.text.length < 6) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter valid email and password')));
      return;
    }
    setState(() => _isLoading = true);
    try {
      if (_isLogin) {
        await supabase.auth.signInWithPassword(email: _email.text.trim(), password: _pass.text.trim());
      } else {
        if (_name.text.isEmpty || _phone.text.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Name and Phone required')));
          return;
        }
        final res = await supabase.auth.signUp(email: _email.text.trim(), password: _pass.text.trim());
        if (res.user != null) {
          
        if (!RegExp(r'^[0-9]{10}$').hasMatch(_phone.text.replaceAll(RegExp(r'[^0-9]'), ''))) { 
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit mobile number'))); 
          return; 
        }
        await supabase.from('profiles').insert({
            'id': res.user!.id,
            'full_name': _name.text,
            'phone': _phone.text,
            'email': _email.text,
            'is_admin': _email.text == adminEmail
          });
        }
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)])),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.directions_car_filled, size: 80, color: Colors.white),
                  const SizedBox(height: 24),
                  const Text('Good Friend Service', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.white)),
                  const SizedBox(height: 40),
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(24)),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        if (!_isLogin) ...[
                          TextField(controller: _name, decoration: InputDecoration(labelText: 'Full Name', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
                          const SizedBox(height: 16),
                          TextField(controller: _phone, keyboardType: TextInputType.number, maxLength: 10, decoration: InputDecoration(labelText: 'Phone Number', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
                          const SizedBox(height: 16),
                        ],
                        TextField(controller: _email, decoration: InputDecoration(labelText: 'Email', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
                        const SizedBox(height: 16),
                        TextField(controller: _pass, obscureText: true, decoration: InputDecoration(labelText: 'Password', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
                        const SizedBox(height: 24),
                        ElevatedButton(
                          onPressed: _isLoading ? null : _submit,
                          style: ElevatedButton.styleFrom(padding: const EdgeInsets.all(16), backgroundColor: const Color(0xFF6366F1), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
                          child: _isLoading ? const CircularProgressIndicator(color: Colors.white) : Text(_isLogin ? 'Login' : 'Register', style: const TextStyle(color: Colors.white, fontSize: 16)),
                        ),
                        TextButton(onPressed: () => setState(() => _isLogin = !_isLogin), child: Text(_isLogin ? 'Need an account? Register' : 'Have an account? Login')),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ================= 2. HOME PAGE =================
class HomePage extends StatelessWidget {
  const HomePage({super.key});
  void _nav(BuildContext c, Widget p) => Navigator.push(c, MaterialPageRoute(builder: (_) => p));

  @override
  Widget build(BuildContext context) {
    final user = supabase.auth.currentUser;
    final isAdmin = user?.email == adminEmail;
    return Scaffold(
      appBar: AppBar(
        title: Text('Hello, ${user?.email?.split('@').first ?? 'Friend'}'),
        backgroundColor: const Color(0xFF6366F1),
        foregroundColor: Colors.white,
        actions: [if (isAdmin) IconButton(icon: const Icon(Icons.admin_panel_settings), onPressed: () => _nav(context, const AdminPanelPage()))],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text('Choose a Service', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 40),
            Row(
              children: [
                Expanded(child: _serviceCard(Icons.directions_car, 'Traveling', 'Rides & Carpooling', const Color(0xFF3B82F6), () => _nav(context, const TravelingMenuPage()))),
                const SizedBox(width: 20),
                Expanded(child: _serviceCard(Icons.favorite, 'Matrimonial', 'Find Life Partner', const Color(0xFFEC4899), () {})),
              ],
            ),
            const SizedBox(height: 40),
            _quickAction(Icons.person, 'My Profile', () => _nav(context, const ProfilePage())),
          ],
        ),
      ),
    );
  }

  Widget _serviceCard(IconData i, String t, String s, Color color, VoidCallback onTap) {
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
            Icon(i, color: Colors.white, size: 40),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(t, style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
                Text(s, style: TextStyle(color: Colors.white.withOpacity(0.9))),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _quickAction(IconData i, String t, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12), boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 5)]),
        child: Row(
          children: [
            Icon(i, color: const Color(0xFF6366F1), size: 24),
            const SizedBox(width: 16),
            Text(t, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const Spacer(),
            const Icon(Icons.arrow_forward_ios),
          ],
        ),
      ),
    );
  }
}

// ================= 3. TRAVELING MENU =================
class TravelingMenuPage extends StatelessWidget {
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
        if (!RegExp(r'^[0-9]{10}$').hasMatch(phoneC.text.replaceAll(' ', '').replaceAll('+91', ''))) { ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit mobile number'))); return; }
        if (!RegExp(r'^[a-zA-Z0-9\s-]{10,20}$').hasMatch(licC.text)) { ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid License Number (10-20 alphanumeric chars)'))); return; }
        
        if (!RegExp(r'^[0-9]{10}$').hasMatch(phoneC.text.replaceAll(RegExp(r'[^0-9]'), ''))) { 
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit mobile number'))); 
          return; 
        }
        if (licC.text.length < 10 || !RegExp(r'^[a-zA-Z0-9 -]+$').hasMatch(licC.text)) { 
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid License Number (min 10 chars)'))); 
          return; 
        }
        await supabase.from('drivers').insert({
          'id': 'drv_${DateTime.now().millisecondsSinceEpoch}',
          'user_id': u.id,
          'full_name': nameC.text,
          'phone': phoneC.text,
          'license_number': licC.text,
          'experience_years': int.tryParse(expC.text) ?? 0,
          'car_model': carC.text,
        });
        nameC.clear(); phoneC.clear(); licC.clear(); expC.clear(); carC.clear(); Navigator.pop(c); _load();
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
                Text('🚗 Car: ${d['car_model']?.toString().isNotEmpty == true ? d['car_model'] : 'Not specified'}', style: TextStyle(color: Colors.blue[700], fontSize: 12, fontWeight: FontWeight.bold)),
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

// ================= NEW: TRAVELS LIST PAGE =================
class TravelsListPage extends StatefulWidget {
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
        if (!RegExp(r'^[0-9]{10}$').hasMatch(phoneC.text.replaceAll(' ', '').replaceAll('+91', ''))) { ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit contact number'))); return; }
        
        if (!RegExp(r'^[0-9]{10}$').hasMatch(phoneC.text.replaceAll(RegExp(r'[^0-9]'), ''))) { 
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit contact number'))); 
          return; 
        }
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
        nameC.clear(); fromC.clear(); toC.clear(); priceC.clear(); seatsC.clear(); carC.clear(); phoneC.clear(); Navigator.pop(c); _load();
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
              Text('🚗 Car: ${t['car_model']?.toString().isNotEmpty == true ? t['car_model'] : 'Not specified'} • Seats: ${t['seats']}', style: TextStyle(color: Colors.blue[700], fontSize: 12, fontWeight: FontWeight.bold)),
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

// ================= 4. FIND RIDE (Perfectly Formatted)
class FindRidePage extends StatefulWidget {
  const FindRidePage({super.key});
  @override
  State<FindRidePage> createState() => _FindRidePageState();
}

class _FindRidePageState extends State<FindRidePage> {
  final _fromCtrl = TextEditingController();
  final _toCtrl = TextEditingController();
  List<String> _fromSuggestions = [];
  List<String> _toSuggestions = [];
  
  List<Map<String, dynamic>> _allRides = []; 
  List<Map<String, dynamic>> _results = [];
  bool _isLoading = false;
  bool _hasSearched = false;

  @override
  void initState() {
    super.initState();
    _loadInitialRides();
  }

  Future<void> _loadInitialRides() async {
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
  }

  void _updateSuggestions(String query, bool isFrom) {
    if (query.length < 2) {
      setState(() { if (isFrom) _fromSuggestions = []; else _toSuggestions = []; });
      return;
    }
    final matches = popularCities.where((c) => c.toLowerCase().contains(query.toLowerCase())).toList();
    setState(() { if (isFrom) _fromSuggestions = matches; else _toSuggestions = matches; });
  }

  void _searchRides() {
    setState(() { _isLoading = true; _hasSearched = true; });
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
        _loadInitialRides();
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

class PublishRidePage extends StatefulWidget {
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
                    if (p != null && p['full_name'] != null && p['full_name'].toString().isNotEmpty) { name = p['full_name']; phone = p['phone'] ?? ''; } 
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

class MyTripsPage extends StatefulWidget {
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

// ================= 7. MESSAGES PAGE (Real Chat) =================
class MessagesPage extends StatefulWidget {
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


// Real Chat Screen
class ChatScreen extends StatefulWidget {
  final String rideId;
  final String otherUserId;
  final String otherUserName;
  final String myId;
  const ChatScreen({super.key, required this.rideId, required this.otherUserId, required this.otherUserName, required this.myId});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _msgCtrl = TextEditingController();
  List<Map<String, dynamic>> _messages = [];
  bool _isLoading = true;

  @override
  void initState() { super.initState(); _loadMessages(); }

  Future<void> _loadMessages() async {
    final data = await supabase.from('messages').select().eq('ride_id', widget.rideId).order('created_at', ascending: true);
    if (mounted) setState(() { _messages = List<Map<String, dynamic>>.from(data); _isLoading = false; });
  }

  Future<void> _sendMessage() async {
    if (_msgCtrl.text.isEmpty) return;
    await supabase.from('messages').insert({
      'id': 'msg_${DateTime.now().millisecondsSinceEpoch}',
      'ride_id': widget.rideId,
      'sender_id': widget.myId,
      'receiver_id': widget.otherUserId,
      'message': _msgCtrl.text,
    });
    _msgCtrl.clear();
    _loadMessages();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Chat with ${widget.otherUserName}'), backgroundColor: const Color(0xFF8B5CF6), foregroundColor: Colors.white),
      body: Column(
        children: [
          Expanded(
            child: _isLoading ? const Center(child: CircularProgressIndicator()) : _messages.isEmpty ? const Center(child: Text('No messages yet. Say Hi!')) : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (c, i) {
                final m = _messages[i];
                final isMe = m['sender_id'] == widget.myId;
                return Align(
                  alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: isMe ? const Color(0xFF8B5CF6) : Colors.grey.shade200, borderRadius: BorderRadius.circular(12)),
                    child: Text(m['message'], style: TextStyle(color: isMe ? Colors.white : Colors.black)),
                  ),
                );
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: Colors.white, boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 5)]),
            child: Row(
              children: [
                Expanded(child: TextField(controller: _msgCtrl, decoration: InputDecoration(hintText: 'Type a message...', border: OutlineInputBorder(borderRadius: BorderRadius.circular(20)))),),
                const SizedBox(width: 8),
                IconButton(onPressed: _sendMessage, icon: const Icon(Icons.send, color: Color(0xFF8B5CF6), size: 30)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ================= 8. COMMUNITY =================
class CommunityPage extends StatefulWidget {
  const CommunityPage({super.key});
  @override
  State<CommunityPage> createState() => _CommunityPageState();
}

class _CommunityPageState extends State<CommunityPage> {
  List<Map<String, dynamic>> _users = [];
  @override
  void initState() { super.initState(); _load(); }
  Future<void> _load() async { _users = await supabase.from('profiles').select(); setState(() {}); }

  @override
  Widget build(BuildContext context) {
    final isAdmin = supabase.auth.currentUser?.email == adminEmail;
    return Scaffold(
      appBar: AppBar(title: const Text('Community'), backgroundColor: const Color(0xFF8B5CF6), foregroundColor: Colors.white, leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context))),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _users.length,
        itemBuilder: (c, i) {
          final u = _users[i];
          final initial = u['full_name'].toString().isNotEmpty ? u['full_name'][0].toUpperCase() : 'U';
          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8, offset: const Offset(0, 2))]),
            child: Row(
              children: [
                CircleAvatar(radius: 30, backgroundColor: const Color(0xFF8B5CF6).withOpacity(0.1), child: Text(initial, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF8B5CF6)))),
                const SizedBox(width: 16),
                Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(u['full_name'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)), const SizedBox(height: 4), Text('📞 ${u['phone']}', style: TextStyle(color: Colors.grey[700], fontSize: 13)), Text('📧 ${u['email']}', style: TextStyle(color: Colors.grey[600], fontSize: 12))])),
                if (isAdmin) IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () async { await supabase.from('profiles').delete().eq('id', u['id']); _load(); }),
              ],
            ),
          );
        },
      ),
    );
  }
}

// ================= 9. ADMIN PANEL (Fixed Data Fetching) =================
class AdminPanelPage extends StatefulWidget {
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

// ================= 10. PROFILE =================
class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});
  @override
  Widget build(BuildContext context) { final u = supabase.auth.currentUser; return Scaffold(appBar: AppBar(title: const Text('Profile'), backgroundColor: const Color(0xFF6366F1), foregroundColor: Colors.white, leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context))), body: Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Text(u?.email ?? '', style: const TextStyle(fontSize: 20)), const SizedBox(height: 20), ElevatedButton(onPressed: () async { await supabase.auth.signOut(); }, child: const Text('Logout'))]))); }
}
