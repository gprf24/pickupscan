// app/static/qr-scanner.js
/**
 * Frontend logic for the QR scanner.
 *
 * Uses html5-qrcode (CDN) to access the camera and detect QR codes.
 * Expects the QR code content to contain ?p=<pharmacy_public_id>
 * or just "p=<pharmacy_public_id>".
 *
 * After detecting a QR code:
 *  1. Parse public pharmacy ID from the QR payload.
 *  2. Ask the browser for GPS coordinates (if available).
 *  3. Send the data to /api/scan as JSON.
 *  4. Show success or error message on the page.
 */

/**
 * Extract the public pharmacy ID from the decoded QR text.
 * Supports:
 *  - full URLs, e.g. "https://pickupscan.de/?p=abc123"
 *  - plain query strings: "p=abc123"
 */
function parseQrPayload(decodedText) {
  try {
    let queryPart = decodedText;
    const qIndex = decodedText.indexOf("?");
    if (qIndex !== -1) {
      // Keep only the query string part after '?'
      queryPart = decodedText.slice(qIndex + 1);
    }
    const params = new URLSearchParams(queryPart);
    const pharmacyPublicId = params.get("p") || params.get("pharmacy");

    return { pharmacyPublicId };
  } catch (e) {
    console.error("Failed to parse QR payload", e);
    return { pharmacyPublicId: null };
  }
}

/**
 * Send scan data to the backend.
 */
async function sendScan(payload) {
  const resp = await fetch("/api/scan", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return resp.json();
}

/**
 * Update status message on the page.
 */
function updateStatus(msg, isError = false) {
  const el = document.getElementById("scan-status");
  if (!el) return;
  el.textContent = msg;
  el.className = "status" + (isError ? " status-error" : " status-ok");
}

/**
 * Initialize the QR scanner using html5-qrcode.
 */
function startScanner() {
  const qrRegionId = "qr-reader";
  const html5QrCode = new Html5Qrcode(qrRegionId);

  // Configuration: 10 FPS, 250px scanning box
  const config = { fps: 10, qrbox: 250 };

  /**
   * Called when a QR code is successfully decoded.
   */
  function onScanSuccess(decodedText, decodedResult) {
    // Stop scanning so we don't process the same code multiple times.
    html5QrCode.stop().catch(console.error);
    updateStatus("QR detected, processing...");

    const { pharmacyPublicId } = parseQrPayload(decodedText);
    if (!pharmacyPublicId) {
      updateStatus("QR code format not recognized.", true);
      return;
    }

    const sendPayload = async (lat, lon) => {
      const payload = {
        pharmacy_public_id: pharmacyPublicId,
        latitude: lat,
        longitude: lon,
        raw_qr: decodedText,
      };

      try {
        const data = await sendScan(payload);
        if (data.ok) {
          updateStatus("Scan saved successfully. Thank you!");
        } else {
          updateStatus("Error: " + (data.error || "unknown"), true);
        }
      } catch (err) {
        console.error(err);
        updateStatus("Failed to send scan.", true);
      }
    };

    const handlePosition = (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      sendPayload(lat, lon);
    };

    const handlePositionError = () => {
      // If location is not available, still send the scan with null coordinates.
      sendPayload(null, null);
    };

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        handlePosition,
        handlePositionError,
        {
          enableHighAccuracy: true,
          timeout: 5000,
        },
      );
    } else {
      handlePositionError();
    }
  }

  /**
   * Called on scan failure (no QR yet).
   * We ignore these events, scanner continues running.
   */
  function onScanFailure(error) {
    // No-op for now.
  }

  // Detect cameras, then start with the first available one.
  Html5Qrcode.getCameras()
    .then((devices) => {
      if (!devices || devices.length === 0) {
        updateStatus("No camera found.", true);
        return;
      }
      const cameraId = devices[0].id;
      html5QrCode.start(cameraId, config, onScanSuccess, onScanFailure);
    })
    .catch((err) => {
      console.error(err);
      updateStatus("Failed to start camera.", true);
    });
}

// Start the scanner when the DOM is ready.
document.addEventListener("DOMContentLoaded", startScanner);
