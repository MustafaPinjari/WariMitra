export interface GPSLocationUpdate {
  entity_id: string;
  type: 'police' | 'ambulance' | 'ngo' | 'volunteer' | 'sos';
  lat: number;
  lng: number;
  speed?: string;
  timestamp: string;
}

export class WariMitraWebSocketClient {
  private url: string;
  private ws: WebSocket | null = null;
  private listeners: Array<(data: GPSLocationUpdate) => void> = [];
  private reconnectInterval: number = 3000;

  constructor(url = 'ws://127.0.0.1:8000/ws/v1/tracking/') {
    this.url = url;
  }

  public connect() {
    if (typeof window === 'undefined') return;

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('[WariMitra WebSockets] Connected to real-time telemetry stream:', this.url);
      };

      this.ws.onmessage = (event) => {
        try {
          const data: GPSLocationUpdate = JSON.parse(event.data);
          this.listeners.forEach((callback) => callback(data));
        } catch (e) {
          console.error('[WariMitra WebSockets] Error parsing message payload:', e);
        }
      };

      this.ws.onclose = () => {
        console.warn('[WariMitra WebSockets] Disconnected. Reconnecting in 3s...');
        setTimeout(() => this.connect(), this.reconnectInterval);
      };

      this.ws.onerror = (err) => {
        console.error('[WariMitra WebSockets] Socket Error:', err);
      };
    } catch (err) {
      console.warn('[WariMitra WebSockets] Live WebSocket server unavailable. Client fallback active.');
    }
  }

  public subscribe(callback: (data: GPSLocationUpdate) => void) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter((cb) => cb !== callback);
    };
  }

  public sendLocation(update: GPSLocationUpdate) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(update));
    }
  }

  public disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

export const globalTelemetrySocket = new WariMitraWebSocketClient();
