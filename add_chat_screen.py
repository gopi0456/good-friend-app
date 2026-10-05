file_path = 'lib/main.dart'

with open(file_path, 'r') as f:
    content = f.read()

chat_screen_code = """
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

"""

marker = "// ================= 8. COMMUNITY"
if marker in content:
    content = content.replace(marker, chat_screen_code + marker)
    with open(file_path, 'w') as f:
        f.write(content)
    print("✅ SUCCESS: ChatScreen class added back!")
else:
    print("❌ ERROR: Could not find the Community marker.")
