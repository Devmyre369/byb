
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

export type EventMedia = {
  id: string;
  event_id: string;
  uploaded_by_id: string;
  media_type: "image";
  cloudinary_url: string;
  caption: string;
  moderation_status: "pending" | "approved" | "rejected" | "removed";
  created_at: string;
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

// Upload an event cover image to Cloudinary.
export type EventCoverUploadResponse = {
  cover_image: string;
};

export async function uploadEventCoverImage(
  image: File
): Promise<EventCoverUploadResponse> {
  const formData = new FormData();

  formData.append("image", image);

  const response = await api.post<EventCoverUploadResponse>(
    "/events/cover-image/",
    formData
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

// Create an event.
export async function createEvent(
  payload: CreateEventPayload
): Promise<EventItem> {
  const response = await api.post<EventItem>(
    "/events/",
    payload
  );

  return response.data;
}

// Upload an image moment to an event.
// Newly uploaded moments remain pending until approved.
export async function uploadEventMoment(
  eventId: string,
  image: File,
  caption = ""
): Promise<EventMedia> {
  const formData = new FormData();

  formData.append("image", image);
  formData.append("caption", caption);

  const response = await api.post<EventMedia>(
    `/events/${eventId}/media/`,
    formData
  );

  return response.data;
}

// Retrieve approved image moments for a specific event.
export async function getEventMoments(
  eventId: string
): Promise<EventMedia[]> {
  const response = await api.get<EventMedia[]>(
    `/events/${eventId}/media/`
  );

  return response.data;
}



export async function getUploadableEvents(
  page = 1,
  pageSize = 100
): Promise<EventListResponse> {
  const response = await api.get<EventListResponse>(
    "/events/uploadable/",
    {
      params: {
        page,
        page_size: pageSize,
      },
    }
  );

  return response.data;
}
