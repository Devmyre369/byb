
import api from "./client";

export type MomentUploader = {
  id: string;
  username: string;
  first_name: string;
  profile_picture: string;
};

export type MomentEvent = {
  id: string;
  title: string;
  location_name: string;
  city: string;
};

export type Moment = {
  id: string;
  media_type: "image";
  cloudinary_url: string;
  caption: string;
  created_at: string;
  uploader: MomentUploader;
  event: MomentEvent;
};

export type MomentModerationStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "removed";

export type MyMoment = {
  id: string;
  media_type: "image";
  cloudinary_url: string;
  caption: string;
  moderation_status: MomentModerationStatus;
  created_at: string;
  event: MomentEvent;
};

export type MomentsFeedResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Moment[];
};

export type MyMomentsResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: MyMoment[];
};

export async function getMoments(
  page = 1,
  pageSize = 20
): Promise<MomentsFeedResponse> {
  const response = await api.get<MomentsFeedResponse>(
    "/events/moments/",
    {
      params: {
        page,
        page_size: pageSize,
      },
    }
  );

  return response.data;
}

export async function getMyMoments(
  page = 1,
  pageSize = 20
): Promise<MyMomentsResponse> {
  const response = await api.get<MyMomentsResponse>(
    "/events/my-moments/",
    {
      params: {
        page,
        page_size: pageSize,
      },
    }
  );

  return response.data;
}
