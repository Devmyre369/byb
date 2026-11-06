
import api from "./client";

export type EventItem = {
  id: string;
  creator_id: string;
  title: string;
  description: string;
  event_type: string;
  category: string;
  cover_image: string;
  starts_at: string;
  ends_at: string | null;
  timezone: string;
  location_name: string;
  location_address: string;
  city: string;
  visibility: string;
  capacity: number | null;
  registration_enabled: boolean;
  registration_mode: string;
  registration_opens_at: string | null;
  registration_closes_at: string | null;
  status: string;
  completed_at: string | null;
  archive_at: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type EventListResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: EventItem[];
};

// Fetch paginated events.
export async function getEvents(
  page = 1,
  pageSize = 20
): Promise<EventListResponse> {
  const response = await api.get<EventListResponse>("/events/", {
    params: {
      page,
      page_size: pageSize,
    },
  });

  return response.data;
}

// Fetch one event using its UUID.
export async function getEvent(
  eventId: string
): Promise<EventItem> {
  const response = await api.get<EventItem>(
    `/events/${eventId}/`
  );

  return response.data;
}



export type CreateEventPayload = {
  title: string;
  description: string;
  event_type: "personal" | "social" | "public";
  category: string;
  cover_image: string;
  starts_at: string;
  ends_at: string | null;
  timezone: string;
  location_name: string;
  location_address: string;
  city: string;
  visibility: "private" | "selected" | "public";
  capacity: number | null;
  registration_enabled: boolean;
  registration_mode: "automatic" | "approval";
  registration_opens_at: string | null;
  registration_closes_at: string | null;
};

export async function createEvent(
  payload: CreateEventPayload
): Promise<EventItem> {
  const response = await api.post<EventItem>(
    "/events/",
    payload
  );

  return response.data;
}
