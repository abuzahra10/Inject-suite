import React from "react";

export type Segment = {
  segment_id: string;
  content: string;
  page?: number | null;
};

export type SegmentedDocument = {
  doc_id: string;
  segments: Segment[];
  page_count?: number | null;
};

export type LocalizationFinding = {
  segment_id: string;
  content_preview: string;
  score: number;
};

export type LocalizationResult = {
  doc_id: string;
  findings: LocalizationFinding[];
  total_segments: number;
};

type Props = {
  document: SegmentedDocument;
  localization?: LocalizationResult;
  title?: string;
};

export function LocalizationViewer({ document, localization, title }: Props) {
  const flagged = new Set(localization?.findings.map((finding) => finding.segment_id));

  return (
    <div className="localization-viewer">
      <h4>{title ?? "Prompt Localization"}</h4>
      {localization ? (
        <p className="hint">
          Highlighted segments indicate suspected injected instructions (total flagged:{" "}
          {localization.findings.length} / {localization.total_segments}).
        </p>
      ) : (
        <p className="hint">
          Document segmented into {document.segments.length} chunks for inspection.
        </p>
      )}

      <div className="segment-grid">
        {document.segments.map((segment) => (
          <article
            key={segment.segment_id}
            className={
              flagged.has(segment.segment_id) ? "segment-item flagged" : "segment-item"
            }
          >
            <header>
              <span className="segment-id">{segment.segment_id}</span>
              {flagged.has(segment.segment_id) && (
                <span className="badge danger">Flagged</span>
              )}
            </header>
            <p>{segment.content}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
