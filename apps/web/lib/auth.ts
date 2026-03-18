export type SessionUser = {
  id: string;
  name: string;
  provider: "jellyfin";
};

export async function getSessionUser(): Promise<SessionUser | null> {
  return {
    id: "demo-user",
    name: "Demo User",
    provider: "jellyfin",
  };
}
