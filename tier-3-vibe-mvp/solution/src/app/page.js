"use client";

import { useState, useEffect } from "react";

export default function Home() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form states
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");
  const [description, setDescription] = useState("");
  const [maxCapacity, setMaxCapacity] = useState("");
  
  // Feedback states
  const [formSuccess, setFormSuccess] = useState("");
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // RSVP feedback tracker per event ID
  const [rsvpEmails, setRsvpEmails] = useState({}); // { [eventId]: email }
  const [rsvpFeedback, setRsvpFeedback] = useState({}); // { [eventId]: { success: '', error: '' } }

  const fetchEvents = async () => {
    try {
      const res = await fetch("/api/events");
      if (res.ok) {
        const data = await res.json();
        setEvents(data);
      }
    } catch (err) {
      console.error("Failed to load events", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleCreateEvent = async (e) => {
    e.preventDefault();
    setFormError("");
    setFormSuccess("");
    setSubmitting(true);

    // Client-side validations
    if (!title.trim()) {
      setFormError("Title is required.");
      setSubmitting(false);
      return;
    }

    if (!date) {
      setFormError("Date is required.");
      setSubmitting(false);
      return;
    }

    const eventDate = new Date(date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (eventDate < today) {
      setFormError("Event date cannot be in the past.");
      setSubmitting(false);
      return;
    }

    const cap = parseInt(maxCapacity, 10);
    if (isNaN(cap) || cap <= 0) {
      setFormError("Max capacity must be a positive integer greater than 0.");
      setSubmitting(false);
      return;
    }

    try {
      const res = await fetch("/api/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, date, description, maxCapacity: cap }),
      });

      const data = await res.json();
      if (res.ok) {
        setFormSuccess("Event created successfully!");
        setTitle("");
        setDate("");
        setDescription("");
        setMaxCapacity("");
        fetchEvents();
      } else {
        setFormError(data.error || "Failed to create event.");
      }
    } catch (err) {
      setFormError("An error occurred. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleRsvp = async (e, eventId) => {
    e.preventDefault();
    const email = rsvpEmails[eventId] || "";
    
    // Clear previous feedback for this event
    setRsvpFeedback(prev => ({ ...prev, [eventId]: { success: "", error: "" } }));

    if (!email.trim()) {
      setRsvpFeedback(prev => ({
        ...prev,
        [eventId]: { success: "", error: "Email is required." }
      }));
      return;
    }

    try {
      const res = await fetch("/api/rsvps", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ eventId, email }),
      });

      const data = await res.json();
      if (res.ok) {
        setRsvpFeedback(prev => ({
          ...prev,
          [eventId]: { success: "RSVP successful!", error: "" }
        }));
        // Clear input
        setRsvpEmails(prev => ({ ...prev, [eventId]: "" }));
        // Refresh events list to update remaining spots
        fetchEvents();
      } else {
        setRsvpFeedback(prev => ({
          ...prev,
          [eventId]: { success: "", error: data.error || "RSVP failed." }
        }));
      }
    } catch (err) {
      setRsvpFeedback(prev => ({
        ...prev,
        [eventId]: { success: "", error: "An error occurred. Please try again." }
      }));
    }
  };

  const handleRsvpEmailChange = (eventId, val) => {
    setRsvpEmails(prev => ({ ...prev, [eventId]: val }));
  };

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem" }}>
      <header style={{ marginBottom: "3rem", textAlign: "center" }}>
        <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>Community Events Hub</h1>
        <p style={{ color: "var(--text-secondary)" }}>Create, RSVP, and stay connected.</p>
      </header>

      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "2.5rem" }}>
        {/* Event Creation Form */}
        <section className="glass-card" style={{ maxWidth: "600px", margin: "0 auto", width: "100%" }}>
          <h2 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>Create a New Event</h2>
          
          <form onSubmit={handleCreateEvent}>
            <div className="form-group">
              <label className="form-label" htmlFor="title">Event Title</label>
              <input
                id="title"
                className="form-input"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Next.js Study Group"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="date">Date</label>
              <input
                id="date"
                className="form-input"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="description">Description</label>
              <textarea
                id="description"
                className="form-textarea"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Provide event details..."
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="maxCapacity">Maximum Capacity</label>
              <input
                id="maxCapacity"
                className="form-input"
                type="number"
                min="1"
                value={maxCapacity}
                onChange={(e) => setMaxCapacity(e.target.value)}
                placeholder="e.g. 50"
                required
              />
            </div>

            {formSuccess && <p className="status-message status-success" style={{ marginBottom: "1rem" }}>{formSuccess}</p>}
            {formError && <p className="status-message status-error" style={{ marginBottom: "1rem" }}>{formError}</p>}

            <button className="btn-primary" type="submit" disabled={submitting} style={{ width: "100%" }}>
              {submitting ? "Creating..." : "Create Event"}
            </button>
          </form>
        </section>

        {/* Public Upcoming Events List */}
        <section style={{ marginTop: "2rem" }}>
          <h2 style={{ fontSize: "1.75rem", borderBottom: "1px solid var(--border-glass)", paddingBottom: "0.75rem", marginBottom: "1.5rem" }}>
            Upcoming Events
          </h2>

          {loading ? (
            <p style={{ textAlign: "center", color: "var(--text-secondary)" }}>Loading events...</p>
          ) : events.length === 0 ? (
            <p style={{ textAlign: "center", color: "var(--text-secondary)" }}>No upcoming events scheduled yet.</p>
          ) : (
            <div className="event-grid">
              {events.map((event) => {
                const remaining = Math.max(0, event.max_capacity - event.rsvp_count);
                const isFull = remaining === 0;
                const feedback = rsvpFeedback[event.id] || { success: "", error: "" };

                return (
                  <article key={event.id} className="glass-card" style={{ display: "flex", flexDirection: "column" }}>
                    <div className="event-header">
                      <span className="event-date">{new Date(event.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' })}</span>
                      <span className={`event-capacity ${isFull ? 'capacity-full' : 'capacity-ok'}`}>
                        {isFull ? "FULL" : `${remaining} of ${event.max_capacity} spots left`}
                      </span>
                    </div>

                    <h3 style={{ fontSize: "1.25rem", marginBottom: "0.75rem" }}>{event.title}</h3>
                    <p className="event-desc">{event.description || "No description provided."}</p>

                    <div className="rsvp-section">
                      <h4 style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "0.5rem" }}>RSVP for this Event</h4>
                      
                      <form onSubmit={(e) => handleRsvp(e, event.id)}>
                        <div className="rsvp-input-group">
                          <input
                            aria-label="Email for RSVP"
                            className="form-input"
                            type="email"
                            placeholder="Enter your email"
                            value={rsvpEmails[event.id] || ""}
                            onChange={(e) => handleRsvpEmailChange(event.id, e.target.value)}
                            disabled={isFull}
                            required
                          />
                          <button className="btn-primary" type="submit" disabled={isFull}>
                            RSVP
                          </button>
                        </div>
                      </form>

                      {feedback.success && <p className="status-message status-success">{feedback.success}</p>}
                      {feedback.error && <p className="status-message status-error">{feedback.error}</p>}
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
