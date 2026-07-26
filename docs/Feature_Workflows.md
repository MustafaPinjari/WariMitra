# Key Feature Workflows - WariMitra

## 1. SOS Emergency Assistance Flow
1. **Trigger:** Pilgrim presses the SOS button on the mobile app.
2. **Capture:** App captures GPS coordinates, timestamp, and optional incident details.
3. **Submission:** If offline, queues request; if online, sends to API Gateway.
4. **Routing:** System identifies the nearest responders (volunteers, medical, police) within the AI-calculated search radius.
5. **Notification:** Responders receive push notifications with the pilgrim's live location.
6. **Action:** A responder accepts the request. The pilgrim receives an ETA.
7. **Resolution:** The incident is addressed and marked as closed by the authorized responder, storing an audit log.

## 2. Missing Person Management Flow
1. **Report:** Pilgrim or Dindi leader reports a missing person, providing a photo, last known location, and physical description.
2. **AI Radius Calculation:** AI engine calculates the search radius based on time elapsed, crowd density, and walking speed.
3. **Alert:** Nearby volunteers, police, and relevant Dindi leaders are notified.
4. **Search & Verification:** A volunteer finds a match, uploads a photo, and the system (or family) verifies identity.
5. **Closure:** Case closed; family notified of reunification point.

## 3. Smart Temple Queue Management
1. **Monitoring:** IoT sensors and CCTV (Computer Vision) monitor entry gates.
2. **Prediction:** AI engine forecasts waiting times using entry rate, exit rate, and current capacity.
3. **Balancing:** If Gate A is congested, system automatically routes incoming pilgrims to Gate B via mobile app alerts.
4. **Slot Booking:** Priority pilgrims (senior citizens, divyang) book scheduled slots to bypass general queues.

## 4. Community Intelligence Engine (CIE)
1. **Report:** A volunteer reports a water shortage at a specific location.
2. **AI Validation:** AI checks for duplicate reports and anomalies.
3. **Verification:** The system asks 3 nearby verified volunteers to confirm the report.
4. **Action:** Once verified, the dashboard updates, alerting the NGO coordinator to dispatch a water tanker.
