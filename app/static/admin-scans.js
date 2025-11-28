// app/static/admin-scans.js
/**
 * Convert UTC timestamps from the HTML table into
 * the browser's local time and update the cell text.
 *
 * The template passes timestamps in data-utc attribute, e.g.:
 *   <td class="utc-time" data-utc="2025-11-28T21:35:12.123456Z"></td>
 */

document.addEventListener("DOMContentLoaded", () => {
  // Select all cells that contain UTC timestamps
  const utcCells = document.querySelectorAll(".utc-time");

  utcCells.forEach((cell) => {
    const utcValue = cell.dataset.utc;
    if (!utcValue) {
      return;
    }

    // Create a Date object from UTC ISO string.
    // The trailing "Z" tells JS that this is UTC.
    const date = new Date(utcValue);
    if (isNaN(date.getTime())) {
      // If parsing fails, do not modify the cell.
      return;
    }

    // Format options for local time display.
    // You can adjust to your preferred format.
    const options = {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    };

    // Use the browser's locale (undefined) or force e.g. "de-DE".
    const localString = date.toLocaleString(undefined, options);

    // Update cell text and explicitly mention that this is local time.
    cell.textContent = `${localString} (local browser time)`;
  });
});
