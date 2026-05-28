const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

const handleResponse = async (response, url) => {
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    console.error("[api] error", {
      url,
      status: response.status,
      payload,
    });
    throw new Error(
      typeof payload === "string" && payload
        ? payload
        : "Request failed"
    );
  }

  console.debug("[api] success", { url, status: response.status });
  return payload;
};

export const getStudents = (page = 1, size = 120) => {
  const url = `${API_BASE}/students?page=${page}&size=${size}`;
  console.debug("[api] GET", url);
  return fetch(url).then((response) => handleResponse(response, url));
};

export const getStudentDetail = (studentId) => {
  const url = `${API_BASE}/students/${studentId}`;
  console.debug("[api] GET", url);
  return fetch(url).then((response) => handleResponse(response, url));
};

export const getAlerts = () => {
  const url = `${API_BASE}/alerts`;
  console.debug("[api] GET", url);
  return fetch(url).then((response) => handleResponse(response, url));
};
