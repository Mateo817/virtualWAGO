import { test, expect } from "@playwright/test";
import type { Project } from "../src/types";
let baseline: Project;
test.beforeAll(async ({ request }) => {
  baseline = (await (await request.get("/api/bootstrap")).json()).project;
});
test.beforeEach(async ({ page, request }) => {
  const b = await (await request.get("/api/bootstrap")).json();
  const headers = {
    "X-VirtualWago-Client": "workbench",
    "X-VirtualWago-Instance": b.state.instance,
  };
  await request.post("/api/command", {
    headers,
    data: { generation: b.state.generation, command: { action: "stop" } },
  });
  expect(
    (
      await request.put("/api/project", {
        headers,
        data: { generation: b.state.generation, project: baseline },
      })
    ).ok(),
  ).toBeTruthy();
  await page.goto("/");
  await expect(page.getByText("Kern verbunden", { exact: true })).toBeVisible();
});
test("theme follows system, persists overrides, and fits mobile", async ({
  page,
}) => {
  await page.emulateMedia({ colorScheme: "dark" });
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page
    .getByRole("combobox", { name: "Farbschema" })
    .selectOption("light");
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await page.getByRole("combobox", { name: "Farbschema" }).selectOption("dark");
  await page.getByRole("tab", { name: /Reaktionsskripte/ }).click();
  await expect(page.locator(".cm-editor")).toHaveCSS(
    "background-color",
    "rgb(40, 44, 52)",
  );
  await page.setViewportSize({ width: 390, height: 844 });
  await expect
    .poll(() =>
      page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
    )
    .toBeTruthy();
  await page.screenshot({
    path: "test-results/workbench-dark-mobile.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 1560, height: 1080 });
  await page.getByRole("tab", { name: "Live-I/O" }).click();
  await page.screenshot({
    path: "test-results/workbench-dark-desktop.png",
    fullPage: true,
  });
});
test("silent open WebSocket marks stale data and recovers", async ({
  page,
}) => {
  let connections = 0;
  let forward = false;
  await page.routeWebSocket("**/api/stream", (ws) => {
    connections++;
    const server = ws.connectToServer();
    server.onMessage((message) => {
      if (forward) ws.send(message);
    });
  });
  await page.reload();
  await expect(
    page.getByText("Live-Daten veraltet", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Start", exact: true }),
  ).toBeDisabled();
  forward = true;
  await expect(page.getByText("Kern verbunden", { exact: true })).toBeVisible();
  forward = false;
  await expect(
    page.getByText("Live-Daten veraltet", { exact: true }),
  ).toBeVisible({ timeout: 4000 });
  await expect(
    page.getByRole("button", { name: "Start", exact: true }),
  ).toBeDisabled();
  await expect.poll(() => connections, { timeout: 8000 }).toBeGreaterThan(1);
  forward = true;
  await expect(page.getByText("Kern verbunden", { exact: true })).toBeVisible();
});
test("project import reconciles module, script and watched signal", async ({
  page,
}) => {
  const p = structuredClone(baseline);
  for (const m of p.modules) m.id = "new-" + m.id;
  for (const r of p.reactions) {
    r.id = "new-" + r.id;
    if (r.source) r.source.module = "new-" + r.source.module;
    r.target.module = "new-" + r.target.module;
  }
  await page.getByLabel("Projektdatei importieren").setInputFiles({
    name: "new.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(p)),
  });
  await page.getByRole("button", { name: "Übernehmen", exact: true }).click();
  await expect(page.getByText("Gespeichert", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("combobox", { name: "Signal für Verlauf" }),
  ).toHaveValue("new-di-bank/ch1");
  await page
    .getByRole("button", { name: "Einzelschritt", exact: true })
    .click();
  await expect
    .poll(() =>
      page
        .locator('.trend-svg polyline[data-signal="new-di-bank/ch1"]')
        .getAttribute("points"),
    )
    .not.toBe("");
  await expect(page.locator(".signal-table tbody tr")).toHaveCount(8);
  await page.getByRole("tab", { name: /Reaktionsskripte/ }).click();
  await expect(page.getByRole("textbox", { name: "Skriptname" })).toHaveValue(
    "Ventilrückmeldung",
  );
});
test("editor locates syntax errors and stateful multi-source model runs", async ({
  page,
}) => {
  await page.getByRole("tab", { name: /Reaktionsskripte/ }).click();
  await page
    .getByRole("textbox", { name: "Reaktionscode" })
    .fill("fn react(o,p,dt,t) {\nlet x = ;\n}");
  await page.getByRole("button", { name: "Syntax prüfen" }).click();
  await expect(page.locator(".validation-error")).toContainText("Zeile 2");
  await page
    .getByRole("checkbox", { name: "Zustandsbehaftetes Modell" })
    .check();
  await page
    .locator(".source-picker label")
    .filter({ hasText: "do-bank/ch2" })
    .getByRole("checkbox")
    .check();
  await page
    .getByRole("textbox", { name: "Reaktionscode" })
    .fill(
      'fn react_state(o,p,s,dt,t) { if !s.contains("n") { s.n=0; } s.n+=1; #{value: if o["do-bank/ch1"]+o["do-bank/ch2"]>1.5 && s.n>=2 {1.0} else {0.0},state:s} }',
    );
  await page.getByRole("button", { name: "Syntax prüfen" }).click();
  await expect(page.getByText(/Syntax gültig/)).toBeVisible();
  await page.getByRole("button", { name: "Übernehmen", exact: true }).click();
  await page.getByRole("tab", { name: "Live-I/O" }).click();
  for (const n of [1, 2])
    await page
      .getByRole("button", {
        name: `Kanal ${n} Testvorgabe einschalten`,
        exact: true,
      })
      .click();
  await page.getByRole("switch", { name: "Modellfreigabe" }).click();
  for (let i = 0; i < 2; i++)
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
test("scenario editor checks a draft in isolation and exports results", async ({
  page,
  request,
}) => {
  await page.getByRole("tab", { name: "Szenarien" }).click();
  await page
    .getByRole("button", { name: "Szenario hinzufügen", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Szenario prüfen", exact: true })
    .click();
  await expect(page.locator(".scenario-result")).toContainText("PASS");
  const live = (await (await request.get("/api/bootstrap")).json()).state;
  expect(live.time_ms).toBe(0);
  expect(live.permit).toBe(false);
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Bericht exportieren" }).click();
  expect((await download).suggestedFilename()).toBe(
    "virtualwago-scenario-report.json",
  );
  await page.getByRole("spinbutton", { name: "Frist (ms)" }).fill("0");
  await expect(page.locator(".scenario-result")).toHaveCount(0);
  await page
    .getByRole("button", { name: "Szenario prüfen", exact: true })
    .click();
  await expect(page.locator(".scenario-result")).toContainText("FAIL");
});
test("multiple signals record, export and replay without issuing commands", async ({
  page,
}) => {
  await page.locator(".trace-panel summary").click();
  await page
    .locator(".trace-panel .source-picker label")
    .filter({ hasText: "Digitale Testausgänge · ch1" })
    .getByRole("checkbox")
    .check();
  await expect(page.locator(".trend-svg polyline")).toHaveCount(2);
  await page.getByRole("button", { name: "Aufzeichnen", exact: true }).click();
  await page.getByRole("tab", { name: /Reaktionsskripte/ }).click();
  await page.getByRole("tab", { name: "Live-I/O" }).click();
  await expect(
    page.getByRole("button", { name: "Aufnahme stoppen" }),
  ).toBeVisible();
  for (let i = 0; i < 3; i++)
    await page
      .getByRole("button", { name: "Einzelschritt", exact: true })
      .click();
  await page.getByRole("button", { name: "Aufnahme stoppen" }).click();
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "JSON exportieren" }).click();
  const stream = await (await download).createReadStream();
  const chunks = [];
  for await (const chunk of stream!) chunks.push(chunk);
  const recording = JSON.parse(Buffer.concat(chunks).toString());
  expect(recording.channels).toHaveLength(2);
  expect(recording.samples.length).toBeGreaterThan(1);
  const csv = page.waitForEvent("download");
  await page.getByRole("button", { name: "CSV exportieren" }).click();
  expect((await csv).suggestedFilename()).toBe("virtualwago-recording.csv");
  let commands = 0;
  page.on("request", (r) => {
    if (r.url().endsWith("/api/command")) commands++;
  });
  await page.getByLabel("Aufzeichnung importieren").setInputFiles({
    name: "trace.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(recording)),
  });
  await expect(page.getByText("Aufzeichnung · Wiedergabe")).toBeVisible();
  await page
    .getByRole("slider", { name: "Wiedergabeposition" })
    .fill(String(recording.samples.length - 1));
  await page.getByRole("button", { name: "Wiedergabe starten" }).click();
  await expect(
    page.getByRole("slider", { name: "Wiedergabeposition" }),
  ).toHaveValue(String(recording.samples.length - 1));
  expect(commands).toBe(0);
  recording.samples[0].values[recording.channels[0].key] = null;
  await page.getByLabel("Aufzeichnung importieren").setInputFiles({
    name: "bad.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(recording)),
  });
  await expect(page.locator(".trace-panel .validation-error")).toContainText(
    "Ungültiger Signalwert",
  );
});
