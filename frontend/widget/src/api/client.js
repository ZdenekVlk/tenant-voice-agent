const DEFAULT_TIMEOUT_MS = 10000;

const normalizeBaseUrl = (value) => value.replace(/\/+$/, "");

const readJson = async (response) => {
  if (!response.body) {
    return null;
  }

  try {
    return await response.json();
  } catch {
    return null;
  }
};

const buildError = (response, payload) => {
  const detail = payload?.detail || payload?.error || "request_failed";
  return new Error(`${response.status} ${detail}`);
};

const withTimeout = async (promise, timeoutMs) => {
  let timeoutId;
  const timeoutPromise = new Promise((_, reject) => {
    timeoutId = setTimeout(() => reject(new Error("timeout")), timeoutMs);
  });

  try {
    return await Promise.race([promise, timeoutPromise]);
  } finally {
    clearTimeout(timeoutId);
  }
};

export const createClient = ({ baseUrl }) => {
  const apiBase = normalizeBaseUrl(baseUrl);

  return {
    async createSession() {
      const response = await withTimeout(
        fetch(`${apiBase}/widget/session`, {
          method: "POST",
        }),
        DEFAULT_TIMEOUT_MS
      );

      const payload = await readJson(response);
      if (!response.ok) {
        throw buildError(response, payload);
      }

      return payload;
    },

    async createMessage(token, text) {
      const response = await withTimeout(
        fetch(`${apiBase}/widget/messages`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text,
            metadata: {},
          }),
        }),
        DEFAULT_TIMEOUT_MS
      );

      const payload = await readJson(response);
      if (!response.ok) {
        throw buildError(response, payload);
      }

      return payload;
    },
  };
};
