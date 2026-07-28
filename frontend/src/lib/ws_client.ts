export class WariMitraWebSocketClient<T = any> {
  private url: string;
  private ws: WebSocket | null = null;
  private listeners: Array<(data: T) => void> = [];
  
  // Exponential backoff properties
  private baseReconnectInterval: number = 1000;
  private maxReconnectInterval: number = 30000;
  private reconnectAttempts: number = 0;
  private intentionallyClosed: boolean = false;

  constructor(url: string) {
    this.url = url;
  }

  public connect() {
    if (typeof window === 'undefined') return;

    this.intentionallyClosed = false;

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log(`[WariMitra WebSockets] Connected to stream: ${this.url}`);
        this.reconnectAttempts = 0; // Reset attempts on successful connection
      };

      this.ws.onmessage = (event) => {
        try {
          const data: T = JSON.parse(event.data);
          this.listeners.forEach((callback) => callback(data));
        } catch (e) {
          console.error('[WariMitra WebSockets] Error parsing message payload:', e);
        }
      };

      this.ws.onclose = () => {
        if (this.intentionallyClosed) {
          console.log(`[WariMitra WebSockets] Intentionally closed stream: ${this.url}`);
          return;
        }

        // Exponential backoff calculation (e.g. 1s, 2s, 4s, 8s, max 30s)
        const delay = Math.min(
          this.baseReconnectInterval * Math.pow(2, this.reconnectAttempts),
          this.maxReconnectInterval
        );
        
        console.warn(`[WariMitra WebSockets] Disconnected. Reconnecting in ${delay}ms... (Attempt ${this.reconnectAttempts + 1})`);
        
        setTimeout(() => {
          this.reconnectAttempts++;
          this.connect();
        }, delay);
      };

      this.ws.onerror = (err) => {
        console.error('[WariMitra WebSockets] Socket Error:', err);
      };
    } catch (err) {
      console.warn('[WariMitra WebSockets] Live WebSocket server unavailable. Client fallback active.');
    }
  }

  public subscribe(callback: (data: T) => void) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter((cb) => cb !== callback);
    };
  }

  public sendData(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  public disconnect() {
    this.intentionallyClosed = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Global instances for different streams
export const globalTelemetrySocket = new WariMitraWebSocketClient('ws://127.0.0.1:8000/ws/v1/tracking/');
export const sosIncidentSocket = new WariMitraWebSocketClient('ws://localhost:8000/ws/sos/');
