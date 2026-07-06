import { getRequestConfig } from "next-intl/server";

/** Single-locale setup: German is the only locale populated today. Adding
 * English later means creating messages/en.json and a locale switcher —
 * this plumbing (no hard-coded strings, next-intl on every page) already
 * supports it without further structural change. See docs/phase-2-roadmap.md.
 */
export default getRequestConfig(async () => {
  return {
    locale: "de",
    messages: (await import("../messages/de.json")).default,
  };
});
