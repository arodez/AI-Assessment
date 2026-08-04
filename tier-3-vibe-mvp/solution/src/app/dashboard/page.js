"use client";

import { useEffect, useState } from "react";

export default function Dashboard() {
  const [events, setEvents] = useState([]);
  const [expanded, setExpanded] = useState({}); // track which event's attendees are shown
  const [attendees, setAttendees] = useState({}); // {eventId: [emails]}

  const fetchEvents = async () => {
    const res = await fetch("/api/events");
    const data = await res.json();
    setEvents(data);
  };

  const fetchAttendees = async (eventId) => {
    const res = await fetch(`/api/events/${eventId}/attendees`);
    const { emails } = await res.json();
    setAttendees(prev => ({ ...prev, [eventId]: emails }));
  };

  const copyCSV = async (eventId) => {
    const res = await fetch(`/api/events/${eventId}/attendees?format=csv`);
    const csv = await res.text();
    await navigator.clipboard.writeText(csv);
    alert("Attendee CSV copied to clipboard!");
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem" }}>
      <h1 style={{ fontSize: "2.5rem", textAlign: "center", marginBottom: "2rem" }}>
        Organizer Dashboard
      </h1>
      <div className="event-grid">
        {events.map((e) => {
          const remaining = Math.max(0, e.max_capacity - e.rsvp_count);
          const isFull = remaining === 0;
          const isOpen = expanded[e.id] ?? false;
          return (
            <article key={e.id} className="glass-card" style={{ display: "flex", flexDirection: "column" }}>
              <div className="event-header">
                <span className="event-date">
                  {new Date(e.date).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}
                </span>
                <span className={`event-capacity ${isFull ? "capacity-full" : "capacity-ok"}`}>
                  {isFull ? "FULL" : `${remaining} / ${e.max_capacity} spots left`}
                </span>
              </div>
              <h3 style={{ fontSize: "1.25rem", marginBottom: "0.75rem" }}>{e.title}</h3>
              <p className="event-desc">{e.description || "No description."}</p>
              <button
                className="btn-primary"
                onClick={() => {
                  setExpanded(prev => ({ ...prev, [e.id]: !prev[e.id] }));
                  if (!attendees[e.id]) fetchAttendees(e.id);
                }}
                style={{ marginTop: "1rem" }}
              >
                {isOpen ? "Hide Attendees" : "View Attendees"}
              </button>
              {isOpen && (
                <div className="rsvp-section" style={{ marginTop: "1rem" }}>
                  <h4 style={{ marginBottom: "0.5rem" }}>Attendees</h4>
                  {attendees[e.id] ? (
                    <ul style={{ paddingLeft: "1.2rem" }}>
                      {attendees[e.id].map((email, i) => (
                        <li key={i}>{email}</li>
                      ))}
                    </ul>
                  ) : (
                    <p>Loading…</p>
                  )}
                  <button
                    className="btn-primary"
                    onClick={() => copyCSV(e.id)}
                    style={{ marginTop: "0.5rem" }}
                  >
                    Copy CSV to Clipboard
                  </button>
                </div>
              )}
            </article>
          );
        })}
      </div>
    </div>
  );
}
