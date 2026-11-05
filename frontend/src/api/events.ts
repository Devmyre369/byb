
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
