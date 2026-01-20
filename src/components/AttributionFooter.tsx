import { ExternalLink } from "lucide-react";

export function AttributionFooter() {
  return (
    <footer className="mt-8 py-4 border-t border-border">
      <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
        <span>Data provided by</span>
        <a
          href="https://nansen.ai"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-primary hover:underline font-medium"
        >
          Nansen
          <ExternalLink className="h-3 w-3" />
        </a>
      </div>
    </footer>
  );
}
