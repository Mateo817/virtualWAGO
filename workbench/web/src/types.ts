export type SignalRef = { module: string; channel: string };
export type Channel = {
  id: string;
  label: string;
  direction: "input" | "output";
  kind: "digital" | "analog";
  unit: string;
  min: number;
  max: number;
  initial: number;
  encoding: { codec: string; [key: string]: unknown };
};
export type ModulePackage = {
  schema: number;
  id: string;
  version: string;
  article: string;
  title: string;
  family: string;
  description: string;
  evidence: string;
  assumptions: string;
  channels: Channel[];
};
export type Instance = {
  id: string;
  package: string;
  package_sha256: string;
  label: string;
};
export type Reaction = {
  id: string;
  name: string;
  enabled: boolean;
  source: SignalRef | null;
  sources?: SignalRef[];
  stateful?: boolean;
  target: SignalRef;
  code: string;
};
export type Project = {
  schema: number;
  name: string;
  tick_ms: number;
  packages: ModulePackage[];
  modules: Instance[];
  reactions: Reaction[];
  scenarios?: Scenario[];
};
export type Signal = {
  signal: SignalRef;
  value: number;
  requested: number | null;
  effective: number | null;
  raw: number;
  requested_raw: number | null;
  source: string;
};
export type Snapshot = {
  instance: string;
  generation: number;
  sequence: string;
  tick: string;
  time_ms: number;
  running: boolean;
  permit: boolean;
  speed: number;
  fault: string | null;
  signals: Signal[];
  events: { time_ms: number; level: string; message: string }[];
  scope: string;
};
export type Bootstrap = { project: Project; state: Snapshot };
export const key = (s: SignalRef) => `${s.module}/${s.channel}`;
export const same = (a: SignalRef, b: SignalRef) => key(a) === key(b);
export const clone = <T>(value: T): T => structuredClone(value);

export type Expectation = {
  signal: SignalRef;
  min: number;
  max: number;
  within_ms: number;
};
export type ScenarioStep = {
  at_ms: number;
  permit: boolean | null;
  set: { signal: SignalRef; value: number }[];
  expect: Expectation[];
};
export type Scenario = { id: string; name: string; steps: ScenarioStep[] };
export type Sample = { time: number; values: Record<string, number> };
export type ScenarioReport = {
  id: string;
  passed: boolean;
  elapsed_ms: number;
  fault: string | null;
  samples: Sample[];
  assertions: {
    step: number;
    signal: SignalRef;
    min: number;
    max: number;
    deadline_ms: number;
    passed_at_ms: number | null;
    actual: number;
  }[];
};
export type Diagnostic = {
  message: string;
  line: number | null;
  column: number | null;
};
