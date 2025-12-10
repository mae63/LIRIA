export default function LiriaLogo({ size = 46, showWordmark = false }) {
  const primary = "#b47a45";
  const secondary = "#d5a06c";

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: showWordmark ? "8px" : 0,
      }}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 120 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{
          filter: "drop-shadow(0 10px 25px rgba(0,0,0,0.45))",
        }}
      >
        <defs>
          <linearGradient id="liriaGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={secondary} />
            <stop offset="100%" stopColor={primary} />
          </linearGradient>
        </defs>
        <rect
          x="0"
          y="0"
          width="120"
          height="120"
          rx="24"
          fill="rgba(15,23,42,0.35)"
          stroke="rgba(244,114,182,0.08)"
        />
        <path
          d="M30 37L60 48L90 37V83L60 93L30 83V37Z"
          stroke="url(#liriaGradient)"
          strokeWidth="5"
          strokeLinejoin="round"
        />
        <path
          d="M60 48V94"
          stroke="url(#liriaGradient)"
          strokeWidth="5"
          strokeLinecap="round"
        />
      </svg>
      {showWordmark && (
        <div style={{ display: "flex", flexDirection: "column", lineHeight: 1 }}>
          <span
            style={{
              fontSize: "16px",
              letterSpacing: "0.2em",
              color: primary,
              fontWeight: 600,
            }}
          >
            LIRIA
          </span>
          <span style={{ fontSize: "10px", color: "#e5e7eb", letterSpacing: "0.22em" }}>
            READ . CURATE
          </span>
        </div>
      )}
    </div>
  );
}








