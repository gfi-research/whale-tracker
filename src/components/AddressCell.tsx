"use client";

import { useState } from "react";
import { Copy, ExternalLink, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { truncateAddress, getHyperliquidUrl } from "@/lib/format";
import { cn } from "@/lib/utils";

interface AddressCellProps {
  address: string;
  label?: string;
  className?: string;
}

export function AddressCell({ address, label, className }: AddressCellProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await navigator.clipboard.writeText(address);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExternalLink = (e: React.MouseEvent) => {
    e.stopPropagation();
    window.open(getHyperliquidUrl(address), "_blank");
  };

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div className="flex flex-col">
        {label && (
          <span className="text-sm font-medium text-foreground truncate max-w-[180px]">
            {label}
          </span>
        )}
        <span className="text-xs text-muted-foreground font-mono">
          {truncateAddress(address)}
        </span>
      </div>
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          onClick={handleCopy}
          title="Copy address"
        >
          {copied ? (
            <Check className="h-3 w-3 text-green-500" />
          ) : (
            <Copy className="h-3 w-3" />
          )}
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          onClick={handleExternalLink}
          title="View on Hyperliquid"
        >
          <ExternalLink className="h-3 w-3" />
        </Button>
      </div>
    </div>
  );
}
