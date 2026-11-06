
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./CreateEventPage.css";

type EventType = "personal" | "social" | "public";

const eventTypes: {
  id: EventType;
  number: string;
  icon: string;
  title: string;
  subtitle: string;
  description: string;
  examples: string[];
  action: string;
}[] = [
  {
    id: "personal",
    number: "01",
    icon: "✦",
    title: "Personal Event",
    subtitle: "Your moments. Your memories.",
    description:
      "Create a space for life's meaningful moments. Celebrate milestones, preserve memories and bring your closest people together.",
    examples: [
      "Birthdays",
      "Family gatherings",
      "Celebrations",
      "Personal milestones",
    ],
    action: "A private space for experiences that matter.",
  },
  {
    id: "social",
    number: "02",
    icon: "◉",
    title: "Social Event",
    subtitle: "Good people. Great experiences.",
    description:
      "Make plans, connect with friends and bring communities together around shared activities and experiences.",
    examples: [
      "Meetups",
      "Gaming sessions",
      "Sports",
      "Group outings",
    ],
    action: "A shared space for people to participate.",
  },
  {
    id: "public",
    number: "03",
    icon: "↗",
    title: "Public Event",
    subtitle: "Make it happen. Let everyone know.",
    description:
      "Bring your event to a wider audience. Publish opportunities, invite registrations and build a community around your event.",
    examples: [
      "College festivals",
      "Hackathons",
      "Workshops",
      "Conferences",
    ],
    action: "A discoverable space for larger audiences.",
  },
];

function CreateEventPage() {
  const navigate = useNavigate();

  const [selectedType, setSelectedType] =
    useState<EventType | null>(null);

  function handleContinue() {
    if (!selectedType) return;

    if (selectedType === "personal") {
      navigate("/events/create/personal");
    }
  }

  return (
    <main className="create-event-page">
      <header className="create-event-header">
        <div>
          <span className="create-event-eyebrow">
            BEYOND YOUR BUBBLE
          </span>

          <h1>What are we creating?</h1>

          <p>
            Every experience is different. Choose the kind of event
            you want to bring to life.
          </p>
        </div>

        <button
          type="button"
          className="create-event-back"
          onClick={() => navigate(-1)}
        >
          ← Back
        </button>
      </header>

      <section className="create-event-options">
        {eventTypes.map((eventType) => (
          <button
            key={eventType.id}
            type="button"
            className={`create-event-card ${
              selectedType === eventType.id ? "selected" : ""
            }`}
            onClick={() => setSelectedType(eventType.id)}
            aria-pressed={selectedType === eventType.id}
          >
            <div className="create-event-card-top">
              <span className="create-event-number">
                {eventType.number}
              </span>

              <span className="create-event-icon">
                {eventType.icon}
              </span>
            </div>

            <div className="create-event-card-content">
              <h2>{eventType.title}</h2>

              <h3>{eventType.subtitle}</h3>

              <p>{eventType.description}</p>

              <div className="create-event-examples">
                {eventType.examples.map((example) => (
                  <span key={example}>{example}</span>
                ))}
              </div>
            </div>

            <div className="create-event-card-bottom">
              <span>{eventType.action}</span>

              <span className="create-event-selection">
                {selectedType === eventType.id
                  ? "Selected"
                  : "Select"}
              </span>
            </div>
          </button>
        ))}
      </section>

      <footer className="create-event-footer">
        <p>
          You can configure your event details and audience in
          the next step.
        </p>

        <button
          type="button"
          className="create-event-continue"
          disabled={!selectedType}
          onClick={handleContinue}
        >
          Continue
          <span>→</span>
        </button>
      </footer>
    </main>
  );
}

export default CreateEventPage;
