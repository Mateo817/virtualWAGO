import { useEffect, useRef } from "react";
import { basicSetup } from "codemirror";
import { Compartment, EditorState } from "@codemirror/state";
import { EditorView } from "@codemirror/view";
import { StreamLanguage } from "@codemirror/language";
import { setDiagnostics } from "@codemirror/lint";
import { oneDark } from "@codemirror/theme-one-dark";
import type { Diagnostic } from "./types";
// Rhai's lexical subset, not a Rust parser. The Rust service is the syntax authority.
const rhai = StreamLanguage.define({
  startState: () => ({ comment: false }),
  token(stream, state) {
    if (state.comment) {
      if (stream.skipTo("*/")) {
        stream.match("*/");
        state.comment = false;
      } else stream.skipToEnd();
      return "comment";
    }
    if (stream.eatSpace()) return null;
    if (stream.match("//")) {
      stream.skipToEnd();
      return "comment";
    }
    if (stream.match("/*")) {
      state.comment = true;
      return "comment";
    }
    if (stream.match(/"(?:[^"\\]|\\.)*"/)) return "string";
    if (
      stream.match(
        /\b(?:fn|let|const|if|else|while|loop|for|in|return|throw|try|catch|switch|break|continue|true|false)\b/,
      )
    )
      return "keyword";
    if (stream.match(/\b\d+(?:\.\d+)?\b/)) return "number";
    stream.next();
    return null;
  },
});
export function ScriptEditor({
  code,
  disabled,
  diagnostic,
  onChange,
}: {
  code: string;
  disabled: boolean;
  diagnostic?: Diagnostic | null;
  onChange: (code: string) => void;
}) {
  const host = useRef<HTMLDivElement>(null);
  const view = useRef<EditorView>(undefined);
  const callback = useRef(onChange);
  callback.current = onChange;
  const externalChange = useRef(false);
  const editable = useRef(new Compartment());
  const theme = useRef(new Compartment());
  useEffect(() => {
    const v = new EditorView({
      parent: host.current!,
      state: EditorState.create({
        doc: code,
        extensions: [
          basicSetup,
          rhai,
          editable.current.of(EditorState.readOnly.of(disabled)),
          theme.current.of(
            document.documentElement.dataset.theme === "dark" ? oneDark : [],
          ),
          EditorView.contentAttributes.of({ "aria-label": "Reaktionscode" }),
          EditorView.updateListener.of((u) => {
            if (u.docChanged && !externalChange.current)
              callback.current(u.state.doc.toString());
          }),
        ],
      }),
    });
    view.current = v;
    const observer = new MutationObserver(() =>
      v.dispatch({
        effects: theme.current.reconfigure(
          document.documentElement.dataset.theme === "dark" ? oneDark : [],
        ),
      }),
    );
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });
    return () => {
      observer.disconnect();
      v.destroy();
    };
  }, []);
  useEffect(() => {
    const v = view.current!;
    if (v.state.doc.toString() !== code) {
      externalChange.current = true;
      v.dispatch({
        changes: { from: 0, to: v.state.doc.length, insert: code },
      });
      externalChange.current = false;
    }
  }, [code]);
  useEffect(() => {
    view.current!.dispatch({
      effects: editable.current.reconfigure(EditorState.readOnly.of(disabled)),
    });
  }, [disabled]);
  useEffect(() => {
    const v = view.current!;
    const row = diagnostic?.line
      ? v.state.doc.line(Math.min(diagnostic.line, v.state.doc.lines))
      : null;
    v.dispatch(
      setDiagnostics(
        v.state,
        row
          ? [
              {
                from: row.from,
                to: row.to,
                severity: "error",
                message: diagnostic!.message,
              },
            ]
          : [],
      ),
    );
  }, [diagnostic]);
  return <div ref={host} className="code-editor" />;
}
