import { Badge } from "@/components/ui/badge";
import { Anchor, Ship, Waves, Fish } from "lucide-react";
import type { SizeCohort } from "@/types/whale";
import { cn } from "@/lib/utils";

interface CohortBadgeProps {
  cohort: SizeCohort;
  className?: string;
}

const cohortConfig: Record<SizeCohort, { icon: typeof Anchor; color: string }> = {
  Kraken: { icon: Anchor, color: "text-purple-400 bg-purple-500/20 border-purple-500/30" },
  Whale: { icon: Ship, color: "text-blue-400 bg-blue-500/20 border-blue-500/30" },
  Shark: { icon: Waves, color: "text-cyan-400 bg-cyan-500/20 border-cyan-500/30" },
  Fish: { icon: Fish, color: "text-gray-400 bg-gray-500/20 border-gray-500/30" },
};

export function CohortBadge({ cohort, className }: CohortBadgeProps) {
  const config = cohortConfig[cohort];
  const Icon = config.icon;

  return (
    <Badge
      variant="outline"
      className={cn("gap-1 border", config.color, className)}
    >
      <Icon className="h-3 w-3" />
      <span>{cohort}</span>
    </Badge>
  );
}
