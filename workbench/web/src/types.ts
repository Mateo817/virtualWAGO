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
