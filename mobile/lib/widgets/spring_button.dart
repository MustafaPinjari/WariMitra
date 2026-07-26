import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';

class SpringButton extends StatefulWidget {
  final Widget child;
  final VoidCallback? onLongPress;
  final VoidCallback? onTap;

  const SpringButton({
    Key? key,
    required this.child,
    this.onLongPress,
    this.onTap,
  }) : super(key: key);

  @override
  _SpringButtonState createState() => _SpringButtonState();
}

class _SpringButtonState extends State<SpringButton> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();
    // Using a normal animation controller, but we'll drive it with spring physics
    _controller = AnimationController(vsync: this, lowerBound: 0.0, upperBound: 1.0, value: 1.0);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _animateTo(double target) {
    // Apple-style UI Spring: Damping 1.0 (no bounce), Response ~0.3s
    // Physics SpringDescription: mass, stiffness, damping
    final spring = SpringDescription(
      mass: 1.0,
      stiffness: 400.0,
      damping: 40.0, 
    );
    
    final simulation = SpringSimulation(spring, _controller.value, target, _controller.velocity);
    _controller.animateWith(simulation);
  }

  void _handleTapDown(TapDownDetails details) {
    setState(() { _isPressed = true; });
    _animateTo(0.92); // Scale down on press instantly
  }

  void _handleTapUp(TapUpDetails details) {
    setState(() { _isPressed = false; });
    _animateTo(1.0);
    if (widget.onTap != null) widget.onTap!();
  }

  void _handleTapCancel() {
    setState(() { _isPressed = false; });
    _animateTo(1.0);
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: _handleTapDown,
      onTapUp: _handleTapUp,
      onTapCancel: _handleTapCancel,
      onLongPress: () {
        if (widget.onLongPress != null) widget.onLongPress!();
        _handleTapCancel(); // snap back up
      },
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return Transform.scale(
            scale: _controller.value,
            child: child,
          );
        },
        child: widget.child,
      ),
    );
  }
}
