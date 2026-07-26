import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import '../widgets/spring_button.dart';

class SOSScreen extends StatelessWidget {
  SOSScreen({Key? key}) : super(key: key);
  
  final dio = Dio();

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              "EMERGENCY",
              style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.red),
            ),
            const SizedBox(height: 8),
            const Text(
              "Press and hold the button below to instantly alert authorities and volunteers.",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 64),
            
            SpringButton(
              onLongPress: () async {
                try {
                  // Show loading
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text("Sending SOS..."), duration: Duration(seconds: 1)),
                  );
                  
                  // Use a fixed URL for Android emulator (10.0.2.2) or desktop (localhost)
                  const String baseUrl = 'http://localhost:8000/api/v1';
                  
                  final response = await dio.post('$baseUrl/sos/', data: {
                    'incident_type': 'Medical',
                    'severity': 'Critical',
                    'latitude': '18.6721', // Dummy Alandi coord
                    'longitude': '73.8889',
                  });
                  
                  if (response.statusCode == 201) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text("SOS Alert Sent! Command center notified."),
                        backgroundColor: Colors.red,
                      )
                    );
                  }
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text("Failed to send SOS: $e"))
                  );
                }
              },
              child: Container(
                width: 250,
                height: 250,
                decoration: BoxDecoration(
                  color: Colors.red.shade600,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.red.withOpacity(0.5),
                      blurRadius: 30,
                      spreadRadius: 10,
                    )
                  ]
                ),
                child: const Center(
                  child: Text(
                    "SOS",
                    style: TextStyle(
                      fontSize: 64,
                      fontWeight: FontWeight.w900,
                      color: Colors.white,
                      letterSpacing: -2,
                    ),
                  ),
                ),
              ),
            ),
            
            const SizedBox(height: 64),
            const Text("Tap and hold for 3 seconds.", style: TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}
