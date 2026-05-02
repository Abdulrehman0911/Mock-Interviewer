import { Star } from "lucide-react";

const ITEMS = [
  "Eye contact tracking",
  "Filler word detection",
  "Confidence scoring",
  "Pace analysis",
  "Tone insights",
  "Micro-expression read",
  "Personalized tips",
  "Real-time alerts",
];

export function Marquee() {
  return (
    <div
      className="relative overflow-hidden border-y border-foreground/10 py-6"
      style={{
        maskImage: "linear-gradient(90deg, transparent, black 12%, black 88%, transparent)",
        WebkitMaskImage: "linear-gradient(90deg, transparent, black 12%, black 88%, transparent)",
      }}
    >
      <div className="flex w-max animate-marquee gap-12 whitespace-nowrap">
        {[...ITEMS, ...ITEMS].map((item, i) => (
          <div
            key={i}
            className="flex items-center gap-3 text-sm font-medium tracking-wide text-muted-foreground"
          >
            <Star className="h-4 w-4 text-primary" />
            <span className="uppercase">{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
