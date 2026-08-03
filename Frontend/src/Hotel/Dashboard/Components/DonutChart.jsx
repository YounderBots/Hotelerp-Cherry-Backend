import React, { useId, useState } from "react";
import { CATEGORICAL_PALETTE } from "./chartPalette";

const SEGMENT_GAP = 3; // px of arc length held back at the end of each segment
const MIN_VISUAL_PCT = 1.5; // smallest share a nonzero segment is allowed to render as, so it never disappears

const formatPct = (pct) => (pct > 0 && Math.round(pct) === 0 ? "<1%" : `${Math.round(pct)}%`);

const DonutChart = ({
  title,
  data = [],
  loading = false,
  error = null,
  emptyMessage = "No data available.",
  valueFormatter = (v) => String(v),
  centerValue,
  centerCaption,
  sampleTag,
}) => {
  const radius = 80;
  const strokeWidth = 26;
  const circumference = 2 * Math.PI * radius;
  const shadowId = useId();
  const [hoverIndex, setHoverIndex] = useState(null);

  const total = data.reduce((sum, d) => sum + (Number(d.value) || 0), 0);
  const withPct = data
    .filter((d) => (Number(d.value) || 0) > 0)
    .map((d, index) => ({
      ...d,
      color: d.color || CATEGORICAL_PALETTE[index % CATEGORICAL_PALETTE.length],
      pct: total > 0 ? ((Number(d.value) || 0) / total) * 100 : 0,
    }));
  const zeroLabels = data.filter((d) => !(Number(d.value) > 0)).map((d) => d.label).filter(Boolean);

  // A real but tiny share (e.g. <1%) renders as an invisible sliver otherwise.
  // The arc gets a visual floor; every displayed number keeps the true pct.
  const boosted = withPct.map((seg) =>
    seg.pct > 0 && seg.pct < MIN_VISUAL_PCT ? { ...seg, renderPct: MIN_VISUAL_PCT } : { ...seg, renderPct: seg.pct },
  );
  const visualDeficit = boosted.reduce((sum, seg, index) => sum + (seg.renderPct - withPct[index].pct), 0);
  const withRenderPct = boosted;
  if (visualDeficit > 0 && withRenderPct.length > 0) {
    const largestIndex = withRenderPct.reduce(
      (bestIndex, seg, index) => (seg.pct > withRenderPct[bestIndex].pct ? index : bestIndex),
      0,
    );
    withRenderPct[largestIndex] = {
      ...withRenderPct[largestIndex],
      renderPct: Math.max(0, withRenderPct[largestIndex].renderPct - visualDeficit),
    };
  }

  const segments = withRenderPct.reduce((acc, seg) => {
    const priorOffset = acc.length > 0 ? acc[acc.length - 1].cumulative : 0;
    const trueDash = (seg.renderPct / 100) * circumference;
    const gap = withRenderPct.length > 1 ? SEGMENT_GAP : 0;
    return [
      ...acc,
      { ...seg, dash: Math.max(0, trueDash - gap), dashOffset: -priorOffset, cumulative: priorOffset + trueDash },
    ];
  }, []);

  const lead = segments[0];
  const active = hoverIndex != null ? segments[hoverIndex] : null;
  const centerMain = active ? valueFormatter(active.value) : centerValue ?? formatPct(lead?.pct ?? 0);
  const centerSub = active
    ? `${active.label} · ${formatPct(active.pct)}`
    : centerCaption ?? lead?.label ?? "";

  const clearHover = () => setHoverIndex(null);

  return (
    <div className="card donut-chart-card">
      <div className="card-header-inline">
        {title && <h4>{title}</h4>}
        {sampleTag && (
          <span className="sample-tag" title={sampleTag}>
            Sample
          </span>
        )}
      </div>

      {loading && (
        <div className="dashboard-empty" role="status" aria-live="polite">
          Loading…
        </div>
      )}

      {!loading && error && (
        <div className="dashboard-alert inline" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && total === 0 && (
        <div className="dashboard-empty">{emptyMessage}</div>
      )}

      {!loading && !error && total > 0 && (
        <>
        <div className="platform-content">
          <svg
            width="240"
            height="240"
            viewBox="0 0 200 200"
            role="img"
            aria-label={`${title || "Breakdown"} donut chart`}
          >
            <defs>
              <filter id={shadowId} x="-30%" y="-30%" width="160%" height="160%">
                <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#000" floodOpacity="0.14" />
              </filter>
            </defs>
            <g transform="translate(100,100)" filter={`url(#${shadowId})`}>
              <circle r={radius} cx="0" cy="0" fill="transparent" stroke="var(--gray-100)" strokeWidth={strokeWidth} />
              {segments.map((seg, index) => (
                <circle
                  key={seg.label ?? index}
                  className="donut-segment"
                  r={radius}
                  cx="0"
                  cy="0"
                  fill="transparent"
                  stroke={seg.color}
                  strokeWidth={hoverIndex === index ? strokeWidth + 6 : strokeWidth}
                  strokeLinecap="round"
                  strokeDasharray={`${seg.dash} ${circumference}`}
                  strokeDashoffset={seg.dashOffset}
                  opacity={hoverIndex === null || hoverIndex === index ? 1 : 0.4}
                  transform="rotate(-90)"
                  tabIndex={0}
                  role="img"
                  aria-label={`${seg.label}: ${valueFormatter(seg.value)}, ${formatPct(seg.pct)}`}
                  onMouseEnter={() => setHoverIndex(index)}
                  onMouseLeave={clearHover}
                  onFocus={() => setHoverIndex(index)}
                  onBlur={clearHover}
                />
              ))}
              <text textAnchor="middle" dy="-0.1em" fontSize="26" fontWeight="900" fill="var(--secondary-dark)">
                {centerMain}
              </text>
              <text textAnchor="middle" dy="1.6em" fontSize="13" fontWeight="600" fill="var(--gray-500)">
                {centerSub}
              </text>
            </g>
          </svg>

          <ul className="platform-legend" role="list">
            {segments.map((seg, index) => (
              <li
                key={seg.label ?? index}
                className={`platform-bar${hoverIndex === index ? " is-active" : ""}`}
                style={{ "--legend-accent": seg.color }}
                tabIndex={0}
                role="button"
                aria-label={`${seg.label}: ${valueFormatter(seg.value)}, ${formatPct(seg.pct)}`}
                onMouseEnter={() => setHoverIndex(index)}
                onMouseLeave={clearHover}
                onFocus={() => setHoverIndex(index)}
                onBlur={clearHover}
              >
                <div className="bar-label">
                  <span className="legend-key">
                    <i className="legend-dot" style={{ background: seg.color }} aria-hidden="true" />
                    {seg.label}
                  </span>
                  <span className="legend-value">
                    <b>{valueFormatter(seg.value)}</b>
                    <em>{formatPct(seg.pct)}</em>
                  </span>
                </div>
                <div className="bar-track" aria-hidden="true">
                  <div className="bar-fill" style={{ width: `${Math.max(seg.pct, seg.pct > 0 ? 2 : 0)}%`, background: seg.color }} />
                </div>
              </li>
            ))}
          </ul>
        </div>
        {zeroLabels.length > 0 && (
          <p className="donut-empty-note">No data recorded yet for: {zeroLabels.join(", ")}</p>
        )}
        </>
      )}
    </div>
  );
};

export default DonutChart;
