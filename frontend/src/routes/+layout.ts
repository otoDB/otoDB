import client, { setToken } from "$lib/api";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async ({ data, fetch }) => {
  if (!data.session || !data.csrf)
    return;
  
  const status = await client.GET('/api/auth/status', { fetch });
  if (!status.data)
    return;

  setToken(data.csrf);
  return {
    user: {
      name: status.data.username,
      id: status.data.user_id
    }
  };
}
