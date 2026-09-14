import { ref } from "vue";

export const personalLocation = ref(window.location.pathname + window.location.search);

export function syncPersonalLocation(): void {
  personalLocation.value = window.location.pathname + window.location.search;
}

export function openPersonalContent(tab: "contributions" | "private" = "contributions", materialId?: string): void {
  const query = new URLSearchParams({ tab });
  if (materialId) query.set("material", materialId);
  window.history.pushState(null, "", `/personal?${query}`);
  syncPersonalLocation();
}

export function closePersonalContent(): void {
  window.history.pushState(null, "", "/");
  syncPersonalLocation();
}
