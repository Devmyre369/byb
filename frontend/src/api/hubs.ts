import api from "./client";

export type HubType =
  | "college"
  | "club"
  | "organisation"
  | "community";

export type MembershipPolicy = "automatic" | "approval";

export type HubMembership = {
  id: string;
  role: "owner" | "admin" | "editor" | "member";
  status: "pending" | "active" | "rejected";
  source: "creation" | "request" | "invitation";
  joined_at: string | null;
};

export type Hub = {
  id: string;
  name: string;
  slug: string;
  description: string;
  hub_type: HubType;
  membership_policy: MembershipPolicy;
  logo: string | null;
  cover_image: string | null;
  city: string;
  location: string;
  created_by_username: string;
  member_count: number;
  current_membership: HubMembership | null;
  verification_status: string;
  verified_at: string | null;
  created_at: string;
  updated_at: string;
};

export type HubListResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Hub[];
};

export type HubListParams = {
  page?: number;
  pageSize?: number;
  search?: string;
  hubType?: HubType | "all";
  city?: string;
};

export async function getHubs(
  params: HubListParams = {}
): Promise<HubListResponse> {
  const response = await api.get<HubListResponse>("/hubs/", {
    params: {
      page: params.page ?? 1,
      page_size: params.pageSize ?? 20,
      ...(params.search ? { search: params.search } : {}),
      ...(params.hubType && params.hubType !== "all"
        ? { hub_type: params.hubType }
        : {}),
      ...(params.city ? { city: params.city } : {}),
    },
  });

  return response.data;
}

export async function getHub(hubId: string): Promise<Hub> {
  const response = await api.get<Hub>(`/hubs/${hubId}/`);
  return response.data;
}

export async function getMyHubMembership(
  hubId: string
): Promise<HubMembership | null> {
  const response = await api.get<{
    membership: HubMembership | null;
  }>(`/hubs/${hubId}/membership/`);

  return response.data.membership;
}

export async function joinHub(
  hubId: string
): Promise<HubMembership> {
  const response = await api.post<{
    membership: HubMembership;
  }>(`/hubs/${hubId}/membership/`, {});

  return response.data.membership;
}

export async function leaveHub(hubId: string): Promise<void> {
  await api.delete(`/hubs/${hubId}/membership/`);
}
