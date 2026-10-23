import { test, expect } from "@playwright/test";
import type { Project } from "../src/types";
let baseline: Project;
test.beforeAll(async ({ request }) => {
  baseline = (await (await request.get("/api/bootstrap")).json()).project;
});
test.beforeEach(async ({ request, page }) => {
  const current = await (await request.get("/api/bootstrap")).json();
  const headers = {
    "X-VirtualWago-Client": "workbench",
    "X-VirtualWago-Instance": current.state.instance,
  };
  await request.post("/api/command", {
    headers,
    data: { generation: current.state.generation, command: { action: "stop" } },
  });
  const reset = await request.put("/api/project", {
    headers,
    data: { generation: current.state.generation, project: baseline },
  });
  expect(reset.ok()).toBeTruthy();
  await page.route("**/*", (route) => {
    const url = new URL(route.request().url());
    if (url.hostname !== "127.0.0.1" && url.protocol !== "data:")
      return route.abort();
    return route.continue();
  });
  await page.goto("/");
  await expect(page.getByText("Kern verbunden", { exact: true })).toBeVisible();
});

test("effective outputs drive feedback, while a closed gate blocks it", async ({
  page,
}) => {
  await page
    .getByRole("button", {
      name: "Kanal 1 Testvorgabe einschalten",
      exact: true,
    })
    .click();
  await page
    .getByRole("button", { name: "Einzelschritt", exact: true })
    .click();
  await page
    .getByRole("button", {
      name: "750-430 · Digitale Rückmeldungen",
      exact: true,
    })
    .click();
  const feedback = page.locator(".signal-table tbody tr").first();
  await expect(feedback.locator(".effective")).toHaveText("0");
  await page.getByRole("switch", { name: "Modellfreigabe" }).click();
  await page
    .getByRole("button", { name: "Einzelschritt", exact: true })
    .click();
  await expect(feedback.locator(".effective")).toHaveText("1");
  await expect(
    feedback.getByRole("button", { name: /Eingang ausschalten/ }),
  ).toBeDisabled();
  await page
    .getByRole("button", { name: "Simulation stoppen", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Einzelschritt", exact: true })
    .click();
  await expect(feedback.locator(".effective")).toHaveText("0");
});

test("add, reorder and apply modules without losing stable script targets", async ({
  page,
}) => {
  await page
    .getByRole("button", { name: "750-1405 hinzufügen", exact: true })
    .click();
  await expect(
    page.getByText("Entwurf geändert", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Start", exact: true }),
  ).toBeDisabled();
  await page
    .getByRole("button", { name: "Modul nach links", exact: true })
    .click();
  await page.getByRole("button", { name: "Übernehmen", exact: true }).click();
  await expect(page.getByText("Gespeichert", { exact: true })).toBeVisible();
  await page
    .getByRole("button", {
      name: "750-530 · Digitale Testausgänge",
      exact: true,
    })
    .click();
  await page
    .getByRole("button", {
      name: "Kanal 1 Testvorgabe einschalten",
      exact: true,
    })
    .click();
  await page.getByRole("switch", { name: "Modellfreigabe" }).click();
  await page
    .getByRole("button", { name: "Einzelschritt", exact: true })
    .click();
  await page
    .getByRole("button", {
      name: "750-430 · Digitale Rückmeldungen",
      exact: true,
    })
    .click();
  await expect(
    page.locator(".signal-table tbody tr").first().locator(".effective"),
  ).toHaveText("1");
});

test("bad script cannot replace the active project; runtime loops fail bounded", async ({
  page,
}) => {
  await page.getByRole("tab", { name: /Reaktionsskripte/ }).click();
  await page
    .getByRole("textbox", { name: "Reaktionscode" })
    .fill("broken script");
  await page.getByRole("button", { name: "Übernehmen", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Ventilrückmeldung");
  await expect(
    page.getByText("Entwurf geändert", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("textbox", { name: "Reaktionscode" })
    .fill("fn react(output, previous, dt_s, time_s) { loop {} 0.0 }");
  await page.getByRole("button", { name: "Übernehmen", exact: true }).click();
  await expect(page.getByText("Gespeichert", { exact: true })).toBeVisible();
  await page
    .getByRole("button", { name: "Einzelschritt", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("operations");
  await expect(
    page.getByRole("switch", { name: "Modellfreigabe" }),
  ).toHaveAttribute("aria-checked", "false");
});

test("a JSON module pack loads and runs without a new frontend or Rust build", async ({
  page,
}) => {
  const pack = structuredClone(
    baseline.packages.find((p) => p.article === "750-466")!,
  );
  pack.id = "own.temperature";
  pack.article = "TEMP-01";
  pack.title = "Eigener Temperatursensor";
  pack.channels = [pack.channels[0]];
  Object.assign(pack.channels[0], {
    min: -10,
    max: 60,
    initial: 20,
    unit: "°C",
    encoding: { codec: "linear", scale: 10, offset: 100, max_raw: 700 },
  });
  await page
    .getByLabel("Modulpaket importieren", { exact: true })
    .setInputFiles({
      name: "temperature.json",
      mimeType: "application/json",
      buffer: Buffer.from(JSON.stringify(pack)),
    });
  await expect(
    page.getByRole("button", { name: "TEMP-01 hinzufügen", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "TEMP-01 hinzufügen", exact: true })
    .click();
  await page.getByRole("button", { name: "Übernehmen", exact: true }).click();
  await expect(page.getByText("Gespeichert", { exact: true })).toBeVisible();
  await expect(
    page.locator(".signal-table tbody tr").first().locator(".effective"),
  ).toHaveText("20 °C");
  await page.reload();
  await expect(page.getByText("Kern verbunden", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("button", {
      name: "TEMP-01 · Eigener Temperatursensor",
      exact: true,
    }),
  ).toBeVisible();
});

test("desktop and mobile stay usable; the app makes no external requests", async ({
  page,
}) => {
  const external: string[] = [];
  const consoleErrors: string[] = [];
  page.on("request", (r) => {
    if (new URL(r.url()).hostname !== "127.0.0.1") external.push(r.url());
  });
  page.on("pageerror", (e) => consoleErrors.push(e.message));
  await page.reload();
  await expect(page.getByText("Kern verbunden", { exact: true })).toBeVisible();
  await page.screenshot({
    path: "test-results/workbench-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(
    page.getByRole("button", { name: "Start", exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({
    path: "test-results/workbench-mobile.png",
    fullPage: true,
  });
  expect(external).toEqual([]);
  expect(consoleErrors).toEqual([]);
});

test("reaction files and self-contained project exports round trip", async ({
  page,
}) => {
  await page.getByRole("tab", { name: /Reaktionsskripte/ }).click();
  const code =
    "fn react(output, previous, dt_s, time_s) { if output > 0.5 { 0.0 } else { 1.0 } }";
  await page
    .getByLabel("Reaktionsskript importieren", { exact: true })
    .setInputFiles({
      name: "inverse.rhai",
      mimeType: "text/plain",
      buffer: Buffer.from(code),
    });
  await expect(
    page.getByRole("textbox", { name: "Reaktionscode" }),
  ).toHaveValue(code);
  await page.getByRole("button", { name: "Übernehmen", exact: true }).click();
  await expect(page.getByText("Gespeichert", { exact: true })).toBeVisible();
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: "Export", exact: true }).click(),
  ]);
  const stream = await download.createReadStream();
  let bytes = "";
  for await (const chunk of stream!) bytes += chunk.toString();
  const exported = JSON.parse(bytes);
  expect(exported.reactions[0].code).toBe(code);
  expect(exported.packages).toHaveLength(7);
  expect(exported.permit).toBeUndefined();
  await page
    .getByRole("button", { name: "Einzelschritt", exact: true })
    .click();
  await page
    .getByRole("button", {
      name: "750-430 · Digitale Rückmeldungen",
      exact: true,
    })
    .click();
  await page.getByRole("tab", { name: "Live-I/O", exact: true }).click();
  await expect(
    page.locator(".signal-table tbody tr").first().locator(".effective"),
  ).toHaveText("1");
});

test("the Rust worker advances time independently and pause freezes it", async ({
  page,
  request,
}) => {
  await page.getByRole("button", { name: "Start", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Pause", exact: true }),
  ).toBeVisible();
  await expect
    .poll(
      async () =>
        (await (await request.get("/api/bootstrap")).json()).state.time_ms,
    )
    .toBeGreaterThan(100);
  await page
    .getByLabel("Simulationsgeschwindigkeit", { exact: true })
    .selectOption("5");
  await page.getByRole("button", { name: "Pause", exact: true }).click();
  const paused = (await (await request.get("/api/bootstrap")).json()).state;
  await page.waitForTimeout(100);
  const current = (await (await request.get("/api/bootstrap")).json()).state;
  expect(current.time_ms).toBe(paused.time_ms);
  expect(current.speed).toBe(5);
  // A constant SVG stroke has zero-height geometry but is painted. Check the
  // actual time samples rather than Playwright's element-box visibility rule.
  await expect
    .poll(
      async () =>
        (
          await page.locator(".trend-svg polyline").getAttribute("points")
        )?.split(" ").length ?? 0,
    )
    .toBeGreaterThan(1);
});
