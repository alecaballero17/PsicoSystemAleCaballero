import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../services/chatbot_service.dart';
import '../services/cita_pago_service.dart';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';

class ChatbotScreen extends StatefulWidget {
  final String token;
  final ChatbotContextType contextType;
  final int? contextId;
  final String title;

  const ChatbotScreen({
    Key? key,
    required this.token,
    required this.contextType,
    this.contextId,
    required this.title,
  }) : super(key: key);

  @override
  State<ChatbotScreen> createState() => _ChatbotScreenState();
}

class _ChatbotScreenState extends State<ChatbotScreen> {
  final List<Map<String, String>> _messages = [];
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _isLoading = false;

  final _record = AudioRecorder();
  bool _isRecording = false;

  @override
  void dispose() {
    _record.dispose();
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    _messages.add({
      'sender': 'bot',
      'text': '¡Hola! Soy Chatsito. ¿En qué te puedo ayudar hoy?'
    });
  }

  void _sendMessage() async {
    if (_controller.text.trim().isEmpty) return;
    
    final msg = _controller.text;
    setState(() {
      _messages.add({'sender': 'user', 'text': msg});
      _isLoading = true;
    });
    _controller.clear();
    _scrollToBottom();

    final response = await ChatbotService.sendMessage(
      token: widget.token,
      type: widget.contextType,
      mensaje: msg,
      contextId: widget.contextId,
    );

    if (mounted) {
      setState(() {
        _messages.add({'sender': 'bot', 'text': response});
        _isLoading = false;
      });
      _scrollToBottom();
    }
  }

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      final path = await _record.stop();
      setState(() => _isRecording = false);
      if (path != null) {
        setState(() => _isLoading = true);
        try {
          // Reutilizamos el endpoint de transcripción
          final transcript = await CitaPagoService.transcribeAudio(
              token: widget.token, filePath: path);
          if (transcript.isNotEmpty) {
            setState(() {
              _controller.text = transcript;
            });
          }
        } catch (e) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Error al procesar audio: $e')),
            );
          }
        } finally {
          setState(() => _isLoading = false);
        }
      }
    } else {
      if (await Permission.microphone.request().isGranted) {
        final dir = await getApplicationDocumentsDirectory();
        final path = '${dir.path}/chat_audio_${DateTime.now().millisecondsSinceEpoch}.m4a';
        await _record.start(const RecordConfig(encoder: AudioEncoder.aacLc), path: path);
        setState(() => _isRecording = true);
      }
    }
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            const Icon(Icons.smart_toy, color: Colors.white),
            const SizedBox(width: 8),
            Text(widget.title),
          ],
        ),
        backgroundColor: Colors.teal.shade700,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                final isUser = message['sender'] == 'user';
                return _buildMessageBubble(message['text']!, isUser);
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: CircularProgressIndicator(),
            ),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(String text, bool isUser) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: isUser ? Colors.teal.shade100 : Colors.grey.shade200,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: isUser ? const Radius.circular(16) : const Radius.circular(0),
            bottomRight: isUser ? const Radius.circular(0) : const Radius.circular(16),
          ),
        ),
        child: Text(text, style: const TextStyle(fontSize: 16)),
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      color: Colors.white,
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                decoration: InputDecoration(
                  hintText: 'Escribe un mensaje...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                  filled: true,
                  fillColor: Colors.grey.shade100,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                ),
                onSubmitted: (_) => _sendMessage(),
              ),
            ),
            const SizedBox(width: 8),
            CircleAvatar(
              backgroundColor: _isRecording ? Colors.red : Colors.teal.shade700,
              child: IconButton(
                icon: Icon(_isRecording ? Icons.stop : Icons.mic, color: Colors.white),
                onPressed: _toggleRecording,
              ),
            ),
            const SizedBox(width: 8),
            CircleAvatar(
              backgroundColor: Colors.teal.shade700,
              child: IconButton(
                icon: const Icon(Icons.send, color: Colors.white),
                onPressed: _sendMessage,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
